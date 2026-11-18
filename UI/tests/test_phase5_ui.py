"""Headless tests for the Phase 5 desktop workflows."""

import base64
from datetime import date
from types import SimpleNamespace

import pytest
from PyQt6.QtCore import QBuffer, QIODevice, Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QDialog, QLabel

from components.qr_widget import QRWidget
from constants import CheckInMethod, CheckInStatus, PaymentMethod
from desktop_portal.dialogs import register_member_dialog as register_module
from desktop_portal.dialogs.register_member_dialog import RegisterMemberDialog
from desktop_portal.views.checkin_counter_page import CheckInCounterPage
from desktop_portal.views.members_page import MembersPage
from desktop_portal.views.pos_billing_page import PosBillingPage
from exceptions import CheckInDeniedException
from models.package_plan import PackagePlan
from web_portal.member_portal_window import MemberPortalWindow
from web_portal.pt_portal_window import PtPortalWindow


class _FakePlanRepository:
    def __init__(self, plan):
        self.plan = plan

    def get_active_plans(self):
        return [self.plan]


class _FakeMemberService:
    def __init__(self, plan):
        self.plan_repo = _FakePlanRepository(plan)
        self.plan = plan
        self.registrations = []
        self.validations = []

    def validate_registration(self, *args, **kwargs):
        self.validations.append((args, kwargs))
        return self.plan

    def generate_invoice_code(self):
        return "HD-TEST-100"

    def register_member_with_package(self, **kwargs):
        self.registrations.append(kwargs)
        return {
            "user": SimpleNamespace(full_name="Nguyen A", username="HV000001"),
            "qr_code": "GYM-QR-HV000001",
        }


def _plan():
    return PackagePlan(
        plan_id="PKG01",
        name="Gói tháng",
        price=500000,
        duration_days=30,
        max_check_in_sessions=20,
    )


def _fill_registration(dialog):
    dialog.txt_name.setText("Nguyen A")
    dialog.txt_phone.setText("0912345678")


def test_qr_widget_displays_data_url_image():
    source_image = QImage(8, 8, QImage.Format.Format_RGB32)
    source_image.fill(Qt.GlobalColor.white)
    buffer = QBuffer()
    assert buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    assert source_image.save(buffer, "PNG")
    data_url = "data:image/png;base64," + base64.b64encode(
        bytes(buffer.data())
    ).decode("ascii")

    widget = QRWidget(data=data_url, size=100)

    assert widget.qr_label.pixmap() is not None
    assert not widget.qr_label.pixmap().isNull()


def test_qr_widget_rejects_malformed_data_url():
    with pytest.raises(ValueError, match="Base64"):
        QRWidget(data="data:image/png;base64,not base64!", size=100)


def test_vietqr_registration_saves_only_after_confirmation(
    monkeypatch,
):
    plan = _plan()
    service = _FakeMemberService(plan)
    dialog = RegisterMemberDialog(member_service=service)
    _fill_registration(dialog)
    dialog._set_busy(True)

    def skip_success(result, selected_plan):
        assert result["qr_code"] == "GYM-QR-HV000001"
        assert selected_plan is plan

    dialog._show_success = skip_success

    class _ConfirmedPaymentDialog:
        def __init__(
            self,
            amount,
            order_code,
            package_name,
            parent=None,
            qr_data_url=None,
        ):
            assert amount == 500000
            assert order_code == "HD-TEST-100"
            assert package_name == plan.name
            assert parent is dialog
            assert qr_data_url.startswith("data:image/")

        def exec(self):
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr(
        register_module, "VietQrPaymentDialog", _ConfirmedPaymentDialog
    )
    dialog._on_qr_ready(
        True, "data:image/png;base64,cGF5bWVudA==", plan, "HD-TEST-100"
    )

    assert len(service.registrations) == 1
    assert (
        service.registrations[0]["payment_method"]
        == PaymentMethod.VIETQR.value
    )
    assert service.registrations[0]["invoice_code"] == "HD-TEST-100"


