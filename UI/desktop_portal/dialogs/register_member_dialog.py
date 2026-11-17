"""Dialog for registering a member with a live package plan."""

from __future__ import annotations

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
    QButtonGroup,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
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
        self._fields: Dict[str, QLineEdit] = {}
        self._errors: Dict[str, QLabel] = {}

        self.setWindowTitle("Đăng ký hội viên mới")
        self.setFixedSize(560, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("ĐĂNG KÝ HỘI VIÊN MỚI")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        form_frame = QFrame()
        form_frame.setObjectName("cardFrame")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setVerticalSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.txt_name = self._add_text_field(
            form_layout, "Họ và tên (*):", "Ví dụ: Nguyễn Văn An", "full_name"
        )
        self.txt_phone = self._add_text_field(
            form_layout,
            "Số điện thoại (*):",
            "10 chữ số, ví dụ 0988112233",
            "phone",
        )
        self.txt_email = self._add_text_field(
            form_layout, "Email:", "Không bắt buộc", "email"
        )

        self.cbo_package = QComboBox()
        self.cbo_package.setObjectName("packageSelector")
        form_layout.addRow("Gói dịch vụ (*):", self.cbo_package)

        payment_row = QHBoxLayout()
        self.payment_group = QButtonGroup(self)
        self.rb_cash = QRadioButton("Tiền mặt")
        self.rb_cash.setChecked(True)
        self.rb_vietqr = QRadioButton("Chuyển khoản VietQR")
        self.payment_group.addButton(self.rb_cash)
        self.payment_group.addButton(self.rb_vietqr)
        payment_row.addWidget(self.rb_cash)
        payment_row.addWidget(self.rb_vietqr)
        form_layout.addRow("Phương thức thanh toán:", payment_row)
        layout.addWidget(form_frame)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        layout.addWidget(self.status_label)

        layout.addStretch()
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.clicked.connect(self.reject)
        self.submit_button = QPushButton("✓ Hoàn tất đăng ký")
        self.submit_button.setProperty("primary", True)
        self.submit_button.clicked.connect(self.save_member)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.submit_button)
        layout.addLayout(button_layout)

        self._load_active_plans()
        self.txt_email.returnPressed.connect(self.save_member)
        QTimer.singleShot(0, self.txt_name.setFocus)

    def _add_text_field(
        self,
        form_layout: QFormLayout,
        label: str,
        placeholder: str,
        field_key: str,
    ) -> QLineEdit:
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setObjectName(f"registration_{field_key}")
        error = QLabel()
        error.setProperty("error", True)
        error.hide()
        wrapper = QVBoxLayout()
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.setSpacing(3)
        wrapper.addWidget(field)
        wrapper.addWidget(error)
        form_layout.addRow(label, wrapper)
        self._fields[field_key] = field
        self._errors[field_key] = error
        return field

    def _load_active_plans(self) -> None:
        try:
            plans = self.member_service.plan_repo.get_active_plans()
        except DatabaseTransactionException as err:
            self._show_status(str(err))
            self.submit_button.setEnabled(False)
            return

        for plan in plans:
            self.cbo_package.addItem(
                f"{plan.name} - {plan.price:,.0f} đ", plan.plan_id
            )
        if self.preferred_plan_id:
            selected_index = self.cbo_package.findData(self.preferred_plan_id)
            if selected_index >= 0:
                self.cbo_package.setCurrentIndex(selected_index)
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
        self.txt_name.setEnabled(not busy)
        self.txt_phone.setEnabled(not busy)
        self.txt_email.setEnabled(not busy)
        self.cbo_package.setEnabled(not busy)
        self.rb_cash.setEnabled(not busy)
        self.rb_vietqr.setEnabled(not busy)
        if busy:
            self.submit_button.setText("Đang lưu dữ liệu…")
        else:
            self.submit_button.setText("✓ Hoàn tất đăng ký")

    def save_member(self) -> None:
        if self._is_submitting:
            return
        self._clear_errors()

        name = self.txt_name.text()
        phone = self.txt_phone.text()
        email = self.txt_email.text() or None
        plan_id = self.cbo_package.currentData()
        if not plan_id:
            self._show_status("Vui lòng chọn gói dịch vụ.")
            self.cbo_package.setFocus()
            return

        self._set_busy(True)
        payment_method = (
            PaymentMethod.VIETQR.value
            if self.rb_vietqr.isChecked()
            else PaymentMethod.CASH.value
        )
        try:
            plan = self.member_service.validate_registration(
                name,
                phone,
                plan_id,
                payment_method=payment_method,
                email=email,
            )
        except DuplicateUserException as err:
            self._set_busy(False)
            self._set_field_error("phone", str(err))
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
        try:
            result = self.member_service.register_member_with_package(
                full_name=self.txt_name.text(),
                phone=self.txt_phone.text(),
                plan_id=plan.plan_id,
                payment_method=payment_method,
                email=self.txt_email.text() or None,
                invoice_code=invoice_code,
            )
        except DuplicateUserException as err:
            self._set_busy(False)
            self._set_field_error("phone", str(err))
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
