# QUY CHUẨN GIAO DIỆN THỊ GIÁC PYQT6 (PYTHON UI RULES)
## ÁP DỤNG CHO 2 TÍNH NĂNG: ĐĂNG KÝ HỘI VIÊN KÈM GÓI TẬP & ĐIỂM DANH HỘI VIÊN
**Tài liệu tham chiếu:** [`UI/task.md`](../UI/task.md) | [`doc/ref_ui_rules.md`](ref_ui_rules.md) | [`UI/styles/color_tokens.py`](../UI/styles/color_tokens.py)  
**Nền tảng:** Python 3.10.11 • PyQt6 Desktop • 100% Dark Mode • Tương phản WCAG 2.2 AA • Athletic Modernism

---

## MỤC TIÊU & TRIẾT LÝ THỊ GIÁC CỐT LÕI

Tài liệu này quy định toàn bộ **Quy chuẩn Giao diện Thị giác (UI - Visual User Interface)** cho ứng dụng Desktop PyQt6 của Ban quản trị / Lễ tân, tập trung vào 2 màn hình tác nghiệp trọng tâm:
1. **Hộp thoại Đăng ký hội viên kèm gói tập** ([`RegisterMemberDialog`](../UI/desktop_portal/dialogs/register_member_dialog.py) - `UC02.1` & `UC05.1`).
2. **Quầy Điểm danh hội viên** ([`CheckInCounterPage`](../UI/desktop_portal/views/checkin_counter_page.py) - `UC03.1` & `UC03.2`).

> [!IMPORTANT]
> **Triết lý Thiết kế Thị giác Bắt buộc:**
> * **100% Dark Mode (Athletic Dark Palette):** Nền tối thể thao sâu lắng, triệt tiêu ánh sáng xanh chói tại quầy làm việc, đạt chuẩn tương phản WCAG 2.2 AA ($\ge 4.5:1$ cho chữ, $\ge 3:1$ cho viền tương tác).
> * **Tuyệt đối KHÔNG hiển thị mã kỹ thuật `(UC...)`:** Không để lộ mã Use Case kỹ thuật như `UC02.1`, `UC03`, `UC5.1` lên bất kỳ tiêu đề, nút bấm, nhãn form hay hộp thoại nào.
> * **Không âm thanh phiền toái & Không nhấp nháy:** Tuyệt đối không dùng hiệu ứng chớp tắt, viền giật, không phát tiếng bíp còi gây ồn ào tại quầy gym.
> * **KISS trong Bố cục Giao diện (Flat Layout Hierarchy):** Tránh lồng ghép quá nhiều cấp `QFrame` và `QLayout` không cần thiết. Giữ cấu trúc widget phẳng, sạch và trực quan.

---

## 1. HỆ THỐNG DESIGN TOKENS (ATHLETIC DARK PALETTE)

Mọi mã nguồn PyQt6 bắt buộc phải import và sử dụng trực tiếp các hằng số màu từ [`UI/styles/color_tokens.py`](../UI/styles/color_tokens.py). **Nghiêm cấm gõ trực tiếp mã màu Hex trong file giao diện.**

```python
# File: UI/styles/color_tokens.py
from styles.color_tokens import (
    CANVAS_BG, SURFACE_BASE, SURFACE_CARD, SURFACE_MODAL,
    BORDER_SUBTLE, BORDER_INTERACTIVE, BORDER_FOCUS,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY, TEXT_DISABLED,
    ACCENT_PRIMARY, ACCENT_HOVER, ACCENT_PRESSED, ACCENT_SUBTLE,
    STATUS_SUCCESS, STATUS_SUCCESS_BG, STATUS_SUCCESS_BORDER,
    STATUS_DANGER, STATUS_DANGER_BG, STATUS_DANGER_BORDER,
    STATUS_WARNING, STATUS_WARNING_BG, STATUS_WARNING_BORDER
)
```

### 1.1. Bảng Định Danh 6 Phân Tầng Màu Sắc

