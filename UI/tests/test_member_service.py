"""Unit tests for MemberService using Mock Repositories (AAA Pattern).

Tests business rules in complete isolation from the physical database.
"""

from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest
from constants import PaymentMethod, RoleID, SubscriptionStatus
from exceptions import (
    DuplicateUserException,
    PackageNotFoundException,
    ValidationException,
)
from models.package_plan import PackagePlan
from models.user import User
from services.member_service import MemberService


@pytest.fixture
def mock_dependencies():
    """Create mock repositories and db connection for MemberService."""
    user_repo = MagicMock()
    plan_repo = MagicMock()
    sub_repo = MagicMock()
    invoice_repo = MagicMock()
    noti_repo = MagicMock()

    mock_db = MagicMock()
    mock_cursor = MagicMock()

    @contextmanager
    def mock_transaction():
        yield mock_cursor

    mock_db.transaction = mock_transaction

    service = MemberService(
        user_repo=user_repo,
        plan_repo=plan_repo,
        sub_repo=sub_repo,
        invoice_repo=invoice_repo,
        noti_repo=noti_repo,
    )
    service.db = mock_db

    sample_plan = PackagePlan(
        plan_id="PLAN_TEST",
        name="Gói 10 Buổi Test",
        duration_days=30,
        price=500000.0,
        max_check_in_sessions=10,
        is_pt_included=0,
        is_active=1,
    )
    plan_repo.get_by_id.return_value = sample_plan
    user_repo.find_by_phone.return_value = None

    return {
        "service": service,
        "user_repo": user_repo,
        "plan_repo": plan_repo,
        "sub_repo": sub_repo,
        "invoice_repo": invoice_repo,
        "noti_repo": noti_repo,
        "plan": sample_plan,
        "cursor": mock_cursor,
    }


def test_register_member_success(mock_dependencies):
    # Arrange
    service = mock_dependencies["service"]
    user_repo = mock_dependencies["user_repo"]
    sub_repo = mock_dependencies["sub_repo"]
    invoice_repo = mock_dependencies["invoice_repo"]
    noti_repo = mock_dependencies["noti_repo"]

    # Act
    result = service.register_member_with_package(
        full_name="Nguyễn Văn A",
        phone="0912345678",
        plan_id="PLAN_TEST",
        payment_method=PaymentMethod.VIETQR.value,
        email="vana@gmail.com",
    )

    # Assert
    assert result["success"] is True
    assert result["user"].full_name == "Nguyễn Văn A"
    assert result["user"].phone == "0912345678"
    assert result["subscription"].remaining_check_in_sessions == 10
    assert result["subscription"].status == SubscriptionStatus.ACTIVE.value
    assert result["qr_code"].startswith("GYM-QR-")
    assert result["invoice"].invoice_code.startswith("HD-")

    # Verify transaction calls across 4 repositories
    user_repo.create_with_cursor.assert_called_once()
    sub_repo.create_with_cursor.assert_called_once()
    invoice_repo.create_with_cursor.assert_called_once()
    noti_repo.create_with_cursor.assert_called_once()


def test_register_member_empty_name_fails(mock_dependencies):
    # Arrange
    service = mock_dependencies["service"]

    # Act & Assert
    with pytest.raises(ValidationException) as exc_info:
        service.register_member_with_package(
            full_name="   ",
            phone="0912345678",
            plan_id="PLAN_TEST",
        )
    assert "Họ và tên" in str(exc_info.value)
    assert exc_info.value.field_name == "full_name"


def test_register_member_invalid_phone_fails(mock_dependencies):
    # Arrange
    service = mock_dependencies["service"]

    # Act & Assert
    with pytest.raises(ValidationException) as exc_info:
        service.register_member_with_package(
            full_name="Nguyễn Văn A",
            phone="0912345",  # Under 10 digits
            plan_id="PLAN_TEST",
        )
    assert "Số điện thoại" in str(exc_info.value)
    assert exc_info.value.field_name == "phone"


def test_register_member_invalid_email_fails(mock_dependencies):
    # Arrange
    service = mock_dependencies["service"]

    # Act & Assert
    with pytest.raises(ValidationException) as exc_info:
        service.register_member_with_package(
            full_name="Nguyễn Văn A",
            phone="0912345678",
            plan_id="PLAN_TEST",
            email="invalid-email-format",
        )
    assert "email" in str(exc_info.value).lower()
    assert exc_info.value.field_name == "email"


def test_register_member_pos_swipe_disallowed(mock_dependencies):
    # Arrange
    service = mock_dependencies["service"]

    # Act & Assert (Zero POS card swipe rule)
    with pytest.raises(ValidationException) as exc_info:
        service.register_member_with_package(
            full_name="Nguyễn Văn A",
            phone="0912345678",
            plan_id="PLAN_TEST",
            payment_method="POS_CARD",
        )
    assert "CASH hoặc VIETQR" in str(exc_info.value)


def test_register_member_duplicate_phone_fails(mock_dependencies):
    # Arrange
    service = mock_dependencies["service"]
    user_repo = mock_dependencies["user_repo"]
    user_repo.find_by_phone.return_value = User(
        username="HV123456",
        password_hash="hash",
        full_name="Trùng Tên",
        role_id=RoleID.MEMBER.value,
        phone="0912345678",
    )

    # Act & Assert
    with pytest.raises(DuplicateUserException) as exc_info:
        service.register_member_with_package(
            full_name="Người Mới",
            phone="0912345678",
            plan_id="PLAN_TEST",
        )
    assert "Số điện thoại" in str(exc_info.value)


def test_register_member_package_not_found(mock_dependencies):
    # Arrange
    service = mock_dependencies["service"]
    plan_repo = mock_dependencies["plan_repo"]
    plan_repo.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(PackageNotFoundException):
        service.register_member_with_package(
            full_name="Nguyễn Văn A",
            phone="0912345678",
            plan_id="NON_EXISTENT_PLAN",
        )


def test_register_member_custom_invoice_code_preserved(mock_dependencies):
    # Arrange
    service = mock_dependencies["service"]
    custom_code = "HD-VIETQR-ORDER-123456"

    # Act
    result = service.register_member_with_package(
        full_name="Nguyễn Văn B",
        phone="0987654321",
        plan_id="PLAN_TEST",
        invoice_code=custom_code,
    )

    # Assert
    assert result["invoice"].invoice_code == custom_code
