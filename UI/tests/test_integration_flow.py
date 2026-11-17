"""End-to-End Integration Test on Live Docker MySQL (Task 6.2 / TSK-22).

Validates complete member lifecycle:
1. Member registration with 4-table atomic transaction
2. Physical DB state verification across User, MemberSubscription, Invoice, Notification
3. QR-code check-in with session decrement (12 -> 11)
4. Manual phone check-in with session decrement (11 -> 10)
5. Physical CheckInLog audit verification
6. Clean teardown
"""

from datetime import date
from uuid import uuid4

import pytest
from constants import CheckInMethod, CheckInStatus, PaymentMethod, SubscriptionStatus
from database.db_connection import db
from services.checkin_service import CheckInService
from services.member_service import MemberService


@pytest.fixture
def live_services():
    """Initialize live services connected to the Docker MySQL container."""
    member_service = MemberService()
    checkin_service = CheckInService()
    return {
        "member_service": member_service,
        "checkin_service": checkin_service,
    }


def test_complete_member_lifecycle_e2e(live_services):
    # -------------------------------------------------------------------------
    # ARRANGE: Unique test data
    # -------------------------------------------------------------------------
    member_service: MemberService = live_services["member_service"]
    checkin_service: CheckInService = live_services["checkin_service"]

    unique_suffix = uuid4().hex[:6]
    test_phone = f"09{int(unique_suffix, 16) % 100000000:08d}"
    test_name = f"Hội Viên E2E {unique_suffix.upper()}"
    test_plan_id = "PKG04"  # Gói PT 12 buổi

    created_username = None
    created_sub_id = None

    try:
        # ---------------------------------------------------------------------
        # ACT 1: Đăng ký hội viên mới với gói 12 buổi
        # ---------------------------------------------------------------------
        reg_result = member_service.register_member_with_package(
            full_name=test_name,
            phone=test_phone,
            plan_id=test_plan_id,
            payment_method=PaymentMethod.CASH.value,
            email=f"e2e_{unique_suffix}@gymtest.vn",
            admin_id="admin",
        )

        assert reg_result["success"] is True
        created_username = reg_result["user"].username
        created_sub_id = reg_result["subscription"].subscription_id
        qr_token = reg_result["qr_code"]
        invoice_code = reg_result["invoice"].invoice_code

        # ---------------------------------------------------------------------
        # ASSERT 1: Kiểm tra dữ liệu trong 4 bảng CSDL
        # ---------------------------------------------------------------------
        with db.get_connection() as cnx:
            with cnx.cursor(dictionary=True) as cursor:
                # 1. Bảng User
                cursor.execute(
                    "SELECT FullName, Phone, RoleID, Status FROM `User` WHERE UserName = %s",
                    (created_username,),
                )
                user_row = cursor.fetchone()
                assert user_row is not None
                assert user_row["FullName"] == test_name
                assert user_row["Phone"] == test_phone
                assert user_row["RoleID"] == "MEMBER"
                assert user_row["Status"] == "ACTIVE"

                # 2. Bảng MemberSubscription
                cursor.execute(
                    "SELECT PlanId, RemainingCheckInSessions, Status, QrCode "
                    "FROM `MemberSubscription` WHERE SubscriptionId = %s",
                    (created_sub_id,),
                )
                sub_row = cursor.fetchone()
                assert sub_row is not None
                assert sub_row["PlanId"] == test_plan_id
                assert sub_row["RemainingCheckInSessions"] == 12
                assert sub_row["Status"] == SubscriptionStatus.ACTIVE.value
                assert sub_row["QrCode"] == qr_token

                # 3. Bảng Invoice
                cursor.execute(
                    "SELECT InvoiceCode, PaymentMethod, Status, TotalAmount "
                    "FROM `Invoice` WHERE UserName = %s",
                    (created_username,),
                )
                inv_row = cursor.fetchone()
                assert inv_row is not None
                assert inv_row["InvoiceCode"] == invoice_code
                assert inv_row["PaymentMethod"] == PaymentMethod.CASH.value
                assert inv_row["Status"] == "PAID"
                assert inv_row["TotalAmount"] == 3600000

                # 4. Bảng Notification
                cursor.execute(
                    "SELECT Title, Message FROM `Notification` WHERE UserName = %s",
                    (created_username,),
                )
                noti_row = cursor.fetchone()
                assert not noti_row is False and noti_row is not None
                assert "Chào mừng" in noti_row["Title"]

        # ---------------------------------------------------------------------
        # ACT 2: Điểm danh lần 1 qua mã QR (QR_SCAN)
        # ---------------------------------------------------------------------
        checkin_qr_res = checkin_service.process_checkin(
            key=qr_token,
            method=CheckInMethod.QR_SCAN.value,
            admin_id="admin",
        )

        assert checkin_qr_res["success"] is True
        assert checkin_qr_res["remaining_sessions"] == 11
        assert checkin_qr_res["username"] == created_username

        # ASSERT 2: Kiểm tra CSDL sau điểm danh QR
        with db.get_connection() as cnx:
            with cnx.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT RemainingCheckInSessions FROM `MemberSubscription` WHERE SubscriptionId = %s",
                    (created_sub_id,),
                )
                assert cursor.fetchone()["RemainingCheckInSessions"] == 11

                cursor.execute(
                    "SELECT Status, DenialReason FROM `CheckInLog` "
                    "WHERE UserName = %s ORDER BY check_in_at DESC LIMIT 1",
                    (created_username,),
                )
                log_1 = cursor.fetchone()
                assert log_1["Status"] == CheckInStatus.SUCCESS.value
                assert log_1["DenialReason"] is None

        # ---------------------------------------------------------------------
        # ACT 3: Điểm danh lần 2 qua nhập tay SĐT (MANUAL)
        # ---------------------------------------------------------------------
        checkin_manual_res = checkin_service.process_checkin(
            key=test_phone,
            method=CheckInMethod.MANUAL.value,
            admin_id="admin",
        )

        assert checkin_manual_res["success"] is True
        assert checkin_manual_res["remaining_sessions"] == 10
        assert checkin_manual_res["username"] == created_username

        # ASSERT 3: Kiểm tra CSDL sau điểm danh SĐT
        with db.get_connection() as cnx:
            with cnx.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT RemainingCheckInSessions FROM `MemberSubscription` WHERE SubscriptionId = %s",
                    (created_sub_id,),
                )
                assert cursor.fetchone()["RemainingCheckInSessions"] == 10

                cursor.execute(
                    "SELECT COUNT(*) as total_logs FROM `CheckInLog` WHERE UserName = %s",
                    (created_username,),
                )
                assert cursor.fetchone()["total_logs"] == 2

    finally:
        # ---------------------------------------------------------------------
        # TEARDOWN: Xóa dữ liệu test để đảm bảo CSDL luôn sạch
        # ---------------------------------------------------------------------
        if created_username:
            with db.get_connection() as cnx:
                with cnx.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM `CheckInLog` WHERE UserName = %s",
                        (created_username,),
                    )
                    cursor.execute(
                        "DELETE FROM `Invoice` WHERE UserName = %s",
                        (created_username,),
                    )
                    cursor.execute(
                        "DELETE FROM `Notification` WHERE UserName = %s",
                        (created_username,),
                    )
                    cursor.execute(
                        "DELETE FROM `MemberSubscription` WHERE UserName = %s",
                        (created_username,),
                    )
                    cursor.execute(
                        "DELETE FROM `User` WHERE UserName = %s",
                        (created_username,),
                    )
                cnx.commit()
