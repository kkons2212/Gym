"""Integration and Unit Test Suite for Phase 4 (Services & External APIs)."""

import sys
import os
from datetime import date, timedelta
from uuid import uuid4

# Add UI to path
current_dir = os.path.dirname(os.path.abspath(__file__))
ui_dir = os.path.abspath(os.path.join(current_dir, ".."))
if ui_dir not in sys.path:
    sys.path.insert(0, ui_dir)

import pytest
from constants import CheckInMethod, PaymentMethod, SubscriptionStatus, UserStatus
from exceptions import (
    CheckInDeniedException,
    DuplicateUserException,
    PackageNotFoundException,
    ValidationException,
)
from services.checkin_service import CheckInService
from services.member_service import MemberService
from services.vietqr_service import VietQrService
from database.db_connection import db


@pytest.fixture(scope="module")
def services():
    return {
        "vietqr": VietQrService(),
        "member": MemberService(),
        "checkin": CheckInService(),
    }


def test_vietqr_service_offline_fallback(services):
    vietqr = services["vietqr"]
    success, qr_data = vietqr.generate_qr_payment(amount=500000, order_code="HD-TEST-001")
    assert success is True
    assert qr_data.startswith("data:image/png;base64,")

    # Kiểm tra số tiền âm
    fail_ok, msg = vietqr.generate_qr_payment(amount=-1000, order_code="HD-ERR")
    assert fail_ok is False


def test_member_registration_full_flow(services):
    member_svc = services["member"]
    random_phone = f"09{uuid4().int % 100000000:08d}"

    # Đăng ký gói 1 tháng (PKG01) thanh toán VietQR
    result = member_svc.register_member_with_package(
        full_name="Nguyễn Văn Test Service",
        phone=random_phone,
        plan_id="PKG01",
        payment_method=PaymentMethod.VIETQR.value,
        email="test.svc@gym.vn",
    )

    assert result["success"] is True
    assert result["user"].phone == random_phone
    assert result["subscription"].plan_id == "PKG01"
    assert result["invoice"].payment_method == "VIETQR"
    assert result["notification"].username == result["user"].username
    assert result["qr_code"].startswith("GYM-QR-")

    # Kiểm tra dữ liệu thực tế tồn tại trong CSDL qua 4 bảng
    with db.cursor() as cur:
        cur.execute("SELECT FullName FROM `User` WHERE UserName = %s;", (result["user"].username,))
        row = cur.fetchone()
        assert row["FullName"] == "Nguyễn Văn Test Service"

        cur.execute(
            "SELECT Status FROM MemberSubscription WHERE SubscriptionId = %s;",
            (result["subscription"].subscription_id,),
        )
        sub_row = cur.fetchone()
        assert sub_row["Status"] == "ACTIVE"

        cur.execute(
            "SELECT TotalAmount FROM Invoice WHERE InvoiceId = %s;",
            (result["invoice"].invoice_id,),
        )
        inv_row = cur.fetchone()
        assert inv_row["TotalAmount"] > 0


def test_member_registration_validation_guardrails(services):
    member_svc = services["member"]

    # 1. Rỗng họ tên
    with pytest.raises(ValidationException):
        member_svc.register_member_with_package(
            full_name="",
            phone="0911223344",
            plan_id="PKG01",
        )

    # 2. Sai định dạng số điện thoại
    with pytest.raises(ValidationException):
        member_svc.register_member_with_package(
            full_name="Trần Lỗi",
            phone="12345",
            plan_id="PKG01",
        )

    # 3. Phương thức thanh toán không được hỗ trợ (Zero POS rule)
    with pytest.raises(ValidationException):
        member_svc.register_member_with_package(
            full_name="Trần Lỗi",
            phone="0911223344",
            plan_id="PKG01",
            payment_method="POS_CARD",
        )

    # 4. Gói tập không tồn tại
    with pytest.raises(PackageNotFoundException):
        member_svc.register_member_with_package(
            full_name="Trần Gói Sai",
            phone="0988776655",
            plan_id="PKG_NON_EXISTENT",
        )


def test_member_registration_duplicate_phone(services):
    member_svc = services["member"]
    dup_phone = f"09{uuid4().int % 100000000:08d}"

    # Lần 1: Thành công
    member_svc.register_member_with_package(
        full_name="Hội Viên 1",
        phone=dup_phone,
        plan_id="PKG01",
    )

    # Lần 2: Ném DuplicateUserException
    with pytest.raises(DuplicateUserException):
        member_svc.register_member_with_package(
            full_name="Hội Viên 2 Trùng SĐT",
            phone=dup_phone,
            plan_id="PKG01",
        )


def test_checkin_flow_qr_and_manual(services):
    member_svc = services["member"]
    checkin_svc = services["checkin"]

    # Tạo hội viên mới với gói tập kèm buổi
    phone = f"09{uuid4().int % 100000000:08d}"
    reg = member_svc.register_member_with_package(
        full_name="Học Viên Checkin",
        phone=phone,
        plan_id="PKG01",
    )
    qr_token = reg["qr_code"]
    username = reg["user"].username

    # 1. Điểm danh qua quét mã QR (UC03.1)
    res_qr = checkin_svc.process_checkin(key=qr_token, method=CheckInMethod.QR_SCAN.value)
    assert res_qr["success"] is True
    assert res_qr["username"] == username

    # 2. Điểm danh thủ công qua Số điện thoại (UC03.2)
    res_phone = checkin_svc.process_checkin(key=phone, method=CheckInMethod.MANUAL.value)
    assert res_phone["success"] is True
    assert res_phone["username"] == username

    # 3. Điểm danh thủ công qua Username (UC03.2)
    res_user = checkin_svc.process_checkin(key=username, method=CheckInMethod.MANUAL.value)
    assert res_user["success"] is True
    assert res_user["username"] == username


def test_checkin_denial_guardrails(services):
    checkin_svc = services["checkin"]
    member_svc = services["member"]

    # 1. Không tìm thấy thẻ
    with pytest.raises(CheckInDeniedException) as exc:
        checkin_svc.process_checkin(key="QR-KHONG-TON-TAI", method=CheckInMethod.QR_SCAN.value)
    assert "Không tìm thấy" in str(exc.value)

    # 2. Thẻ đã hết hạn
    phone = f"09{uuid4().int % 100000000:08d}"
    reg = member_svc.register_member_with_package(
        full_name="Hội Viên Hết Hạn",
        phone=phone,
        plan_id="PKG01",
    )
    qr_token = reg["qr_code"]

    # Cập nhật end_date về quá khứ trong CSDL
    past_date = date.today() - timedelta(days=10)
    with db.transaction() as cur:
        cur.execute(
            "UPDATE MemberSubscription SET EndDate = %s WHERE QrCode = %s;",
            (past_date, qr_token),
        )

    with pytest.raises(CheckInDeniedException) as exc_exp:
        checkin_svc.process_checkin(key=qr_token, method=CheckInMethod.QR_SCAN.value)
    assert "hết hạn" in str(exc_exp.value).lower()
