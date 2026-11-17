"""Repository operations for member notifications."""

from __future__ import annotations

from typing import Type

from mysql.connector.cursor import MySQLCursor

from models.notification import Notification
from repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Write notification records."""

    table_name = "Notification"
    id_column = "NotificationId"

    @property
    def entity_type(self) -> Type[Notification]:
        return Notification

    def create_with_cursor(
        self, cursor: MySQLCursor, notification: Notification
    ) -> None:
        """Insert a notification using the caller's transaction."""
        query = (
            "INSERT INTO `Notification` "
            "(`NotificationId`, `Title`, `Message`, `IsRead`, `CreatedAt`, "
            "`UserName`) VALUES (%s, %s, %s, %s, "
            "COALESCE(%s, CURRENT_DATE), %s)"
        )
        params = (
            notification.notification_id,
            notification.title,
            notification.message,
            notification.is_read,
            notification.created_at,
            notification.username,
        )
        self.execute_with_cursor(cursor, query, params)