def test_cancelled_vietqr_payment_does_not_register(monkeypatch):
    plan = _plan()
    service = _FakeMemberService(plan)
    dialog = RegisterMemberDialog(member_service=service)
    _fill_registration(dialog)
    dialog._set_busy(True)

    class _CancelledPaymentDialog:
        def __init__(
            self,
            amount,
            order_code,
            package_name,
            parent=None,
            qr_data_url=None,
        ):
            assert amount == 500000
            assert order_code == "HD-TEST-100"
            assert package_name == plan.name
            assert parent is dialog
            assert qr_data_url.startswith("data:image/")

        def exec(self):
            return QDialog.DialogCode.Rejected

    monkeypatch.setattr(
        register_module, "VietQrPaymentDialog", _CancelledPaymentDialog
    )
    dialog._on_qr_ready(
        True, "data:image/png;base64,cGF5bWVudA==", plan, "HD-TEST-100"
    )

    assert service.registrations == []
    assert not dialog._is_submitting


def test_cash_registration_uses_live_service():
    service = _FakeMemberService(_plan())
    dialog = RegisterMemberDialog(member_service=service)
    _fill_registration(dialog)

    def skip_success(result, selected_plan):
        assert result["qr_code"] == "GYM-QR-HV000001"
        assert selected_plan is service.plan

    dialog._show_success = skip_success

    dialog.save_member()

    assert len(service.registrations) == 1
    assert (
        service.registrations[0]["payment_method"]
        == PaymentMethod.CASH.value
    )
    assert service.registrations[0]["invoice_code"] is None


def test_register_member_wizard_2step_fields_and_validation():
    plan = _plan()
    service = _FakeMemberService(plan)
    dialog = RegisterMemberDialog(member_service=service)

    # Check 2-Step fields exist and initialized
    assert dialog.txt_code.placeholderText().startswith("VD: MBR-0010")
    assert dialog.cbo_gender.count() == 3
    assert dialog.cbo_gender.currentText() == "Nam"
    assert dialog.txt_password.text() == "123456"
    assert "500,000" in dialog.txt_total_amount.text()

    # Fill invalid short password
    dialog.txt_name.setText("Le Van B")
    dialog.txt_phone.setText("0908889999")
    dialog.txt_password.setText("123")
    dialog.save_member()
    assert len(service.registrations) == 0
    assert not dialog._errors["password"].isHidden()
    assert "ít nhất 6 ký tự" in dialog._errors["password"].text()

    # Fill valid data with custom member code
    dialog.txt_password.setText("securePass123")
    dialog.txt_code.setText("MBR-0099")
    dialog.cbo_gender.setCurrentIndex(1)  # Nu

    def dummy_success(result, selected_plan):
        pass

    dialog._show_success = dummy_success
    dialog.save_member()

    assert len(service.registrations) == 1
    reg = service.registrations[0]
    assert reg["full_name"] == "Le Van B"
    assert reg["phone"] == "0908889999"
    assert reg["username"] == "MBR-0099"
    assert reg["password"] == "securePass123"
    assert reg["gender"] == 0


class _FakeCheckInService:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = []

    def process_checkin(self, key, method):
        self.calls.append((key, method))
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


class _FakeCheckInRepository:
    def __init__(self, logs=None):
        self.logs = logs or []

    def get_today_logs(self):
        return self.logs


class _FakeMemberSummaryRepository:
    def get_member_summaries(self):
        return [
            {
                "username": "HV000001",
                "full_name": "Nguyen A",
                "phone": "0912345678",
                "email": "a@example.com",
                "user_status": "ACTIVE",
                "subscription_id": "SUB0001",
                "qr_code": "GYM-QR-HV000001",
                "start_date": date.today(),
                "end_date": date.today(),
                "subscription_status": "ACTIVE",
                "remaining_check_in_sessions": 4,
                "remaining_pt_sessions": 2,
                "assigned_pt_id": None,
                "plan_id": "PKG01",
                "plan_name": "Gói tháng",
            }
        ]


class _FakePackageRepository:
    def __init__(self, plans):
        self.plans = plans

    def get_active_plans(self):
        return self.plans


def test_checkin_page_uses_manual_service_and_refreshes_logs():
    checkin_service = _FakeCheckInService(
        {
            "check_in_id": "CK000001",
            "check_in_at": date.today(),
            "username": "HV000001",
            "full_name": "Nguyen A",
            "plan_name": "Gói tháng",
            "end_date": date.today(),
            "remaining_sessions": 19,
        }
    )
    logs = [
        {
            "check_in_id": "CK000001",
            "check_in_at": date.today(),
            "username": "HV000001",
            "full_name": "Nguyen A",
            "status": CheckInStatus.SUCCESS.value,
        }
    ]
    page = CheckInCounterPage(
        checkin_service=checkin_service,
        check_in_repo=_FakeCheckInRepository(logs),
    )
    page.txt_search.setText("0912345678")
    page.do_checkin()

    assert checkin_service.calls == [
        ("0912345678", CheckInMethod.MANUAL.value)
    ]
    assert page.table.rowCount() == 1
    assert page.status_title.text() == "ĐIỂM DANH THÀNH CÔNG"


