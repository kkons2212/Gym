"""VietQR Payment Integration Service.

Supports dynamic QR generation through VietQR Sandbox API (https://api.vietqr.io/v2/generate)
with automated offline fallback using local EMVCo format and qrcode library.
Ensures counter POS checkout is never blocked by network latency or API outages.
"""

from __future__ import annotations

import base64
import io
import logging
from typing import Tuple

import qrcode
import requests

from config.settings import settings

logger = logging.getLogger(__name__)


class VietQrService:
    """Service chịu trách nhiệm tích hợp và sinh mã QR thanh toán ngân hàng."""

    API_URL = "https://api.vietqr.io/v2/generate"
    DEFAULT_TIMEOUT_SECONDS = 5

    def __init__(self) -> None:
        self.account_no = settings.vietqr_account_no
        self.account_name = settings.vietqr_account_name
        self.bank_bin = settings.vietqr_bank_bin
        self.template = settings.vietqr_template
        self.client_id = settings.vietqr_client_id
        self.api_key = settings.vietqr_api_key

    def generate_qr_payment(
        self, amount: int, order_code: str
    ) -> Tuple[bool, str]:
        """Tạo mã QR thanh toán VietQR động cho đơn hàng hoặc gói đăng ký.

        Thử gọi API VietQR trước; nếu mất mạng hoặc API lỗi, tự động
        chuyển sang tạo mã offline bằng thư viện qrcode cục bộ.

        Args:
            amount: Số tiền thanh toán (VNĐ, >= 0).
            order_code: Nội dung chuyển khoản / Mã hóa đơn (Unique).

        Returns:
            Tuple[bool, str]: (Thành công: True/False, Chuỗi Base64 Data URL ảnh QR hoặc thông báo lỗi).
        """
        if amount < 0:
            return False, "Số tiền thanh toán không được là số âm."

        # Thử gọi API VietQR chính thức nếu có Client ID hoặc thử kết nối mạng
        try:
            headers = {
                "Content-Type": "application/json",
            }
            if self.client_id and self.api_key:
                headers["x-client-id"] = self.client_id
                headers["x-api-key"] = self.api_key

            payload = {
                "accountNo": self.account_no,
                "accountName": self.account_name,
                "acqId": self.bank_bin,
                "amount": int(amount),
                "addInfo": order_code,
                "format": "text",
                "template": self.template,
            }

            response = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=self.DEFAULT_TIMEOUT_SECONDS,
            )

            if response.status_code == 200:
                res_data = response.json()
                if res_data.get("code") == "00" and res_data.get("data"):
                    qr_data_url = res_data["data"].get("qrDataURL")
                    if qr_data_url:
                        logger.info(
                            "Sinh mã VietQR online thành công qua API: order=%s, amount=%d",
                            order_code,
                            amount,
                        )
                        return True, qr_data_url
        except Exception as err:
            logger.warning(
                "Không thể kết nối API VietQR (%s). Chuyển sang cơ chế Offline Fallback.",
                err,
            )

        # Cơ chế Offline Fallback: Sinh chuỗi EMVCo cục bộ và render Base64
        return self._generate_offline_qr(amount, order_code)

    def _generate_offline_qr(
        self, amount: int, order_code: str
    ) -> Tuple[bool, str]:
        """Sinh mã QR VietQR ngoại tuyến chuẩn EMVCo và chuyển đổi thành Base64 Data URL."""
        try:
            # Tạo chuỗi dữ liệu chuyển khoản ngân hàng chuẩn Napas VietQR
            # Cấu trúc payload ngân hàng: 000201...
            clean_acc = self.account_no.replace(" ", "")
            amt_str = str(int(amount))
            clean_memo = order_code[:25].replace(" ", "_")

            emvco_payload = (
                f"00020101021238540010A00000072701240006{self.bank_bin}"
                f"01{len(clean_acc):02d}{clean_acc}530370454{len(amt_str):02d}{amt_str}"
                f"5802VN62{len(clean_memo) + 4:02d}08{len(clean_memo):02d}{clean_memo}6304"
            )

            # Render ảnh QR bằng qrcode cục bộ
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=6,
                border=2,
            )
            qr.add_data(emvco_payload)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            data_url = f"data:image/png;base64,{b64_str}"

            logger.info(
                "Đã sinh mã VietQR offline dự phòng thành công: order=%s",
                order_code,
            )
            return True, data_url
        except Exception as err:
            logger.error("Lỗi sinh mã QR offline: %s", err)
            return False, f"Lỗi sinh mã QR ngoại tuyến: {err}"