| Phân Tầng | Tên Token Python | Mã Hex / RGB | Ý Nghĩa Sử Dụng Trong 2 Tính Năng | Tỷ Lệ Tương Phản WCAG |
| :--- | :--- | :--- | :--- | :--- |
| **L0: Không Gian (Surfaces)** | `CANVAS_BG` | `#0A0F1D` | Nền gốc toàn bộ cửa sổ ứng dụng (Obsidian Deep Dark). | Nền gốc |
| | `SURFACE_BASE` | `#111827` | Nền sidebar điều hướng, nền tiêu đề cố định. | Phân tách không gian |
| | `SURFACE_CARD` | `#1E293B` | Nền khung camera, thẻ thông tin hội viên, nền bảng check-in. | Khối nội dung |
| | `SURFACE_MODAL` | `#162032` | Nền hộp thoại `RegisterMemberDialog`, popup mã QR. | Hộp thoại nổi |
| **L1: Đường Viền (Borders)** | `BORDER_SUBTLE` | `#334155` | Viền `1px solid` phân cách các card và phân vùng layout. | $\ge 3:1$ |
| | `BORDER_INTERACTIVE`| `#475569` | Viền ô `QLineEdit` nhập SĐT/CCCD ở trạng thái bình thường. | Trạng thái nghỉ |
| | `BORDER_FOCUS` | `#38BDF8` | Viền ô `QLineEdit` khi người dùng đang trỏ con trỏ chuột vào. | `:focus` |
| **L2: Kiểu Chữ (Text)** | `TEXT_PRIMARY` | `#F8FAFC` | Tiêu đề form, Họ tên hội viên check-in, Số tiền hóa đơn. | **14.8:1** (Rất cao) |
| | `TEXT_SECONDARY` | `#94A3B8` | Nhãn form (Họ tên, SĐT), Mã hội viên, Ngày hết hạn gói. | **5.2:1** (Đạt chuẩn AA) |
| | `TEXT_TERTIARY` | `#64748B` | Chữ mờ gợi ý (Placeholder trong ô nhập liệu). | Hướng dẫn mờ |
| | `TEXT_DISABLED` | `#475569` | Chữ của nút hoặc ô đang bị khóa (`setEnabled(False)`). | Trạng thái khóa |
| **L3: Điểm Nhấn (Accent)** | `ACCENT_PRIMARY` | `#0EA5E9` | Nút hành động chính (CTA): `"Xác nhận Đăng ký"`, `"Bật Camera"`. | Điểm nhấn chính |
| | `ACCENT_HOVER` | `#38BDF8` | Màu nút CTA khi người dùng di chuột lên trên. | Hover feedback |
| | `ACCENT_PRESSED` | `#0284C7` | Màu nút CTA khi người dùng click giữ chuột. | Active feedback |
| | `ACCENT_SUBTLE` | `rgba(14,165,233,0.15)` | Màu viền highlight thẻ gói tập đang được chọn. | Selection state |
| **L4: Trạng Thái (Status)** | `STATUS_SUCCESS` | `#4ADE80` | Chữ trạng thái thẻ: `HỢP LỆ`, `ĐANG HOẠT ĐỘNG`. | Thành công |
| | `STATUS_SUCCESS_BG` | `#064E3B` | Nền chip trạng thái `HỢP LỆ` tại quầy check-in. | Nền xanh lục đậm |
| | `STATUS_DANGER` | `#F87171` | Chữ trạng thái thẻ: `TỪ CHỐI`, `HẾT HẠN`, `ĐÃ HẾT LƯỢT`. | Thất bại / Lỗi |
| | `STATUS_DANGER_BG` | `#7F1D1D` | Nền chip trạng thái `TỪ CHỐI` tại quầy check-in. | Nền đỏ sẫm |

---

## 2. QUY CHUẨN KIỂU CHỮ & VI MÔ (TYPOGRAPHY & MICRO-TYPOGRAPHY)

### 2.1. Thang Kích Thước Chữ (Type Scale)

