"""Verification Test Suite for Phase 2 (Models & CSDL Connection Pool)."""

import sys
import os
from datetime import date, timedelta

# Add UI to path
current_dir = os.path.dirname(os.path.abspath(__file__))
ui_dir = os.path.abspath(os.path.join(current_dir, ".."))
if ui_dir not in sys.path:
    sys.path.insert(0, ui_dir)

from constants import RoleID, SubscriptionStatus, PaymentMethod, DenialReason
from exceptions import ValidationException, DatabaseTransactionException
from database.db_connection import db
from models.role import Role
from models.user import User
from models.package_plan import PackagePlan
from models.member_subscription import MemberSubscription
from models.invoice import Invoice
from models.check_in_log import CheckInLog
from models.notification import Notification

def test_db_pool_and_transaction():
    print("-> Test 1: Connection Pool & Transaction Manager")
    with db.transaction() as cur:
        cur.execute("SELECT COUNT(*) as cnt FROM Role;")
        res = cur.fetchone()
        cnt = res["cnt"] if isinstance(res, dict) else res[0]
        assert cnt >= 3, f"Expected at least 3 roles, got {cnt}"
    print("   ✓ Đọc dữ liệu từ connection pool thành công.")

    # Test Rollback
    print("-> Test 2: Transaction Automated Rollback on Error")
    try:
        with db.transaction() as cur:
            cur.execute("INSERT INTO Role (RoleID, RoleName) VALUES ('TEST_R', 'Test Role');")
            # Cố tình gây lỗi cú pháp để kích hoạt rollback
            cur.execute("INVALID SQL STATEMENT THAT FAILS;")
    except DatabaseTransactionException:
        pass

    with db.cursor() as cur:
        cur.execute("SELECT RoleID FROM Role WHERE RoleID = 'TEST_R';")
        assert cur.fetchone() is None, "Role 'TEST_R' không được lưu khi có lỗi (Rollback thành công)!"
    print("   ✓ Transaction tự động rollback an toàn khi gặp ngoại lệ.")

def test_models_serialization():
    print("-> Test 3: Model instantiation & from_row serialization")
    user_row = {
        "UserName": "HV9999",
        "RoleID": "MEMBER",
        "FullName": "Trần Văn Test",
        "Phone": "0988-123-456",
        "Status": "ACTIVE",
        "created_at": date.today()
    }
    user = User.from_row(user_row)
    assert user.username == "HV9999"
    assert user.role_id == "MEMBER"
    assert user.is_active() is True
    
    clean_p = user.validate_phone()
    assert clean_p == "0988123456"
    assert user.to_dict()["username"] == "HV9999"
    print("   ✓ User Entity và phone validation hoạt động chuẩn xác.")

def test_checkin_eligibility():
    print("-> Test 4: MemberSubscription.is_eligible_for_checkin guardrails")
    today = date.today()

    # Case 1: Thẻ hợp lệ
    sub_valid = MemberSubscription(
        subscription_id="SUB01",
        username="HV9999",
        plan_id="PKG01",
        start_date=today - timedelta(days=5),
        end_date=today + timedelta(days=25),
        remaining_check_in_sessions=10,
        status=SubscriptionStatus.ACTIVE.value
    )
    ok, msg = sub_valid.is_eligible_for_checkin(today)
    assert ok is True
    assert msg == "Hợp lệ"

    # Case 2: Thẻ hết hạn
    sub_expired = MemberSubscription(
        subscription_id="SUB02",
        username="HV9999",
        plan_id="PKG01",
        start_date=today - timedelta(days=35),
        end_date=today - timedelta(days=5),
        remaining_check_in_sessions=10,
        status=SubscriptionStatus.ACTIVE.value
    )
    ok, msg = sub_expired.is_eligible_for_checkin(today)
    assert ok is False
    assert msg == DenialReason.EXPIRED.value

    # Case 3: Thẻ hết số buổi tập
    sub_out = MemberSubscription(
        subscription_id="SUB03",
        username="HV9999",
        plan_id="PKG01",
        start_date=today - timedelta(days=5),
        end_date=today + timedelta(days=25),
        remaining_check_in_sessions=0,
        status=SubscriptionStatus.ACTIVE.value
    )
    ok, msg = sub_out.is_eligible_for_checkin(today)
    assert ok is False
    assert msg == DenialReason.OUT_OF_SESSIONS.value

    # Case 4: Thẻ đang bảo lưu (FROZEN)
    sub_frozen = MemberSubscription(
        subscription_id="SUB04",
        username="HV9999",
        plan_id="PKG01",
        start_date=today - timedelta(days=5),
        end_date=today + timedelta(days=25),
        remaining_check_in_sessions=10,
        status=SubscriptionStatus.FROZEN.value
    )
    ok, msg = sub_frozen.is_eligible_for_checkin(today)
    assert ok is False
    assert "bảo lưu" in msg
    print("   ✓ Logic kiểm tra điều kiện điểm danh đáp ứng 100% kịch bản UC03.")

def test_invoice_validation():
    print("-> Test 5: Invoice PaymentMethod guardrails (Zero POS rule)")
    # Hợp lệ với CASH và VIETQR
    inv1 = Invoice(invoice_id="INV01", username="HV9999", subscription_id="SUB01", payment_method=PaymentMethod.CASH.value)
    inv2 = Invoice(invoice_id="INV02", username="HV9999", subscription_id="SUB01", payment_method=PaymentMethod.VIETQR.value)
    assert inv1.payment_method == "CASH"
    assert inv2.payment_method == "VIETQR"

    # Không hợp lệ với POS quẹt thẻ
    try:
        Invoice(invoice_id="INV03", username="HV9999", subscription_id="SUB01", payment_method="POS_CARD")
        assert False, "Phải quăng ValidationException khi dùng phương thức POS_CARD!"
    except ValidationException:
        pass
    print("   ✓ Invoice tuân thủ tuyệt đối quy chuẩn chỉ chấp nhận CASH và VIETQR.")

if __name__ == "__main__":
    print("==================================================================")
    print(" BẮT ĐẦU KIỂM THỬ GIAI ĐOẠN 2: MODELS & CSDL CONNECTION POOL")
    print("==================================================================")
    test_db_pool_and_transaction()
    test_models_serialization()
    test_checkin_eligibility()
    test_invoice_validation()
    print("==================================================================")
    print(" TẤT CẢ 5 BÀI TEST GIAI ĐOẠN 2 ĐÃ VƯỢT QUA XUẤT SẮC (100% PASS)!")
    print("==================================================================")
