"""Dialog displaying live member and subscription information."""

from __future__ import annotations

from typing import Any, Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from components.qr_widget import QRWidget
from styles.color_tokens import (
    ACCENT_PRIMARY,
    STATUS_DANGER,
    STATUS_DANGER_BG,
    STATUS_SUCCESS,
    STATUS_SUCCESS_BG,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class MemberDetailDialog(QDialog):
    """Present saved member data without fabricating unavailable metrics."""

    def __init__(self, member: Dict[str, Any], parent=None) -> None:
        super().__init__(parent)
        self.member = member
        self.setWindowTitle(
            "Hồ sơ hội viên • "
            f"{member.get('name') or 'Hội viên'}"
        )
        self.setFixedSize(620, 560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        identity = QVBoxLayout()
        name = QLabel(member.get("name") or "—")
        name.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;"
        )
        code = QLabel(
            f"Mã HV: {member.get('code') or '—'}"
            f"  •  SĐT: {member.get('phone') or '—'}"
        )
        code.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        identity.addWidget(name)
        identity.addWidget(code)
        header.addLayout(identity)
        header.addStretch()

        status = member.get("status") or "Không xác định"
        badge = QLabel(f"  {status.upper()}  ")
        if status == "Đang hoạt động":
            badge.setStyleSheet(
                f"color: {STATUS_SUCCESS}; "
                f"background-color: {STATUS_SUCCESS_BG}; "
                "border-radius: 4px; font-size: 11px; "
                "font-weight: bold; padding: 4px;"
            )
        else:
            badge.setStyleSheet(
                f"color: {STATUS_DANGER}; "
                f"background-color: {STATUS_DANGER_BG}; "
                "border-radius: 4px; font-size: 11px; "
                "font-weight: bold; padding: 4px;"
            )
        header.addWidget(badge)
        layout.addLayout(header)

        content_row = QHBoxLayout()
        content_row.setSpacing(16)
        membership_card = QFrame()
        membership_card.setObjectName("cardFrame")
        membership_layout = QVBoxLayout(membership_card)
        membership_layout.setSpacing(8)

        title = QLabel("THÔNG TIN GÓI TẬP HIỆN TẠI")
        title.setStyleSheet(
            f"color: {ACCENT_PRIMARY}; font-size: 12px; font-weight: bold;"
        )
        membership_layout.addWidget(title)

        check_ins_left = member.get("check_ins_left")
        check_ins_text = (
            "Không giới hạn"
            if check_ins_left is None and member.get("qr_code")
            else str(check_ins_left)
            if check_ins_left is not None
            else "—"
        )
        pt_sessions = member.get("sessions_left")
        rows = (
            ("Gói dịch vụ:", member.get("package_name") or "Chưa đăng ký"),
            ("Ngày bắt đầu:", member.get("start_date") or "—"),
            ("Ngày hết hạn:", member.get("expiry_date") or "—"),
            ("Lượt check-in còn:", check_ins_text),
            (
                "Buổi PT còn:",
                str(pt_sessions) if pt_sessions is not None else "—",
            ),
            ("HLV phụ trách:", member.get("pt_assigned") or "Chưa phân công"),
            ("Email:", member.get("email") or "—"),
        )
        for label_text, value_text in rows:
            row = QHBoxLayout()
            row.addWidget(QLabel(label_text))
            row.addStretch()
            value = QLabel(str(value_text))
            value.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold;")
            row.addWidget(value)
            membership_layout.addLayout(row)
        content_row.addWidget(membership_card, 6)

        qr_code = member.get("qr_code")
        if qr_code:
            content_row.addWidget(
                QRWidget(
                    data=str(qr_code),
                    size=150,
                    caption="Mã QR check-in",
                ),
                4,
            )
        else:
            no_qr_card = QFrame()
            no_qr_card.setObjectName("cardFrame")
            no_qr_layout = QVBoxLayout(no_qr_card)
            no_qr = QLabel("Chưa có thẻ QR")
            no_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_qr_layout.addWidget(no_qr)
            content_row.addWidget(no_qr_card, 4)
        layout.addLayout(content_row)

        inbody_card = QFrame()
        inbody_card.setObjectName("cardFrame")
        inbody_layout = QGridLayout(inbody_card)
        inbody_layout.addWidget(QLabel("Chỉ số InBody:"), 0, 0)
        inbody_layout.addWidget(
            QLabel("Chưa có dữ liệu InBody trong hệ thống."), 0, 1
        )
        layout.addWidget(inbody_card)

        close_button = QPushButton("Đóng")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
