"""Repository operations for check-in logs."""

from __future__ import annotations

from typing import Any, Dict, List

from mysql.connector.cursor import MySQLCursor

from database.db_connection import db
from models.check_in_log import CheckInLog
from repositories.base_repository import BaseRepository


class CheckInRepository(BaseRepository[CheckInLog]):
    """Read and write member check-in attempts."""

    table_name = "CheckInLog"
    id_column = "CheckInId"

    @property
    def entity_type(self) -> type[CheckInLog]:
        return CheckInLog

    def create(self, log: CheckInLog) -> None:
        """Insert a check-in log in its own transaction."""
        with db.transaction(dictionary=False) as cursor:
            self.create_with_cursor(cursor, log)

    def create_with_cursor(self, cursor: MySQLCursor, log: CheckInLog) -> None:
        """Insert a check-in log using the caller's transaction."""
        if log.subscription_id is None:
            raise ValueError(
                "SubscriptionId là bắt buộc theo lược đồ CheckInLog."
            )

        query = (
            "INSERT INTO `CheckInLog` "
            "(`CheckInId`, `check_in_at`, `Status`, `DenialReason`, "
            "`SubscriptionId`, `VerifiedByAdminId`, `UserName`) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        params = (
            log.check_in_id,
            log.check_in_at,
            log.status,
            log.denial_reason,
            log.subscription_id,
            log.verified_by_admin_id,
            log.username,
        )
        self.execute_with_cursor(cursor, query, params)

    def get_today_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch today's check-in attempts with the member's full name."""
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit phải là số nguyên dương.")

        query = (
            "SELECT `CheckInLog`.`CheckInId` AS `check_in_id`, "
            "`CheckInLog`.`check_in_at` AS `check_in_at`, "
            "`CheckInLog`.`Status` AS `status`, "
            "`CheckInLog`.`DenialReason` AS `denial_reason`, "
            "`CheckInLog`.`SubscriptionId` AS `subscription_id`, "
            "`CheckInLog`.`VerifiedByAdminId` AS `verified_by_admin_id`, "
            "`CheckInLog`.`UserName` AS `username`, "
            "`User`.`FullName` AS `full_name` "
            "FROM `CheckInLog` "
            "JOIN `User` ON `User`.`UserName` = `CheckInLog`.`UserName` "
            "WHERE `CheckInLog`.`check_in_at` >= CURRENT_DATE "
            "AND `CheckInLog`.`check_in_at` < CURRENT_DATE + INTERVAL 1 DAY "
            "ORDER BY `CheckInLog`.`check_in_at` DESC, "
            "`CheckInLog`.`CheckInId` DESC LIMIT %s"
        )
        return self.execute_query(query, (limit,))