* **Display / Big Highlight (20px - 24px Bold):**
  * Tên hội viên tại màn hình kết quả điểm danh: `font-size: 22px; font-weight: bold; color: #F8FAFC;`
  * Số tiền thanh toán hóa đơn: `font-size: 20px; font-weight: bold; color: #0EA5E9;`
* **Heading 2 (16px - 18px Bold):**
  * Tiêu đề trang: `"QUẦY ĐIỂM DANH HỘI VIÊN"`, `"ĐĂNG KÝ HỘI VIÊN MỚI"`: `font-size: 18px; font-weight: bold;`
* **Body / Input Text (13px - 14px Regular):**
  * Nội dung các ô nhập liệu `QLineEdit`, văn bản bảng dữ liệu `QTableWidget`: `font-size: 13px;`
* **Caption / Status Badges (11px - 12px Bold):**
  * Nhãn chip trạng thái `HỢP LỆ`, `TỪ CHỐI`, nhãn phụ thời gian: `font-size: 11px; font-weight: bold;`

### 2.2. Quy Chuẩn Vi Mô Bắt Buộc (Micro-Typography Rules)

1. **Khoảng trắng không ngắt (Non-Breaking Space `\u00A0`):**
   * Giữa số lượng và đơn vị tiền tệ/thời gian **BẮT BUỘC** dùng `\u00A0` để chống rớt dòng đơn vị:
   * Ví dụ: `f"{amount:,.0f}\u00A0đ"`, `f"{days}\u00A0ngày"`, `f"{sessions}\u00A0buổi"`.
2. **Ký tự dấu ba chấm chuẩn (`\u2026` / `…`):**
   * Dùng `…` (`\u2026`) cho trạng thái chờ, nghiêm cấm gõ 3 dấu chấm liên tiếp `...`.
   * Ví dụ: `"Đang lưu dữ liệu…"`, `"Nhập SĐT hoặc Mã HV…"`.
3. **Chữ số đơn cách cho bảng dữ liệu (Tabular Numbers):**
   * Cột thời gian điểm danh (`10:45:12`) và cột số tiền phải được căn phải hoặc canh đều để các hàng số thẳng cột không rung lắc bố cục.
4. **Quy chuẩn Bo góc (Border Radius):**
   * Hộp thoại Dialog & Khối thẻ Card: `border-radius: 12px;`
   * Nút bấm (QPushButton) & Ô nhập liệu (QLineEdit): `border-radius: 8px;`
   * Chip trạng thái (Badge): `border-radius: 4px;` hoặc viên thuốc `border-radius: 12px;`

---

## 3. QUY TẮC PHONG CÁCH QT (QSS - QT STYLE SHEETS)

### 3.1. Phân Tách QSS Tập Trung
Toàn bộ stylesheet chung phải nằm trong [`UI/styles/dark_theme.qss`](../UI/styles/dark_theme.qss).  
Sử dụng Dynamic Property của Qt (`setProperty()`) thay vì nối chuỗi CSS cục bộ:

```python
# ĐÚNG: Sử dụng Dynamic Property chuẩn Qt
btn_submit = QPushButton("✓ Xác Nhận Đăng Ký")
btn_submit.setProperty("primary", True)
# File dark_theme.qss sẽ tự bắt QPushButton[primary="true"] để tô màu ACCENT_PRIMARY
```

```python
# SAI (CẤM): Nối chuỗi CSS cứng trong file giao diện
btn_submit.setStyleSheet("background-color: #0EA5E9; color: white; border-radius: 8px;")
```

### 3.2. Chống Lồng Ghép Layout Quá Mức (KISS Layout Principle)
Tránh việc lồng một `QVBoxLayout` chỉ chứa đúng một `QHBoxLayout` chứa tiếp một `QFrame`. Hãy cấu hình trực tiếp khoảng cách lề `setContentsMargins(16, 16, 16, 16)` và `setSpacing(12)` trên container cha.

---

## 4. QUY CHUẨN THỊ GIÁC CHI TIẾT CHO 2 TÍNH NĂNG

### 4.1. Tính Năng 1: Hộp Thoại Đăng Ký Hội Viên Kèm Gói (`RegisterMemberDialog`)