def test_checkin_without_subscription_does_not_add_persisted_log():
    service = _FakeCheckInService(
        CheckInDeniedException(
            "Không tìm thấy thẻ hoặc gói tập hợp lệ.",
            username="0912345678",
        )
    )
    page = CheckInCounterPage(
        checkin_service=service,
        check_in_repo=_FakeCheckInRepository(),
    )
    page.txt_search.setText("0912345678")
    page.do_checkin()

    assert page.table.rowCount() == 0
    assert page.status_title.text() == "ĐIỂM DANH BỊ TỪ CHỐI"


def test_members_page_maps_live_summary_to_active_member():
    page = MembersPage(
        subscription_repo=_FakeMemberSummaryRepository()
    )

    assert page.table.rowCount() == 1
    assert page._members[0]["status"] == "Đang hoạt động"
    assert page._members[0]["qr_code"] == "GYM-QR-HV000001"


def test_package_catalog_uses_repository_plans():
    plan = _plan()
    page = PosBillingPage(package_repo=_FakePackageRepository([plan]))

    assert page._plans == [plan]
    assert any(
        label.text() == plan.name
        for label in page.findChildren(QLabel)
    )


def test_member_portal_tabs_and_workout_history():
    window = MemberPortalWindow()
    assert window.tabs.count() == 4
    tab_titles = [window.tabs.tabText(i) for i in range(4)]
    assert tab_titles == [
        "💳 Thẻ Điện Tử & Hồ Sơ",
        "📅 Đặt Lịch Huấn Luyện Viên",
        "📈 Chỉ Số Cơ Thể InBody",
        "🕒 Nhật Ký Tập Luyện",
    ]

    # Verify initial state of history table
    assert window.history_table.columnCount() == 4
    total_events = len(window.workout_events)
    assert window.history_table.rowCount() == total_events

    # Test CHECKIN filter
    window.apply_history_filter("CHECKIN")
    checkin_count = sum(
        1 for e in window.workout_events if e["type"] == "CHECKIN"
    )
    assert window.history_table.rowCount() == checkin_count

    # Test PT filter
    window.apply_history_filter("PT")
    pt_count = sum(1 for e in window.workout_events if e["type"] == "PT")
    assert window.history_table.rowCount() == pt_count

    # Reset to ALL
    window.apply_history_filter("ALL")
    assert window.history_table.rowCount() == total_events


def test_pt_portal_tabs_and_availability_grid():
    window = PtPortalWindow()
    assert window.tabs.count() == 4
    tab_titles = [window.tabs.tabText(i) for i in range(4)]
    assert tab_titles == [
        "📅 Lịch Dạy & Buổi Hẹn",
        "👥 Danh Sách Học Viên",
        "⏱ Đăng Ký Ca Rảnh",
        "👤 Hồ Sơ & Đánh Giá",
    ]

    # Tab 1 Schedule layout verification (with Ngày column)
    assert window.schedule_table.columnCount() == 6
    assert window.schedule_table.columnWidth(5) == 150

    # Tab 2 Students layout & search verification
    assert window.students_table.columnCount() == 5
    assert window.students_table.columnWidth(4) == 160
    window.txt_student_search.setText("Hoàng Nam")
    assert window.students_table.rowCount() == 1
    window.txt_student_search.setText("")
    assert window.students_table.rowCount() > 1

    # Tab 3 Availability grid verification
    assert len(window.day_buttons) == 7
    assert window.avail_table.columnCount() == 4
    assert window.avail_table.columnWidth(3) == 140

    # Test adding a slot
    initial_count = len(window.availability_slots)
    window.cbo_start_time.setCurrentText("14:00")
    window.cbo_end_time.setCurrentText("15:00")
    window.add_avail_slot()
    assert len(window.availability_slots) == initial_count + 1

    # Test removing slot
    added_slot = window.availability_slots[-1]
    window.remove_avail_slot(added_slot)
    assert len(window.availability_slots) == initial_count
