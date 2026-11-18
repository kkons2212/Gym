"""Dialog for registering a member with a live package plan (2-Step Wizard)."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from PyQt6.QtCore import (
    QObject,
    QRunnable,
    Qt,
    QThreadPool,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from constants import PaymentMethod
from components.qr_widget import QRWidget
from desktop_portal.dialogs.vietqr_dialog import VietQrPaymentDialog
from exceptions import (
    DatabaseTransactionException,
    DuplicateUserException,
    PackageNotFoundException,
    ValidationException,
)
from models.package_plan import PackagePlan
from services.member_service import MemberService
from services.vietqr_service import VietQrService


class _QrSignals(QObject):
    finished = pyqtSignal(bool, str)


class _QrGenerationTask(QRunnable):
    def __init__(
        self, service: VietQrService, amount: int, invoice_code: str
    ) -> None:
        super().__init__()
        self.service = service
        self.amount = amount
        self.invoice_code = invoice_code
        self.signals = _QrSignals()

    def run(self) -> None:
        success, result = self.service.generate_qr_payment(
            self.amount, self.invoice_code
        )
        self.signals.finished.emit(success, result)


class _PaymentMethodRadioAdapter:
    """Adapter providing isChecked/setChecked compatibility for test suites."""

    def __init__(self, combo: QComboBox, method: str) -> None:
        self._combo = combo
        self._method = method

    def isChecked(self) -> bool:
        return self._combo.currentData() == self._method

    def setChecked(self, checked: bool) -> None:
        if checked:
            idx = self._combo.findData(self._method)
            if idx >= 0:
                self._combo.setCurrentIndex(idx)

    def setEnabled(self, enabled: bool) -> None:
        pass


class RegisterMemberDialog(QDialog):
    """Collect registration details and save after payment confirmation."""

    def __init__(
        self,
        parent=None,
        member_service: Optional[MemberService] = None,
        vietqr_service: Optional[VietQrService] = None,
        preferred_plan_id: Optional[str] = None,
    ) -> None:
        super().__init__(parent)
        self.member_service = member_service or MemberService()
        self.vietqr_service = vietqr_service or VietQrService()
        self.preferred_plan_id = preferred_plan_id
        self._is_submitting = False
        self._qr_task: Optional[_QrGenerationTask] = None
        self._plans_by_id: Dict[str, PackagePlan] = {}
        self._fields: Dict[str, QLineEdit] = {}
        self._errors: Dict[str, QLabel] = {}

        self.setWindowTitle("Đăng ký hội viên mới")
        self.setFixedWidth(560)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        # Title
        title = QLabel("ĐĂNG KÝ HỘI VIÊN MỚI & KÍCH HOẠT GÓI (2-STEP)")
        title.setObjectName("pageTitle")
        title.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #F8FAFC;"
        )
        main_layout.addWidget(title)

        # -------------------------------------------------------------
        # STEP 1: Personal Info Card
        # -------------------------------------------------------------
        step1_card = QFrame()
        step1_card.setObjectName("cardFrame")
        step1_layout = QVBoxLayout(step1_card)
        step1_layout.setContentsMargins(16, 14, 16, 14)
        step1_layout.setSpacing(10)

        step1_header = QLabel("BƯỚC 1: THÔNG TIN CÁ NHÂN HỘI VIÊN")
        step1_header.setStyleSheet(
            "color: #38BDF8; font-weight: bold; font-size: 12px;"
        )
        step1_layout.addWidget(step1_header)

        # Row 1: Member Code (6) + Gender (4)
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(12)

        self.txt_code = self._create_input_field(
            "VD: MBR-0010 (Tối đa 10 ký tự)", "username", max_length=10
        )
        row1_layout.addWidget(
            self._create_field_widget(
                "Mã hội viên (Để trống để tự sinh mã):",
                self.txt_code,
                "username",
            ),
            6,
        )

        self.cbo_gender = QComboBox()
        self.cbo_gender.setFixedHeight(36)
        self.cbo_gender.addItem("Nam", 1)
        self.cbo_gender.addItem("Nữ", 0)
        self.cbo_gender.addItem("Khác", None)
        row1_layout.addWidget(
            self._create_field_widget("Giới tính:", self.cbo_gender), 4
        )
        step1_layout.addLayout(row1_layout)

        # Row 2: Full Name (6) + Phone (4)
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(12)

        self.txt_name = self._create_input_field(
            "Ví dụ: Nguyễn Văn An", "full_name"
        )
        row2_layout.addWidget(
            self._create_field_widget(
                "Họ và tên (*):", self.txt_name, "full_name"
            ),
            6,
        )

        self.txt_phone = self._create_input_field(
            "10 chữ số, ví dụ 0988112233", "phone", max_length=10
        )
        row2_layout.addWidget(
            self._create_field_widget(
                "Số điện thoại (*):", self.txt_phone, "phone"
            ),
            4,
        )
        step1_layout.addLayout(row2_layout)

        # Row 3: Email
        self.txt_email = self._create_input_field(
            "Không bắt buộc (ví dụ: member@example.com)", "email"
        )
        step1_layout.addWidget(
            self._create_field_widget(
                "Email liên hệ:", self.txt_email, "email"
            )
        )

        # Row 4: Password
        self.txt_password = self._create_input_field(
            "Nhập mật khẩu (tối thiểu 6 ký tự)...",
            "password",
            is_password=True,
        )
        self.txt_password.setText("123456")
        step1_layout.addWidget(
            self._create_field_widget(
                "Mật khẩu đăng nhập (*):", self.txt_password, "password"
            )
        )

        main_layout.addWidget(step1_card)

        # -------------------------------------------------------------
        # STEP 2: Package & Payment Card
        # -------------------------------------------------------------
        step2_card = QFrame()
        step2_card.setObjectName("cardFrame")
        step2_layout = QVBoxLayout(step2_card)
        step2_layout.setContentsMargins(16, 14, 16, 14)
        step2_layout.setSpacing(10)

        step2_header = QLabel("BƯỚC 2: CHỌN GÓI DỊCH VỤ & THANH TOÁN")
        step2_header.setStyleSheet(
            "color: #38BDF8; font-weight: bold; font-size: 12px;"
        )
        step2_layout.addWidget(step2_header)

        # Row 1: Package selection
        self.cbo_package = QComboBox()
        self.cbo_package.setFixedHeight(36)
        self.cbo_package.setObjectName("packageSelector")
        self.cbo_package.currentIndexChanged.connect(self._update_total_amount)
        step2_layout.addWidget(
            self._create_field_widget(
                "Gói tập kích hoạt ngay (*):", self.cbo_package
            )
        )

        # Row 2: Payment method (1) + Total Amount (1)
        row_pay_layout = QHBoxLayout()
        row_pay_layout.setSpacing(12)

        self.cbo_payment_method = QComboBox()
        self.cbo_payment_method.setFixedHeight(36)
        self.cbo_payment_method.addItem(
            "Tiền mặt (CASH)", PaymentMethod.CASH.value
        )
        self.cbo_payment_method.addItem(
            "Chuyển khoản VietQR", PaymentMethod.VIETQR.value
        )
        row_pay_layout.addWidget(
            self._create_field_widget(
                "Hình thức thanh toán:", self.cbo_payment_method
            ),
            1,
        )

        self.txt_total_amount = QLineEdit()
        self.txt_total_amount.setFixedHeight(36)
        self.txt_total_amount.setReadOnly(True)
        self.txt_total_amount.setStyleSheet(
            "font-weight: bold; color: #38BDF8; font-size: 14px; "
            "background-color: #0F172A;"
        )
        row_pay_layout.addWidget(
            self._create_field_widget(
                "Tổng tiền thu (VNĐ):", self.txt_total_amount
            ),
            1,
        )
        step2_layout.addLayout(row_pay_layout)

        main_layout.addWidget(step2_card)

        # Backward-compatible radio adapters
        self.rb_cash = _PaymentMethodRadioAdapter(
            self.cbo_payment_method, PaymentMethod.CASH.value
        )
        self.rb_vietqr = _PaymentMethodRadioAdapter(
            self.cbo_payment_method, PaymentMethod.VIETQR.value
        )

        # Status / Validation message
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(
            "color: #EF4444; font-size: 12px; font-weight: 500;"
        )
        self.status_label.hide()
        main_layout.addWidget(self.status_label)

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.clicked.connect(self.reject)

        self.submit_button = QPushButton("✓ Hoàn tất đăng ký")
        self.submit_button.setFixedHeight(40)
        self.submit_button.setProperty("primary", True)
        self.submit_button.clicked.connect(self.save_member)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.submit_button)
        main_layout.addLayout(button_layout)

        # Load data & focus
        self._load_active_plans()
        self.txt_name.returnPressed.connect(self.save_member)
        self.txt_phone.returnPressed.connect(self.save_member)
        self.txt_email.returnPressed.connect(self.save_member)
        self.txt_code.returnPressed.connect(self.save_member)
        self.txt_password.returnPressed.connect(self.save_member)
        QTimer.singleShot(0, self.txt_name.setFocus)

    def _create_input_field(
        self,
        placeholder: str,
        field_key: str,
        max_length: Optional[int] = None,
        is_password: bool = False,
    ) -> QLineEdit:
        field = QLineEdit()
        field.setFixedHeight(36)
        field.setPlaceholderText(placeholder)
        field.setObjectName(f"registration_{field_key}")
        if max_length:
            field.setMaxLength(max_length)
        if is_password:
            field.setEchoMode(QLineEdit.EchoMode.Password)

        error = QLabel()
        error.setProperty("error", True)
        error.setStyleSheet("color: #F87171; font-size: 11px;")
        error.hide()

        self._fields[field_key] = field
        self._errors[field_key] = error
        return field

    def _create_field_widget(
        self,
        label_text: str,
        field: QWidget,
        field_key: Optional[str] = None,
    ) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        layout.addWidget(lbl)
        layout.addWidget(field)

        if field_key and field_key in self._errors:
            layout.addWidget(self._errors[field_key])

        return container

    def _update_total_amount(self) -> None:
        plan_id = self.cbo_package.currentData()
        plan = self._plans_by_id.get(plan_id)
        if plan:
            self.txt_total_amount.setText(f"{plan.price:,.0f} đ")
        else:
            self.txt_total_amount.clear()

    def _load_active_plans(self) -> None:
        try:
            plans = self.member_service.plan_repo.get_active_plans()
        except DatabaseTransactionException as err:
            self._show_status(str(err))
            self.submit_button.setEnabled(False)
            return

        self._plans_by_id.clear()
        self.cbo_package.clear()
        for plan in plans:
            self._plans_by_id[plan.plan_id] = plan
            self.cbo_package.addItem(
                f"{plan.name} - {plan.price:,.0f} đ", plan.plan_id
            )

        if self.preferred_plan_id:
            selected_index = self.cbo_package.findData(self.preferred_plan_id)
            if selected_index >= 0:
                self.cbo_package.setCurrentIndex(selected_index)

        self._update_total_amount()

        if not plans:
            self._show_status("Hiện không có gói tập nào đang mở bán.")
            self.submit_button.setEnabled(False)

    def _clear_errors(self) -> None:
        for field_key, field in self._fields.items():
            field.setProperty("invalid", False)
            field.style().unpolish(field)
            field.style().polish(field)
            self._errors[field_key].clear()
            self._errors[field_key].hide()
        self.status_label.clear()
        self.status_label.hide()

    def _set_field_error(self, field_key: str, message: str) -> None:
        field = self._fields.get(field_key)
        error = self._errors.get(field_key)
        if field is None or error is None:
            self._show_status(message)
            return
        field.setProperty("invalid", True)
        field.style().unpolish(field)
        field.style().polish(field)
        error.setText(message)
        error.show()
        field.setFocus()

    def _show_status(self, message: str) -> None:
        self.status_label.setText(message)
        self.status_label.show()

    def _set_busy(self, busy: bool) -> None:
        self._is_submitting = busy
        self.submit_button.setEnabled(not busy)
        self.cancel_button.setEnabled(not busy)
        self.txt_code.setEnabled(not busy)
        self.cbo_gender.setEnabled(not busy)
        self.txt_name.setEnabled(not busy)
        self.txt_phone.setEnabled(not busy)
        self.txt_email.setEnabled(not busy)
        self.txt_password.setEnabled(not busy)
        self.cbo_package.setEnabled(not busy)
        self.cbo_payment_method.setEnabled(not busy)
        if busy:
            self.submit_button.setText("Đang lưu dữ liệu…")
        else:
            self.submit_button.setText("✓ Hoàn tất đăng ký")

    def save_member(self) -> None:
        if self._is_submitting:
            return
        self._clear_errors()

        name = self.txt_name.text().strip()
        phone = self.txt_phone.text().strip()
        email = self.txt_email.text().strip() or None
        username = self.txt_code.text().strip() or None
        password = self.txt_password.text().strip() or None
        plan_id = self.cbo_package.currentData()
        payment_method = (
            self.cbo_payment_method.currentData() or PaymentMethod.CASH.value
        )

        # Fast client-side validations matching WinUI RegisterMemberWizard
        if username:
            if len(username) > 10:
                self._set_field_error(
                    "username", "Mã hội viên không được vượt quá 10 ký tự!"
                )
                return
            if not re.match(r"^[A-Za-z0-9_-]+$", username):
                self._set_field_error(
                    "username",
                    "Mã hội viên chỉ được chứa chữ cái, chữ số, "
                    "gạch ngang (-) hoặc gạch dưới (_)!",
                )
                return

        if not name:
            self._set_field_error(
                "full_name", "Họ và tên hội viên không được để trống!"
            )
            return

        if not phone or not re.match(r"^0\d{9}$", phone):
            self._set_field_error(
                "phone",
                "Số điện thoại không hợp lệ. "
                "Vui lòng nhập đúng 10 chữ số (bắt đầu bằng 0)!",
            )
            return

        if not password or len(password) < 6:
            self._set_field_error(
                "password", "Mật khẩu đăng nhập phải có ít nhất 6 ký tự!"
            )
            return

        if not plan_id:
            self._show_status("Vui lòng chọn một gói dịch vụ để kích hoạt!")
            self.cbo_package.setFocus()
            return

        self._set_busy(True)
        try:
            plan = self.member_service.validate_registration(
                full_name=name,
                phone=phone,
                plan_id=plan_id,
                payment_method=payment_method,
                email=email,
                username=username,
                password=password,
            )
        except DuplicateUserException as err:
            self._set_busy(False)
            if "Số điện thoại" in str(err):
                self._set_field_error("phone", str(err))
            else:
                self._set_field_error("username", str(err))
            return
        except PackageNotFoundException as err:
            self._set_busy(False)
            self._show_status(str(err))
            return
        except ValidationException as err:
            self._set_busy(False)
            field_key = (
                err.field_name if err.field_name in self._fields else None
            )
            if field_key:
                self._set_field_error(field_key, str(err))
            else:
                self._show_status(str(err))
            return
        except DatabaseTransactionException as err:
            self._set_busy(False)
            self._show_status(str(err))
            return

        if payment_method == PaymentMethod.VIETQR.value:
            self._start_vietqr_payment(plan)
        else:
            self._persist_registration(plan, payment_method, None)

    def _persist_registration(
        self,
        plan: PackagePlan,
        payment_method: str,
        invoice_code: Optional[str],
    ) -> None:
        gender = (
            1
            if self.cbo_gender.currentIndex() == 0
            else (0 if self.cbo_gender.currentIndex() == 1 else None)
        )
        try:
            result = self.member_service.register_member_with_package(
                full_name=self.txt_name.text().strip(),
                phone=self.txt_phone.text().strip(),
                plan_id=plan.plan_id,
                payment_method=payment_method,
                email=self.txt_email.text().strip() or None,
                invoice_code=invoice_code,
                username=self.txt_code.text().strip() or None,
                password=self.txt_password.text().strip() or None,
                gender=gender,
            )
        except DuplicateUserException as err:
            self._set_busy(False)
            if "Số điện thoại" in str(err):
                self._set_field_error("phone", str(err))
            else:
                self._set_field_error("username", str(err))
        except PackageNotFoundException as err:
            self._set_busy(False)
            self._show_status(str(err))
        except ValidationException as err:
            self._set_busy(False)
            field_key = (
                err.field_name if err.field_name in self._fields else None
            )
            if field_key:
                self._set_field_error(field_key, str(err))
            else:
                self._show_status(str(err))
        except DatabaseTransactionException as err:
            self._set_busy(False)
            self._show_status(str(err))
        else:
            self._set_busy(False)
            self._show_success(result, plan)

    def _start_vietqr_payment(self, plan: PackagePlan) -> None:
        invoice_code = self.member_service.generate_invoice_code()
        self._set_busy(True)
        self.status_label.setText("Đang tạo mã VietQR…")
        self.status_label.show()

        task = _QrGenerationTask(
            self.vietqr_service, int(plan.price), invoice_code
        )
        task.signals.finished.connect(
            lambda success, payload: self._on_qr_ready(
                success, payload, plan, invoice_code
            )
        )
        self._qr_task = task
        QThreadPool.globalInstance().start(task)

    def _on_qr_ready(
        self,
        success: bool,
        payload: str,
        plan: PackagePlan,
        invoice_code: str,
    ) -> None:
        self._qr_task = None
        if not success:
            self._set_busy(False)
            self._show_status(payload)
            return

        try:
            payment_dialog = VietQrPaymentDialog(
                int(plan.price),
                invoice_code,
                plan.name,
                self,
                qr_data_url=payload,
            )
        except ValueError as err:
            self._set_busy(False)
            self._show_status(f"Không thể hiển thị mã QR: {err}")
            return
        if payment_dialog.exec() == QDialog.DialogCode.Accepted:
            self.status_label.setText(
                "Đã xác nhận nhận tiền. Đang lưu đăng ký..."
            )
            self.status_label.show()
            self._persist_registration(
                plan, PaymentMethod.VIETQR.value, invoice_code
            )
        else:
            self._set_busy(False)
            self.status_label.clear()
            self.status_label.hide()

    def _show_success(self, result: Dict[str, Any], plan: PackagePlan) -> None:
        member = result["user"]
        success_dialog = QDialog(self)
        success_dialog.setWindowTitle("Đăng ký thành công")
        success_dialog.setFixedSize(360, 430)
        layout = QVBoxLayout(success_dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("ĐĂNG KÝ THÀNH CÔNG")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        detail = QLabel(
            f"{member.full_name}\n"
            f"Mã hội viên: {member.username}\n"
            f"Gói tập: {plan.name}"
        )
        detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        detail.setWordWrap(True)
        layout.addWidget(detail)
        layout.addWidget(
            QRWidget(
                data=str(result["qr_code"]),
                size=200,
                caption="Mã QR điểm danh hội viên",
            ),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        close_button = QPushButton("Hoàn tất")
        close_button.setProperty("primary", True)
        close_button.clicked.connect(success_dialog.accept)
        layout.addWidget(close_button)
        success_dialog.exec()
        self.accept()

    def reject(self) -> None:
        if self._is_submitting:
            return
        super().reject()

    def closeEvent(self, event) -> None:
        if self._is_submitting:
            event.ignore()
            return
        super().closeEvent(event)
