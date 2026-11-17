"""Unit tests for CheckInService using Mock Repositories (AAA Pattern).

Tests check-in access control rules in complete isolation from the physical database.
"""

from contextlib import contextmanager
from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from constants import (
    CheckInMethod,
    CheckInStatus,
    DenialReason,
    SubscriptionStatus,
    UserStatus,
)
from exceptions import CheckInDeniedException
from models.member_subscription import MemberSubscription
from models.package_plan import PackagePlan
from models.user import User
from services.checkin_service import CheckInService


@pytest.fixture
def mock_checkin_deps():
    """Create mock repositories and fixtures for CheckInService."""
    sub_repo = MagicMock()
    user_repo = MagicMock()
    check_in_repo = MagicMock()
    plan_repo = MagicMock()

    mock_db = MagicMock()
    mock_cursor = MagicMock()

    @contextmanager
    def mock_transaction(*args, **kwargs):
        yield mock_cursor

    mock_db.transaction = mock_transaction

    service = CheckInService(
        sub_repo=sub_repo,
        user_repo=user_repo,
        check_in_repo=check_in_repo,
        plan_repo=plan_repo,
    )
    service.db = mock_db

    sub_repo.decrement_sessions_with_cursor.return_value = True

    sample_user = User(
        username="HV123456",
        password_hash="hashed_pw",
        full_name="Nguyễn Văn Hội Viên",
        phone="0911223344",
        status=UserStatus.ACTIVE.value,
    )

    sample_sub = MemberSubscription(
        subscription_id="SUB001",
        username="HV123456",
        plan_id="PLAN_10S",
        start_date=date.today() - timedelta(days=5),
        end_date=date.today() + timedelta(days=25),
        remaining_check_in_sessions=10,
        status=SubscriptionStatus.ACTIVE.value,
        qr_code="GYM-QR-HV123456-TOKEN123",
    )

    sample_plan = PackagePlan(
        plan_id="PLAN_10S",
        name="Gói 10 Buổi",
        duration_days=30,
        price=500000.0,
        max_check_in_sessions=10,
        is_active=1,
    )

    plan_repo.get_by_id.return_value = sample_plan

    return {
        "service": service,
        "sub_repo": sub_repo,
        "user_repo": user_repo,
        "check_in_repo": check_in_repo,
        "plan_repo": plan_repo,
        "user": sample_user,
        "sub": sample_sub,
        "plan": sample_plan,
        "cursor": mock_cursor,
    }


def test_checkin_qr_success_and_decrement_session(mock_checkin_deps):
    # Arrange
    service = mock_checkin_deps["service"]
    sub_repo = mock_checkin_deps["sub_repo"]
    user_repo = mock_checkin_deps["user_repo"]
    check_in_repo = mock_checkin_deps["check_in_repo"]
    sub = mock_checkin_deps["sub"]
    user = mock_checkin_deps["user"]

    sub_repo.find_by_qrcode.return_value = sub
    user_repo.find_by_username.return_value = user

    # Act
    result = service.process_checkin(
        key="GYM-QR-HV123456-TOKEN123",
        method=CheckInMethod.QR_SCAN.value,
    )

    # Assert
    assert result["success"] is True
    assert result["full_name"] == user.full_name
    assert result["remaining_sessions"] == 9  # 10 - 1
    assert result["status"] == SubscriptionStatus.ACTIVE.value

    sub_repo.decrement_sessions_with_cursor.assert_called_once()
    check_in_repo.create_with_cursor.assert_called_once()
    created_log = check_in_repo.create_with_cursor.call_args[0][1]
    assert created_log.status == CheckInStatus.SUCCESS.value


def test_checkin_manual_flow_success(mock_checkin_deps):
    # Arrange
    service = mock_checkin_deps["service"]
    sub_repo = mock_checkin_deps["sub_repo"]
    user_repo = mock_checkin_deps["user_repo"]
    check_in_repo = mock_checkin_deps["check_in_repo"]
    sub = mock_checkin_deps["sub"]
    user = mock_checkin_deps["user"]

    user_repo.find_by_phone_or_username.return_value = user
    sub_repo.find_active_by_username.return_value = sub

    # Act
    result = service.process_checkin(
        key="0911223344",
        method=CheckInMethod.MANUAL.value,
    )

    # Assert
    assert result["success"] is True
    assert result["full_name"] == user.full_name
    assert result["remaining_sessions"] == 9

    sub_repo.decrement_sessions_with_cursor.assert_called_once()
    check_in_repo.create_with_cursor.assert_called_once()


