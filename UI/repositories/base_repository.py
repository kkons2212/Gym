"""Generic helpers for repositories backed by MySQL."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Sequence, Type, TypeVar

import mysql.connector
from mysql.connector.cursor import MySQLCursor

from database.db_connection import db
from exceptions import DatabaseTransactionException
from models.base_model import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)

logger = logging.getLogger(__name__)


class BaseRepository(ABC, Generic[ModelT]):
    """Provide shared parameterized MySQL operations for repositories."""

    table_name: str
    id_column: str

    @property
    @abstractmethod
    def entity_type(self) -> Type[ModelT]:
        """Return the entity class used to map database rows."""

    def get_by_id(self, record_id: str) -> Optional[ModelT]:
        """Fetch one entity by its primary key."""
        query = (
            f"SELECT * FROM `{self.table_name}` "
            f"WHERE `{self.id_column}` = %s LIMIT 1"
        )
        rows = self.execute_query(query, (record_id,))
        if not rows:
            return None
        return self.entity_type.from_row(rows[0])

    def get_all(self) -> List[ModelT]:
        """Fetch all rows from this repository's table."""
        query = f"SELECT * FROM `{self.table_name}`"
        rows = self.execute_query(query)
        return [self.entity_type.from_row(row) for row in rows]

    def execute_query(
        self, query: str, params: Sequence[Any] = ()
    ) -> List[Dict[str, Any]]:
        """Execute a parameterized query and return dictionary rows."""
        try:
            with db.cursor(dictionary=True) as cursor:
                cursor.execute(query, tuple(params))
                return cursor.fetchall()
        except DatabaseTransactionException:
            raise
        except mysql.connector.Error as err:
            logger.exception("MySQL query failed.")
            raise DatabaseTransactionException(err) from err

    def execute_scalar(
        self, query: str, params: Sequence[Any] = ()
    ) -> Optional[Any]:
        """Execute a query and return the first value of its first row."""
        try:
            with db.cursor(dictionary=True) as cursor:
                cursor.execute(query, tuple(params))
                row = cursor.fetchone()
        except DatabaseTransactionException:
            raise
        except mysql.connector.Error as err:
            logger.exception("MySQL scalar query failed.")
            raise DatabaseTransactionException(err) from err

        if row is None:
            return None
        if isinstance(row, dict):
            return next(iter(row.values()), None)
        return row[0] if row else None

    @staticmethod
    def execute_with_cursor(
        cursor: MySQLCursor, query: str, params: Sequence[Any] = ()
    ) -> int:
        """Execute a write using a caller-owned transaction cursor."""
        try:
            cursor.execute(query, tuple(params))
            return cursor.rowcount
        except mysql.connector.Error as err:
            logger.exception("MySQL statement failed.")
            raise DatabaseTransactionException(err) from err
