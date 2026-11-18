"""Database Connection Manager with Singleton Connection Pool.

Implements thread-safe MySQL connection pooling and transactional context managers
with automated commit, rollback on error, and leak-free resource disposal.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Generator, Optional
import mysql.connector
from mysql.connector import pooling
from mysql.connector.cursor import MySQLCursor

from config.settings import settings
from exceptions import DatabaseTransactionException

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Singleton Manager for MySQL connection pooling and transactional execution."""

    _instance: Optional[DatabaseConnection] = None
    _pool: Optional[pooling.MySQLConnectionPool] = None

    def __new__(cls) -> DatabaseConnection:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _initialize_pool(self) -> None:
        """Khởi tạo connection pool một lần duy nhất theo cấu hình từ settings."""
        if self._pool is not None:
            return

        db_cfg = settings.get_db_config()
        pool_name = settings.db_pool_name
        pool_size = settings.db_pool_size

        try:
            self._pool = pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                pool_reset_session=True,
                **db_cfg,
            )
            logger.info(
                "Đã khởi tạo MySQL Connection Pool thành công: name=%s, size=%d, db=%s",
                pool_name,
                pool_size,
                db_cfg.get("database"),
            )
        except mysql.connector.Error as err:
            self._pool = None
            logger.error("Không thể khởi tạo MySQL Connection Pool: %s", err)
            raise DatabaseTransactionException(err) from err

    def get_connection(self) -> mysql.connector.connection.MySQLConnection:
        """Lấy một kết nối còn rảnh từ connection pool.

        Returns:
            MySQLConnection: Kết nối sẵn sàng thực thi truy vấn.
        """
        if self._pool is None:
            self._initialize_pool()

        try:
            return self._pool.get_connection()
        except mysql.connector.Error as err:
            logger.error("Lỗi cấp phát kết nối từ Connection Pool: %s", err)
            raise DatabaseTransactionException(err) from err

    @contextmanager
    def transaction(
        self, dictionary: bool = True
    ) -> Generator[MySQLCursor, None, None]:
        """Context manager điều phối transaction an toàn.

        Tự động commit khi kết thúc khối lệnh không lỗi.
        Tự động rollback khi phát sinh ngoại lệ.
        Luôn đóng cursor và trả kết nối về pool trong khối finally.

        Args:
            dictionary: Nếu True, cursor trả về dạng dict; nếu False, trả về tuple.

        Yields:
            MySQLCursor: Con trỏ thực thi SQL trong transaction hiện hành.
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=dictionary)
        try:
            yield cursor
            conn.commit()
        except Exception as err:
            conn.rollback()
            logger.error("Transaction gặp lỗi, đã tự động rollback: %s", err)
            if isinstance(err, DatabaseTransactionException):
                raise
            raise DatabaseTransactionException(err) from err
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass

    @contextmanager
    def cursor(
        self, dictionary: bool = True
    ) -> Generator[MySQLCursor, None, None]:
        """Context manager dùng cho các truy vấn SELECT chỉ đọc (Read-only)."""
        conn = self.get_connection()
        cur = conn.cursor(dictionary=dictionary)
        try:
            yield cur
        except Exception as err:
            logger.error("Lỗi thực thi truy vấn chỉ đọc: %s", err)
            raise DatabaseTransactionException(err) from err
        finally:
            try:
                cur.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass


# Đối tượng Singleton tiện ích dùng toàn cục
db = DatabaseConnection()