def test_checkin_unlimited_plan_does_not_decrement(mock_checkin_deps):
    # Arrange
    service = mock_checkin_deps["service"]
    sub_repo = mock_checkin_deps["sub_repo"]
    user_repo = mock_checkin_deps["user_repo"]
    plan_repo = mock_checkin_deps["plan_repo"]
    sub = mock_checkin_deps["sub"]
    user = mock_checkin_deps["user"]

    sub.remaining_check_in_sessions = None  # None indicates unlimited

    unlimited_plan = PackagePlan(
        plan_id="PLAN_UNLIMITED",
        name="Gói 1 Tháng Không Giới Hạn",
        duration_days=30,
        price=1000000.0,
        max_check_in_sessions=None,
        is_active=1,
    )
    plan_repo.get_by_id.return_value = unlimited_plan
    sub_repo.find_by_qrcode.return_value = sub
    user_repo.find_by_username.return_value = user

    # Act
    result = service.process_checkin(key="GYM-QR-HV123456-TOKEN123")

    # Assert
    assert result["success"] is True
    sub_repo.decrement_sessions_with_cursor.assert_not_called()


def test_checkin_denied_when_key_empty(mock_checkin_deps):
    # Arrange
    service = mock_checkin_deps["service"]

    # Act & Assert
    with pytest.raises(CheckInDeniedException) as exc_info:
        service.process_checkin(key="   ")
    assert "không được để trống" in str(exc_info.value)


def test_checkin_denied_when_not_found(mock_checkin_deps):
    # Arrange
    service = mock_checkin_deps["service"]
    sub_repo = mock_checkin_deps["sub_repo"]
    sub_repo.find_by_qrcode.return_value = None

    # Act & Assert
    with pytest.raises(CheckInDeniedException) as exc_info:
        service.process_checkin(key="NON_EXISTENT_QR")
    assert "Không tìm thấy" in str(exc_info.value)


def test_checkin_denied_when_expired(mock_checkin_deps):
    # Arrange
    service = mock_checkin_deps["service"]
    sub_repo = mock_checkin_deps["sub_repo"]
    user_repo = mock_checkin_deps["user_repo"]
    check_in_repo = mock_checkin_deps["check_in_repo"]
    sub = mock_checkin_deps["sub"]
    user = mock_checkin_deps["user"]

    # Expired 2 days ago
    sub.end_date = date.today() - timedelta(days=2)
    sub_repo.find_by_qrcode.return_value = sub
    user_repo.find_by_username.return_value = user

    # Act & Assert
    with pytest.raises(CheckInDeniedException) as exc_info:
        service.process_checkin(key="GYM-QR-HV123456-TOKEN123")

    assert "hết hạn" in str(exc_info.value).lower()
    # Log must still be created as DENIED
    check_in_repo.create_with_cursor.assert_called_once()
    created_log = check_in_repo.create_with_cursor.call_args[0][1]
    assert created_log.status == CheckInStatus.DENIED.value
    assert created_log.denial_reason == DenialReason.EXPIRED.value


def test_checkin_denied_when_sessions_exhausted(mock_checkin_deps):
    # Arrange
    service = mock_checkin_deps["service"]
    sub_repo = mock_checkin_deps["sub_repo"]
    user_repo = mock_checkin_deps["user_repo"]
    check_in_repo = mock_checkin_deps["check_in_repo"]
    sub = mock_checkin_deps["sub"]
    user = mock_checkin_deps["user"]

    sub.remaining_check_in_sessions = 0
    sub_repo.find_by_qrcode.return_value = sub
    user_repo.find_by_username.return_value = user

    # Act & Assert
    with pytest.raises(CheckInDeniedException) as exc_info:
        service.process_checkin(key="GYM-QR-HV123456-TOKEN123")

    assert "hết" in str(exc_info.value).lower()
    check_in_repo.create_with_cursor.assert_called_once()
    created_log = check_in_repo.create_with_cursor.call_args[0][1]
    assert created_log.status == CheckInStatus.DENIED.value
    assert created_log.denial_reason == DenialReason.OUT_OF_SESSIONS.value


def test_checkin_denied_when_user_locked(mock_checkin_deps):
    # Arrange
    service = mock_checkin_deps["service"]
    sub_repo = mock_checkin_deps["sub_repo"]
    user_repo = mock_checkin_deps["user_repo"]
    check_in_repo = mock_checkin_deps["check_in_repo"]
    sub = mock_checkin_deps["sub"]
    user = mock_checkin_deps["user"]

    user.status = UserStatus.LOCKED.value
    sub_repo.find_by_qrcode.return_value = sub
    user_repo.find_by_username.return_value = user

    # Act & Assert
    with pytest.raises(CheckInDeniedException) as exc_info:
        service.process_checkin(key="GYM-QR-HV123456-TOKEN123")

    assert "khóa" in str(exc_info.value).lower()
    check_in_repo.create_with_cursor.assert_called_once()
    created_log = check_in_repo.create_with_cursor.call_args[0][1]
    assert created_log.status == CheckInStatus.DENIED.value
    assert created_log.denial_reason == DenialReason.USER_LOCKED.value
