"""Module quản trị cấu hình tập trung và biến môi trường (Zero-Secrets Rule).

Đọc các biến cấu hình từ tệp .env và biến môi trường hệ thống,
cung cấp tham số kết nối an toàn cho CSDL MySQL 8.0, VietQR Sandbox,
và các thiết lập runtime khác của ứng dụng.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


class Settings:
    """Lớp lưu trữ cấu hình ứng dụng tập trung (Centralized Application Settings).

    Thuộc tính:
        db_host (str): Địa chỉ máy chủ CSDL MySQL.
        db_port (int): Cổng kết nối CSDL MySQL.
        db_name (str): Tên CSDL hệ thống.
        db_user (str): Tên người dùng CSDL.
        db_password (str): Mật khẩu người dùng CSDL.
        db_pool_name (str): Tên định danh cho Connection Pool.
        db_pool_size (int): Kích thước vùng đệm kết nối.
        vietqr_client_id (str): Client ID dịch vụ VietQR Sandbox.
        vietqr_api_key (str): API Key dịch vụ VietQR Sandbox.
        vietqr_account_no (str): Số tài khoản ngân hàng thụ hưởng.
        vietqr_account_name (str): Tên chủ tài khoản thụ hưởng.
        vietqr_bank_bin (str): Mã BIN ngân hàng (ví dụ: 970422).
        vietqr_template (str): Giao diện mẫu QR của VietQR.
        app_env (str): Môi trường hoạt động (development, test, production).
        log_level (str): Mức độ ghi nhật ký hệ thống.
    """

    def __init__(self, env_file: Path | str | None = None) -> None:
        """Khởi tạo và nạp cấu hình từ tệp .env nếu có.

        Args:
            env_file: Đường dẫn tùy chỉnh tới tệp .env (tùy chọn).
        """
        self._load_environment(env_file)
        self._validate_configuration()

    def _load_environment(self, env_file: Path | str | None = None) -> None:
        """Tìm kiếm và nạp tệp .env theo thứ tự ưu tiên."""
        if env_file and Path(env_file).exists():
            self._apply_env_file(Path(env_file))
            return

        # Tìm .env ở thư mục gốc của dự án (cấp cha của UI) hoặc thư mục làm việc
        possible_paths = [
            Path.cwd() / ".env",
            Path(__file__).resolve().parent.parent.parent / ".env",
            Path(__file__).resolve().parent.parent / ".env",
        ]

        for path in possible_paths:
            if path.exists():
                self._apply_env_file(path)
                break

    def _apply_env_file(self, path: Path) -> None:
        """Nạp các cặp key-value từ file .env vào os.environ."""
        if load_dotenv is not None:
            load_dotenv(dotenv_path=path, override=False)
            return

        # Fallback phân tích cú pháp đơn giản khi chưa cài đặt python-dotenv
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = val
        except OSError:
            pass

    def _validate_configuration(self) -> None:
        """Kiểm tra tính hợp lệ của các tham số cốt lõi (Fail-Fast).

        Raises:
            ValueError: Khi thông số kết nối CSDL không hợp lệ.
        """
        if self.db_port <= 0 or self.db_port > 65535:
            raise ValueError(f"Cổng CSDL không hợp lệ: {self.db_port}")

        if not self.db_host.strip():
            raise ValueError("Địa chỉ DB_HOST không được để trống.")

        if not self.db_name.strip():
            raise ValueError("Tên DB_NAME không được để trống.")

    @property
    def db_host(self) -> str:
        """Địa chỉ máy chủ MySQL (mặc định: 127.0.0.1)."""
        return os.getenv("DB_HOST", "127.0.0.1")

    @property
    def db_port(self) -> int:
        """Cổng kết nối MySQL (mặc định: 3306)."""
        raw_val = os.getenv("DB_PORT", "3306")
        try:
            return int(raw_val)
        except ValueError:
            return 3306

    @property
    def db_name(self) -> str:
        """Tên cơ sở dữ liệu (mặc định: gym_management_db)."""
        return os.getenv("DB_NAME", "gym_management_db")

    @property
    def db_user(self) -> str:
        """Tài khoản truy cập CSDL (mặc định: gym_user)."""
        return os.getenv("DB_USER", "gym_user")

    @property
    def db_password(self) -> str:
        """Mật khẩu truy cập CSDL (mặc định: gym_password@2026)."""
        return os.getenv("DB_PASSWORD", "gym_password@2026")

    @property
    def db_pool_name(self) -> str:
        """Tên của Connection Pool (mặc định: gym_connection_pool)."""
        return os.getenv("DB_POOL_NAME", "gym_connection_pool")

    @property
    def db_pool_size(self) -> int:
        """Kích thước connection pool (mặc định: 5)."""
        raw_val = os.getenv("DB_POOL_SIZE", "5")
        try:
            val = int(raw_val)
            return max(1, min(val, 32))
        except ValueError:
            return 5

    @property
    def vietqr_client_id(self) -> str:
        """Client ID VietQR Sandbox API."""
        return os.getenv("VIETQR_CLIENT_ID", "")

    @property
    def vietqr_api_key(self) -> str:
        """API Key VietQR Sandbox API."""
        return os.getenv("VIETQR_API_KEY", "")

    @property
    def vietqr_account_no(self) -> str:
        """Số tài khoản ngân hàng thụ hưởng (mặc định: 0987654321)."""
        return os.getenv("VIETQR_ACCOUNT_NO", "0987654321")

    @property
    def vietqr_account_name(self) -> str:
        """Tên chủ tài khoản thụ hưởng."""
        return os.getenv("VIETQR_ACCOUNT_NAME", "HE THONG PHONG TAP GYM")

    @property
    def vietqr_bank_bin(self) -> str:
        """Mã BIN ngân hàng thụ hưởng (mặc định: 970422)."""
        return os.getenv("VIETQR_BANK_BIN", "970422")

    @property
    def vietqr_template(self) -> str:
        """Mẫu giao diện VietQR (mặc định: compact2)."""
        return os.getenv("VIETQR_TEMPLATE", "compact2")

    @property
    def app_env(self) -> str:
        """Môi trường hoạt động của ứng dụng (mặc định: development)."""
        return os.getenv("APP_ENV", "development").lower()

    @property
    def log_level(self) -> str:
        """Mức log hệ thống (mặc định: INFO)."""
        return os.getenv("LOG_LEVEL", "INFO").upper()

    def get_db_config(self) -> Dict[str, Any]:
        """Tạo từ điển cấu hình chuẩn để kết nối MySQL Connector.

        Returns:
            Dict[str, Any]: Tham số nạp trực tiếp vào mysql.connector.connect.
        """
        return {
            "host": self.db_host,
            "port": self.db_port,
            "user": self.db_user,
            "password": self.db_password,
            "database": self.db_name,
            "charset": "utf8mb4",
            "use_pure": True,
            "autocommit": False,
        }


# Đối tượng cấu hình Singleton dùng toàn cục trong ứng dụng
settings = Settings()