```text
┌─────────────────────────────────────────────────────────────┐
│ ĐĂNG KÝ HỘI VIÊN MỚI                                     [X]│
├─────────────────────────────────────────────────────────────┤
│ Họ và Tên Hội Viên (*):                                     │
│ [ Nguyễn Văn An                                           ] │
│                                                             │
│ Số Điện Thoại (*) (Dùng làm Tên đăng nhập):                │
│ [ 0988112233                                              ] │
│                                                             │
│ Số CCCD / Định Danh Cá Nhân:                                │
│ [ 001202009988                                            ] │
│                                                             │
│ Email Liên Hệ:                                              │
│ [ an.nguyen@gmail.com                                     ] │
│                                                             │
│ Gói Dịch Vụ Đăng Ký (*):                                    │
│ [ Gym Standard 3 Tháng — 1.200.000 đ                      ▼]│
│                                                             │
│ Phương Thức Thanh Toán:                                     │
│ (•) Tiền Mặt                    ( ) Chuyển Khoản VietQR     │
├─────────────────────────────────────────────────────────────┤
│ [ Hủy Bỏ ]                             [ ✓ Hoàn Tất Đăng Ký]│
└─────────────────────────────────────────────────────────────┘
```

* **Trường bắt buộc (*):** Gắn nhãn màu đỏ mờ hoặc ký hiệu `(*)`.
* **Phương thức thanh toán:** Chỉ hỗ trợ 2 hình thức: **Tiền Mặt** (`CASH`) và **Chuyển Khoản VietQR** (`VIETQR`). Tuyệt đối không dùng máy quẹt thẻ POS.
* **Hiển thị lỗi nội dòng:** Khi phát hiện ô nhập thiếu hoặc trùng SĐT, ô đó viền đỏ `border: 1px solid #DC2626;`, thông báo lỗi hiển thị ngay dưới ô nhập liệu bằng chữ màu `#F87171`.
* **Popup thành công kèm QR Widget:** Sau khi bấm đăng ký thành công, hiển thị modal thông báo kèm mã QR kích thước $200 \times 200\text{px}$ nền trắng, viền bo tròn sắc nét.

### 4.2. Tính Năng 2: Quầy Điểm Danh Hội Viên (`CheckInCounterPage`)

Bố cục phân bổ chuẩn tỷ lệ vàng **4 : 6**:
* **Cột trái (40%): Cổng Tiếp Nhận Điểm Danh**
  * Khung Webcam Camera (Chiều cao cố định 240px, viền đứt nét `2px dashed #334155`).
  * Nút `"Bật Camera"` (`ACCENT_PRIMARY`), khi bật chuyển thành `"Tắt Camera"` (`#DC2626`).
  * Khung tra cứu thủ công: Ô `QLineEdit` tìm kiếm to rõ, kèm nút `"Điểm Danh (Enter)"`.
* **Cột phải (60%): Bảng Kết Quả & Nhật Ký Ra Vào**
  * **Card Thẻ Kết Quả:**
    * Nếu HỢP LỆ: Viền xanh lục đậm `#059669`, Badge `HỢP LỆ` (`#4ADE80` trên nền `#064E3B`).
    * Nếu TỪ CHỐI: Viền đỏ sẫm `#DC2626`, Badge `TỪ CHỐI` (`#F87171` trên nền `#7F1D1D`), kèm dòng lý do chữ đỏ to rõ: `"Gói tập đã hết hạn"`.
  * **Bảng Nhật Ký Check-in Hôm Nay:**
    * Bảng `QTableWidget` 5 cột: `Thời Gian`, `Mã HV`, `Họ Tên Hội Viên`, `Phương Thức`, `Trạng Thái`.
    * Cột trạng thái: Chữ màu xanh `#4ADE80` cho lượt hợp lệ, màu đỏ `#F87171` cho lượt từ chối.
    * Ẩn thanh tiêu đề dòng dọc (`verticalHeader().setVisible(False)`), dòng so le màu nhẹ để dễ quét mắt.
