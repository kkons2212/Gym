"""Focused tests for repository query and row-mapping behavior."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime, timedelta
from typing import Any, Dict, Generator, List, Optional, Sequence
from uuid import uuid4

import mysql.connector
import pytest

from database.db_connection import db
from exceptions import DatabaseTransactionException
from models.check_in_log import CheckInLog
from models.invoice import Invoice
from models.member_subscription import MemberSubscription
from models.notification import Notification
from models.user import User
from repositories import (
    CheckInRepository,
    InvoiceRepository,
    NotificationRepository,
    PackagePlanRepository,
    SubscriptionRepository,
    UserRepository,
)


class FakeCursor:
    """Capture a statement and return configured rows."""

    def __init__(
        self,
        rows: Optional[List[Dict[str, Any]]] = None,
        rowcount: int = 1,
        error: Optional[Exception] = None,
    ) -> None:
        self.rows = rows or []
        self.rowcount = rowcount
        self.error = error
        self.query: Optional[str] = None
        self.params: Sequence[Any] = ()

    def execute(self, query: str, params: Sequence[Any] = ()) -> None:
        self.query = query
        self.params = params
        if self.error is not None:
            raise self.error

    def fetchall(self) -> List[Dict[str, Any]]:
        return self.rows

    def fetchone(self) -> Optional[Dict[str, Any]]:
        return self.rows[0] if self.rows else None


@contextmanager
def fake_cursor_context(
    cursor: FakeCursor,
) -> Generator[FakeCursor, None, None]:
    yield cursor


def patch_read_cursor(
    monkeypatch: pytest.MonkeyPatch, cursor: FakeCursor
) -> None:
    def cursor_factory(
        dictionary: bool = True,
    ) -> Generator[FakeCursor, None, None]:
        if not dictionary:
            raise AssertionError("Repository reads require dictionary rows.")
        return fake_cursor_context(cursor)

    monkeypatch.setattr(
        "repositories.base_repository.db.cursor",
        cursor_factory,
    )


def test_user_lookup_parameterizes_search_and_maps_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(
        rows=[
            {
                "UserName": "HV1001",
                "RoleID": "MEMBER",
                "FullName": "Test Member",
                "Phone": "0900000000",
                "Status": "ACTIVE",
            }
        ]
    )
    patch_read_cursor(monkeypatch, cursor)

    user = UserRepository().find_by_phone_or_username("' OR 1=1 --")

    assert isinstance(user, User)
    assert user.username == "HV1001"
    assert cursor.params == ("' OR 1=1 --", "' OR 1=1 --", "' OR 1=1 --")
    assert "%s" in cursor.query


def test_get_by_id_returns_none_for_missing_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor()
    patch_read_cursor(monkeypatch, cursor)

    assert PackagePlanRepository().get_by_id("MISSING") is None
    assert cursor.params == ("MISSING",)


def test_mysql_query_error_is_wrapped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(error=mysql.connector.Error("database unavailable"))
    patch_read_cursor(monkeypatch, cursor)

    with pytest.raises(DatabaseTransactionException) as error:
        UserRepository().find_by_username("member")

    assert isinstance(error.value.__cause__, mysql.connector.Error)


def test_invoice_repository_maps_physical_checkin_foreign_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(
        rows=[
            {
                "InvoiceId": "INV001",
                "UserName": "member",
                "SubscriptionId": "SUB001",
                "check_in_log_id": "CHK001",
            }
        ]
    )
    patch_read_cursor(monkeypatch, cursor)

    invoice = InvoiceRepository().get_by_id("INV001")

    assert invoice is not None
    assert invoice.check_in_log_id == "CHK001"
    assert "`CheckInLogCheckInId` AS `check_in_log_id`" in cursor.query


def test_decrement_sessions_uses_atomic_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(rowcount=0)

    @contextmanager
    def transaction_context(
        dictionary: bool = True,
    ) -> Generator[FakeCursor, None, None]:
        if dictionary:
            pytest.fail("Session decrement requires a transaction cursor.")
        yield cursor

    monkeypatch.setattr(db, "transaction", transaction_context)

    result = SubscriptionRepository().decrement_sessions("SUB001")

    assert result is False
    assert cursor.params == ("SUB001", "ACTIVE")
    assert "`RemainingCheckInSessions` > 0" in cursor.query


def test_today_checkin_query_uses_date_range_and_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor(rows=[{"check_in_id": "CHK001", "full_name": "Test"}])
    patch_read_cursor(monkeypatch, cursor)

    logs = CheckInRepository().get_today_logs(limit=5)

    assert logs[0]["full_name"] == "Test"
    assert cursor.params == (5,)
    assert "CURRENT_DATE + INTERVAL 1 DAY" in cursor.query


def test_checkin_create_uses_its_own_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cursor = FakeCursor()

    @contextmanager
    def transaction_context(
        dictionary: bool = True,
    ) -> Generator[FakeCursor, None, None]:
        if dictionary:
            pytest.fail("Check-in writes require a transaction cursor.")
        yield cursor

    monkeypatch.setattr(db, "transaction", transaction_context)

    CheckInRepository().create(
        CheckInLog(
            check_in_id="CHK001",
            username="member",
            subscription_id="SUB001",
        )
    )

    assert "`CheckInLog`" in cursor.query
    assert cursor.params[0] == "CHK001"


def test_recent_invoice_limit_must_be_positive() -> None:
    with pytest.raises(ValueError):
        InvoiceRepository().get_recent_invoices(limit=0)


def test_checkin_create_rejects_missing_required_subscription() -> None:
    with pytest.raises(ValueError, match="SubscriptionId là bắt buộc"):
        CheckInRepository().create_with_cursor(
            FakeCursor(),
            CheckInLog(check_in_id="CHK001", username="member"),
        )


def test_seeded_repository_reads_against_mysql() -> None:
    users = UserRepository()
    plans = PackagePlanRepository()
    subscriptions = SubscriptionRepository()
    invoices = InvoiceRepository()

    member = users.find_by_username("nam.nguyen")
    member_by_phone = users.find_by_phone("0987654321")
    member_by_key = users.find_by_phone_or_username("nam.nguyen")
    plan = plans.get_by_id("PKG01")
    subscription = subscriptions.find_by_qrcode("QR-HV1001-PKG03-ACTIVE")
    active_subscription = subscriptions.find_active_by_username("nam.nguyen")
    invoice = invoices.get_by_id("INV001")

    assert member is not None
    assert member.phone == "0987654321"
    assert member_by_phone is not None
    assert member_by_phone.username == "nam.nguyen"
    assert member_by_key is not None
    assert member_by_key.username == "nam.nguyen"
    assert len(users.get_all_members(limit=10)) >= 2
    assert len(plans.get_active_plans()) == 5
    assert len(plans.get_all()) >= 5
    assert plan is not None
    assert plan.price == 450000
    assert subscription is not None
    assert subscription.subscription_id == "SUB001"
    assert active_subscription is not None
    assert active_subscription.subscription_id == "SUB001"
    assert invoice is not None
    assert invoice.invoice_id == "INV001"
    assert invoices.get_recent_invoices(limit=10)
    assert isinstance(CheckInRepository().get_today_logs(limit=10), list)
    assert users.execute_scalar("SELECT COUNT(*) FROM `Role`") == 3


def test_repository_writes_rollback_as_one_transaction() -> None:
    suffix = uuid4().hex[:8].upper()
    username = f"U{suffix}"
    subscription_id = f"S{suffix}"
    invoice_id = f"I{suffix}"
    notification_id = f"N{suffix}"
    check_in_id = f"C{suffix}"
    user_repository = UserRepository()
    subscription_repository = SubscriptionRepository()
    check_in_repository = CheckInRepository()

    with pytest.raises(DatabaseTransactionException) as error:
        with db.transaction(dictionary=False) as cursor:
            user_repository.create_with_cursor(
                cursor,
                User(
                    username=username,
                    phone=f"09{suffix[:8]}",
                    full_name="Repository Test",
                ),
            )
            subscription_repository.create_with_cursor(
                cursor,
                MemberSubscription(
                    subscription_id=subscription_id,
                    username=username,
                    plan_id="PKG01",
                    qr_code=f"QR-{suffix}",
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=30),
                    remaining_check_in_sessions=2,
                    created_at=date.today(),
                ),
            )
            InvoiceRepository().create_with_cursor(
                cursor,
                Invoice(
                    invoice_id=invoice_id,
                    username=username,
                    subscription_id=subscription_id,
                    total_amount=450000,
                    paid_at=datetime.now(),
                ),
            )
            NotificationRepository().create_with_cursor(
                cursor,
                Notification(
                    notification_id=notification_id,
                    username=username,
                    title="Test",
                    message="Rollback test",
                ),
            )
            check_in_repository.create_with_cursor(
                cursor,
                CheckInLog(
                    check_in_id=check_in_id,
                    username=username,
                    subscription_id=subscription_id,
                    check_in_at=datetime.now(),
                ),
            )
            assert subscription_repository.decrement_sessions_with_cursor(
                cursor, subscription_id
            )
            raise RuntimeError("Force rollback after repository writes")

    assert isinstance(error.value.__cause__, RuntimeError)
    with db.cursor() as cursor:
        for table, identifier_column, identifier in (
            ("User", "UserName", username),
            ("MemberSubscription", "SubscriptionId", subscription_id),
            ("Invoice", "InvoiceId", invoice_id),
            ("Notification", "NotificationId", notification_id),
            ("CheckInLog", "CheckInId", check_in_id),
        ):
            cursor.execute(
                f"SELECT COUNT(*) AS `row_count` FROM `{table}` "
                f"WHERE `{identifier_column}` = %s",
                (identifier,),
            )
            assert cursor.fetchone()["row_count"] == 0
