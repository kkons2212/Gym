"""Repository operations for member subscriptions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type

from mysql.connector.cursor import MySQLCursor

from constants import RoleID, SubscriptionStatus
from database.db_connection import db
from models.member_subscription import MemberSubscription
from repositories.base_repository import BaseRepository


class SubscriptionRepository(BaseRepository[MemberSubscription]):
    """Read and update membership subscriptions."""

    table_name = "MemberSubscription"
    id_column = "SubscriptionId"

    @property
    def entity_type(self) -> Type[MemberSubscription]:
        return MemberSubscription

    def create_with_cursor(
        self, cursor: MySQLCursor, subscription: MemberSubscription
    ) -> None:
        """Insert a subscription using the caller's transaction."""
        query = (
            "INSERT INTO `MemberSubscription` "
            "(`SubscriptionId`, `QrCode`, `StartDate`, `EndDate`, "
            "`RemainingCheckInSessions`, `RemainingPtSessions`, "
            "`FreezeStartDate`, `FreezeEndDate`, `Status`, `created_at`, "
            "`UserName`, `AssignedPtId`, `PlanId`, `PTSessionId`) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        params = (
            subscription.subscription_id,
            subscription.qr_code,
            subscription.start_date,
            subscription.end_date,
            subscription.remaining_check_in_sessions,
            subscription.remaining_pt_sessions,
            subscription.freeze_start_date,
            subscription.freeze_end_date,
            subscription.status,
            subscription.created_at,
            subscription.username,
            subscription.assigned_pt_id,
            subscription.plan_id,
            subscription.pt_session_id,
        )
        self.execute_with_cursor(cursor, query, params)

    def find_by_qrcode(self, qr_token: str) -> Optional[MemberSubscription]:
        """Find a subscription by its QR token."""
        rows = self.execute_query(
            "SELECT * FROM `MemberSubscription` WHERE `QrCode` = %s LIMIT 1",
            (qr_token,),
        )
        return MemberSubscription.from_row(rows[0]) if rows else None

    def find_active_by_username(
        self, username: str
    ) -> Optional[MemberSubscription]:
        """Find the newest active subscription for a member."""
        rows = self.execute_query(
            "SELECT * FROM `MemberSubscription` "
            "WHERE `UserName` = %s AND `Status` = %s "
            "ORDER BY `StartDate` DESC, `created_at` DESC, "
            "`SubscriptionId` DESC LIMIT 1",
            (username, SubscriptionStatus.ACTIVE.value),
        )
        return MemberSubscription.from_row(rows[0]) if rows else None

    def get_member_summaries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch members with their newest subscription and package details."""
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit phải là số nguyên dương.")

        query = (
            "SELECT `User`.`UserName` AS `username`, "
            "`User`.`FullName` AS `full_name`, `User`.`Phone` AS `phone`, "
            "`User`.`Email` AS `email`, `User`.`Status` AS `user_status`, "
            "`MemberSubscription`.`SubscriptionId` AS `subscription_id`, "
            "`MemberSubscription`.`QrCode` AS `qr_code`, "
            "`MemberSubscription`.`StartDate` AS `start_date`, "
            "`MemberSubscription`.`EndDate` AS `end_date`, "
            "`MemberSubscription`.`Status` AS `subscription_status`, "
            "`MemberSubscription`.`RemainingCheckInSessions` "
            "AS `remaining_check_in_sessions`, "
            "`MemberSubscription`.`RemainingPtSessions` "
            "AS `remaining_pt_sessions`, "
            "`MemberSubscription`.`AssignedPtId` AS `assigned_pt_id`, "
            "`MemberSubscription`.`PlanId` AS `plan_id`, "
            "`PackagePlan`.`Name` AS `plan_name` "
            "FROM `User` "
            "LEFT JOIN `MemberSubscription` ON "
            "`MemberSubscription`.`SubscriptionId` = ("
            "SELECT `newest`.`SubscriptionId` "
            "FROM `MemberSubscription` AS `newest` "
            "WHERE `newest`.`UserName` = `User`.`UserName` "
            "ORDER BY `newest`.`StartDate` DESC, "
            "`newest`.`created_at` DESC, "
            "`newest`.`SubscriptionId` DESC LIMIT 1) "
            "LEFT JOIN `PackagePlan` ON "
            "`PackagePlan`.`PlanId` = `MemberSubscription`.`PlanId` "
            "WHERE `User`.`RoleID` = %s "
            "ORDER BY `User`.`created_at` DESC, `User`.`UserName` ASC "
            "LIMIT %s"
        )
        return self.execute_query(query, (RoleID.MEMBER.value, limit))

    def decrement_sessions(self, subscription_id: str) -> bool:
        """Atomically decrement a positive session count for an active card."""
        with db.transaction(dictionary=False) as cursor:
            return self.decrement_sessions_with_cursor(cursor, subscription_id)

    def decrement_sessions_with_cursor(
        self, cursor: MySQLCursor, subscription_id: str
    ) -> bool:
        """Decrement sessions in an existing transaction, if any remain."""
        query = (
            "UPDATE `MemberSubscription` "
            "SET `RemainingCheckInSessions` = `RemainingCheckInSessions` - 1 "
            "WHERE `SubscriptionId` = %s AND `Status` = %s "
            "AND `RemainingCheckInSessions` > 0"
        )
        affected_rows = self.execute_with_cursor(
            cursor, query, (subscription_id, SubscriptionStatus.ACTIVE.value)
        )
        return affected_rows == 1
