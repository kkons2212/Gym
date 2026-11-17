"""Repository operations for users and gym members."""

from __future__ import annotations

from typing import List, Optional, Type

from mysql.connector.cursor import MySQLCursor

from constants import RoleID
from models.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Read and write user records."""

    table_name = "User"
    id_column = "UserName"

    @property
    def entity_type(self) -> Type[User]:
        return User

    def create_with_cursor(self, cursor: MySQLCursor, user: User) -> None:
        """Insert a user using the caller's transaction."""
        query = (
            "INSERT INTO `User` "
            "(`UserName`, `RoleID`, `FullName`, `Phone`, `Email`, "
            "`PasswordHash`, `Gender`, `Status`, `created_at`) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        params = (
            user.username,
            user.role_id,
            user.full_name,
            user.phone,
            user.email,
            user.password_hash,
            user.gender,
            user.status,
            user.created_at,
        )
        self.execute_with_cursor(cursor, query, params)

    def find_by_username(self, username: str) -> Optional[User]:
        """Find a user by username."""
        rows = self.execute_query(
            "SELECT * FROM `User` WHERE `UserName` = %s LIMIT 1",
            (username,),
        )
        return User.from_row(rows[0]) if rows else None

    def find_by_phone(self, phone: str) -> Optional[User]:
        """Find a user by phone number."""
        rows = self.execute_query(
            "SELECT * FROM `User` WHERE `Phone` = %s LIMIT 1",
            (phone,),
        )
        return User.from_row(rows[0]) if rows else None

    def find_by_phone_or_username(self, search_key: str) -> Optional[User]:
        """Find a user by username or phone, preferring the username."""
        rows = self.execute_query(
            "SELECT * FROM `User` "
            "WHERE `UserName` = %s OR `Phone` = %s "
            "ORDER BY (`UserName` = %s) DESC LIMIT 1",
            (search_key, search_key, search_key),
        )
        return User.from_row(rows[0]) if rows else None

    def get_all_members(self, limit: int = 100) -> List[User]:
        """Fetch members ordered by newest account first."""
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit phải là số nguyên dương.")

        rows = self.execute_query(
            "SELECT * FROM `User` WHERE `RoleID` = %s "
            "ORDER BY `created_at` DESC, `UserName` ASC LIMIT %s",
            (RoleID.MEMBER.value, limit),
        )
        return [User.from_row(row) for row in rows]
