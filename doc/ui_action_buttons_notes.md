# Ghi Chú Đối Chiếu Nút Thao Tác Giao Diện Desktop (PyQt6 vs WinUI 3)

Tài liệu này tổng hợp chi tiết kết quả rà soát, đối chiếu và chuẩn hóa các nút thao tác giữa bản thiết kế mẫu WinUI 3 (`ui_ref/Desktop/Views/`, `ui_ref/Desktop/Dialogs/`) và ứng dụng desktop PyQt6 (`UI/desktop_portal/`).

---

## 1. Bảng Tổng Hợp Ma Trận Nút Thao Tác

| Màn Hình | Tên Nút | Kiểu Giao Diện (QSS) | Trạng Thái Xử Lý | Dialog Tham Chiếu WinUI 3 | Ghi Chú Nghiệp Vụ & Bố Cục |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Quản lý hội viên** (`MembersPage`) | `Sửa` | `tableAction` | Giao diện + Thông báo | `UserEditDialog.xaml` | Cho phép sửa họ tên, số điện thoại, email liên hệ của hội viên. |
| | `Bảo lưu` | `tableAction` (`warning`) | Giao diện + Thông báo | `FreezeSubscriptionDialog.xaml` | Tiếp nhận ngày bắt đầu nghỉ, ngày tập lại, lý do bảo lưu; gia hạn hạn gói. |
| | `Hủy gói` | `tableAction` (`danger`) | Giao diện + Xác nhận | `CancelSubscriptionDialog.xaml` | Cảnh báo thu hồi quyền lợi tập; yêu cầu xác nhận trước khi hủy. |
| | *(Mở chi tiết)* | *(Double-click dòng)* | Hoạt động đầy đủ | `MemberDetailDialog.xaml` | Đã bỏ nút "Chi tiết" để nhường không gian cho 3 nút trên; double-click vào dòng để mở chi tiết thẻ & QR. |
| **Quản lý nhân sự** (`SettingsPage`) | `Sửa` | `tableAction` | Giao diện + Thông báo | `UserEditDialog.xaml` | Chỉnh sửa thông tin tài khoản và điều chỉnh vai trò truy cập hệ thống (Admin / PT). |
| | `Khóa TK` / `Mở Khóa` | `tableAction` (`danger` / `success`) | Hoạt động đầy đủ | `SettingsPage.xaml` | Tự động đổi nhãn và màu theo trạng thái tài khoản (`Hoạt động` <-> `Tạm khóa`). |
| | `Tạo Tài Khoản` | `primary` (44px) | Hoạt động đầy đủ | `SettingsPage.xaml` | Form thêm nhân sự mới với đủ 5 trường thông tin và vai trò. |
| | `Tải Lại` | Segmented (36px) | Hoạt động đầy đủ | `SettingsPage.xaml` | Nạp lại danh sách tài khoản vận hành. |
| **Hóa đơn & Phiếu thu** (`InvoiceHistoryPage`) | `In K80` | `tableAction` | Hoạt động đầy đủ | `ReceiptPreviewDialog.xaml` | Gửi lệnh in phiếu thu nhiệt K80 chuẩn quầy thu ngân. |
| | `Hoàn Tiền` | `tableAction` (`warning`) | Giao diện + Xác nhận | `RefundInvoiceDialog.xaml` | Xử lý hoàn tiền, chuyển trạng thái hóa đơn sang `REFUNDED` và thu hồi gói tập. |
| | `Làm mới` | Segmented (40px) | Hoạt động đầy đủ | `InvoiceHistoryPage.xaml` | Làm mới danh sách giao dịch từ kho dữ liệu. |
| **Lịch biểu HLV** (`PtSchedulePage`) | `Chi Tiết` | `tableAction` | Hoạt động đầy đủ | `PtSchedulePage.xaml` | Xem thông tin buổi tập, HLV và học viên kèm. |
| | `Xác Nhận` | `tableAction` (`success`) | Hoạt động đầy đủ | `PtSchedulePage.xaml` | Xác nhận hoàn thành ca tập của học viên và HLV. |
| | `Xếp Lịch HLV` | `primary` (44px) | Hoạt động đầy đủ | `PtSchedulePage.xaml` | Đặt ca tập mới với đủ 4 trường: HLV, Ngày, Học viên, Giờ. |
| | `Danh Sách HLV` | `primary` (36px) | Hoạt động đầy đủ | `TrainerListDialog.xaml` | Xem danh sách HLV, chuyên môn và số học viên phụ trách. |

---

## 2. Chi Tiết Tối Ưu Bố Cục Nút (Layout Fixes)

### 2.1. Phân Hệ Quản Lý Hội Viên & Gói Tập (`MembersPage`)
* **Tệp mã nguồn**: `UI/desktop_portal/views/members_page.py`
* **Vấn đề đã xử lý**: 
  - Trước đây, việc hiển thị cùng lúc 4 nút (`Sửa`, `Chi tiết`, `Bảo lưu`, `Hủy gói`) khiến các chữ "Bảo lưu" và "Hủy gói" bị ép vụn, xén mất đuôi chữ (`Bảo l...`, `Hủy gó...`).
  - Đã lược bỏ nút `Chi tiết` trên dòng thao tác theo yêu cầu người dùng, giữ lại 3 nút hành động chính: `Sửa`, `Bảo lưu`, `Hủy gói`.
  - Khóa cứng độ rộng cột Thao Tác thành **220px** (`setColumnWidth(6, 220)` với `QHeaderView.ResizeMode.Fixed`).
  - Bổ sung sự kiện double-click trên dòng bảng (`self.table.cellDoubleClicked`) để người quản trị vẫn có thể mở modal `MemberDetailDialog` (xem mã QR thẻ tập, hạn sử dụng, chỉ số cơ thể) một cách trực quan, tiện lợi.

### 2.2. Phân Hệ Quản Lý Nhân Sự & Cài Đặt Hệ Thống (`SettingsPage`)
* **Tệp mã nguồn**: `UI/desktop_portal/views/settings_page.py`
* **Vấn đề đã xử lý**:
  - Cơ chế `ResizeToContents` của Qt làm co hẹp cột Thao Tác xuống khoảng 80px, dẫn đến các chữ `Khóa TK` hoặc `Mở Khóa` bị cắt cụt.
  - Đã cố định độ rộng cột Thao Tác thành **180px** (`setColumnWidth(5, 180)` với `QHeaderView.ResizeMode.Fixed`).
  - Hai nút `Sửa` và `Khóa TK` / `Mở Khóa` hiển thị đầy đủ 100% nội dung chữ, có lề và khoảng cách nút 6px đồng bộ.

### 2.3. Phân Hệ Lịch Sử Hóa Đơn & In Phiếu Thu (`InvoiceHistoryPage`)
* **Tệp mã nguồn**: `UI/desktop_portal/views/invoice_history_page.py`
* **Vấn đề đã xử lý**:
  - Nút `Hoàn Tiền` bị xén chữ do cột Thao Tác bị co lại tự động.
  - Cấu trúc bảng được chuẩn hóa thành 8 cột: `MÃ HÓA ĐƠN`, `THỜI GIAN`, `HỘI VIÊN`, `GÓI DỊCH VỤ`, `SỐ TIỀN`, `PHƯƠNG THỨC`, `TRẠNG THÁI`, `THAO TÁC`.
  - Khóa cứng độ rộng cột Thao Tác thành **190px** (`setColumnWidth(7, 190)` với `QHeaderView.ResizeMode.Fixed`).
  - Cả hai nút `In K80` và `Hoàn Tiền` có đầy đủ không gian hiển thị rõ ràng, không còn hiện tượng tràn hay mất chữ.

### 2.4. Phân Hệ Điều Phối Lịch Biểu HLV (`PtSchedulePage`)
* **Tệp mã nguồn**: `UI/desktop_portal/views/pt_schedule_page.py`
* **Vấn đề đã xử lý**:
  - **Bổ sung các trường nhập liệu còn thiếu ở cột trái**:
    - `Ngày dạy`: Bổ sung `QDateEdit` chọn ngày (`setCalendarPopup(True)`).
    - `Hội viên đặt ca`: Bổ sung `QComboBox` danh sách học viên kèm số buổi tập còn lại.
    - `Khung giờ`: Bổ sung bộ đôi ComboBox chọn `Giờ bắt đầu` và `Giờ kết thúc` (06:00 - 22:00).
    - `Xếp Lịch HLV`: Nút bấm lưu ca tập mới vào danh sách.
  - **Bổ sung thanh điều hướng và khung hiển thị cột phải**:
    - Đóng gói toàn bộ bảng lịch dạy vào khung `QFrame#cardFrame` bo góc 16px đồng bộ.
    - Bổ sung nút `Danh Sách HLV` (36px, Accent) và `Tải Lại Lịch` (36px) ở tiêu đề.
  - **Sửa lỗi hiển thị cột Thao Tác**:
    - Khóa cứng độ rộng cột Thao Tác thành **170px** (`setColumnWidth(3, 170)` với `QHeaderView.ResizeMode.Fixed`).
    - Hai nút `Chi Tiết` và `Xác Nhận` (màu xanh lá `success`) hiển thị đầy đủ 100% chữ không bị co cụt.

---

## 3. Các Điểm Kỹ Thuật Cần Lưu Ý Khi Nối Backend (Technical Notes)

1. **Quy tắc padding và cell container**:
   - `QPushButton[tableAction="true"]` trong `UI/styles/dark_theme.qss` được đặt padding `0px 8px`, chiều cao chuẩn `28px`.
   - Mỗi ô thao tác sử dụng container `QWidget` kết hợp `QHBoxLayout` (`contentsMargins: 4, 2, 4, 2`, `spacing: 6`).
2. **Quy tắc giao dịch CSDL khi gắn Backend**:
   - **Bảo lưu gói tập**: Cập nhật trạng thái `FROZEN` trong bảng `MemberSubscriptions`, ghi nhận khoảng thời gian nghỉ và tự động cộng thêm số ngày bảo lưu vào `end_date`.
   - **Hủy gói tập & Hoàn tiền**: Mở transaction cập nhật bảng `Invoices` (`status = 'REFUNDED'`), đồng thời hủy quyền sử dụng trong `MemberSubscriptions` (`status = 'CANCELLED'`) và vô hiệu hóa mã QR để chặn cửa quầy điểm danh.
3. **Bảo toàn tính toàn vẹn của kiểm thử**:
   - Toàn bộ 49/49 unit test trong `UI/tests/` tiếp tục vượt qua ổn định 100%.

---

## 4. Chuẩn Hóa Cổng Hội Viên (Member Portal - 1:1 Tham Chiếu Blazor Server)

* **Tệp mã nguồn**: `UI/web_portal/member_portal_window.py`
* **Tham chiếu**: `ui_ref/Web/Components/Layout/NavMenu.razor`, `ui_ref/Web/Components/Pages/Member/History.razor`, `ui_ref/Web/Components/Member/WorkoutHistoryTimeline.razor`.

### 4.1. Cấu Trúc 4 Tab Chuẩn Phân Hệ Member
1. `💳 Thẻ Điện Tử & Hồ Sơ` (`/member/dashboard`): Thẻ thành viên kèm mã QR điểm danh, thời hạn gói tập, số buổi PT còn lại và form cập nhật hồ sơ.
2. `📅 Đặt Lịch Huấn Luyện Viên` (`/member/booking`): Chọn HLV, ngày tập và khung giờ ca rảnh để đặt lịch tập 1-1.
3. `📈 Chỉ Số Cơ Thể InBody` (`/member/inbody`): Thống kê cân nặng, chiều cao, body fat, khối lượng cơ và biểu đồ radar so sánh thể trạng mục tiêu.
4. `🕒 Nhật Ký Tập Luyện` (`/member/history`): Toàn bộ nhật ký vào cửa phòng gym và các buổi tập cùng HLV.

### 4.2. Các Thay Đổi & Sửa Đổi Đã Thực Hiện
- **Lược bỏ tab "Mua Gói Tập (VietQR)"**: Cổng hội viên cá nhân không có chức năng tự mua gói tập độc lập. Gói tập được đăng ký và thanh toán trực tiếp tại quầy lễ tân (Admin Desktop POS Billing).
- **Tái cấu trúc tab "Lịch Sử & Hóa Đơn" thành "Nhật Ký Tập Luyện & Vào Cửa"**:
  - Không hiển thị dữ liệu tiền tệ hóa đơn trong giao diện này.
  - Bổ sung thanh 3 nút lọc trạng thái hoạt động: `Tất Cả Hoạt Động`, `Vào Cửa Phòng Tập`, `Tập Với HLV (PT)`.
  - Thiết lập bảng timeline 4 cột: `Thời Gian`, `Loại Hoạt Động`, `Nội Dung Hoạt Động`, `Chi Tiết / Ghi Chú`.
  - Phân loại rõ ràng:
    - *Vào Cửa Phòng Tập*: Điểm danh qua cổng kiểm soát, quét mã QR thành công (màu xanh lá `#34D399`).
    - *Tập Luyện PT 1-1*: Ca tập cùng HLV phụ trách, thời lượng 60 phút, nội dung bài tập và ghi chú chuyên môn (màu xanh dương `#38BDF8`).

---

## 5. Chuẩn Hóa Cổng Huấn Luyện Viên (PT Portal - 1:1 Tham Chiếu Blazor Server)

* **Tệp mã nguồn**: `UI/web_portal/pt_portal_window.py`
* **Tham chiếu**: `ui_ref/Web/Components/PT/PtWeeklySchedule.razor`, `ui_ref/Web/Components/PT/PtStudentsList.razor`, `ui_ref/Web/Components/PT/PtAvailabilityGrid.razor`, `ui_ref/Web/Components/PT/PtProfileSummaryWidget.razor`.

### 5.1. Sửa Lỗi Bố Cục Nút Thao Tác & Trực Quan Hóa (Layout & Visual Fixes)
- **Chuẩn hóa thanh chọn ngày (Tab 1 & Tab 3)**:
  * **Bỏ nhãn "(Hôm nay)"**: Theo yêu cầu, không chèn chữ `(Hôm nay)` làm dài nhãn; chỉ cần làm sáng (highlight xanh `#0284C7`) nút ngày đang được chọn là đủ nhận biết.
  * **Sửa lỗi cắt chữ "Chủ Nhật"**: Mở rộng chiều rộng nút ngày từ 84px lên **96px** (`setFixedWidth(96)`), bổ sung inline CSS `padding: 4px; font-size: 12px;` đè padding mặc định của QSS tổng, giúp chữ `Chủ Nhật` hiển thị trọn vẹn 100%, không bị xén mép.
  * **Trạng thái ngày đã qua**: Các ngày trong quá khứ (`< hôm nay`) hiển thị nền tối `#0F172A`, chữ xám `#64748B`.
- **Tab 1: Lịch Dạy & Buổi Hẹn**:
  * **Vấn đề**: Thiếu thông tin ngày dạy khiến HLV không biết buổi tập diễn ra ngày nào; nút `Hoàn Tất Buổi` bị nén cụt chữ.
  * **Giải pháp**:
    - Bổ sung bộ chọn 7 ngày tuần chuẩn từ Thứ 2 đến Chủ Nhật kèm nút xem "Tất Cả Tuần Này".
    - Bảng lịch dạy bổ sung cột `Ngày` (110px Fixed) hiển thị rõ ràng ngày dạy (`dd/MM/yyyy`).
    - Khóa cứng cột Thao Tác thành **150px** (`QHeaderView.ResizeMode.Fixed`). Nút bấm sử dụng thuộc tính `tableAction="true"` kết hợp `actionVariant="primary"`, hiển thị 100% chữ không bao giờ bị cắt.
- **Tab 2: Danh Sách Học Viên**:
  * **Vấn đề**: Nút `📊 Nhập InBody` bị ép hẹp và cắt dọc chữ do xung đột chiều cao tối thiểu của QSS chung.
  * **Giải pháp**: Thiết lập `tableAction="true"` và cố định độ rộng cột thành **160px**, tăng chiều cao dòng lên **44px** giúp nút nằm cân đối, sắc nét.
- **Tab 3: Đăng Ký Ca Rảnh (`PtAvailabilityGrid`)**:
  * **Thứ tự các ngày chuẩn**: Hiển thị cố định từ **Thứ 2** đến **Chủ Nhật** của tuần hiện tại.
  * **Trạng thái ngày đã qua**: Các ngày trong quá khứ (`< hôm nay`) được hiển thị nền xám đậm `#0F172A`, chữ xám `#64748B`, có banner cảnh báo và tự động vô hiệu hóa nút thêm khung giờ.
  * **Sửa lỗi layout bị nhảy hàng**: Bố trí `Giờ bắt đầu`, `Giờ kết thúc` và nút `+ Mở Khung Giờ Này` trên cùng một hàng ngang cân đối, không còn bị tụt nút xuống dưới.
- **Tab 4: Hồ Sơ & Đánh Giá (Khắc phục lỗi Cascade Stylesheet)**:
  * **Vấn đề**: Việc gán `setStyleSheet` trực tiếp lên `QFrame` cha mà không có CSS selector khiến toàn bộ `QLabel` bên trong bị thừa viền bo góc, viền xám và nền đen biến dạng (làm các ô metric bị ẩn chữ).
  * **Giải pháp**: Sử dụng `setObjectName("cardFrame")` chuẩn và gắn scoped selector `QFrame { ... }`, `QLabel { background: transparent; border: none; }` để loại bỏ hoàn toàn các viền thừa, hiển thị đầy đủ avatar, tên HLV, badge trạng thái và 4 ô chỉ số thống kê.

### 5.2. Bổ Sung Đầy Đủ Trường Nghiệp Vụ Tab Đăng Ký Ca Rảnh (`PtAvailabilityGrid`)
- **Bộ chọn 7 ngày trong tuần**: Thứ 2 đến Chủ Nhật kèm ngày/tháng `dd/MM`.
- **Khung chọn khoảng thời gian (Time Range Selector)**: Dropdown `Giờ bắt đầu` và `Giờ kết thúc` cùng hàng với nút `+ Mở Khung Giờ Này`.
- **Bảng quản lý ca rảnh theo ngày**: Cột `Khung Giờ` (150px), `Trạng Thái` (180px), `Chi Tiết / Học Viên Đặt` (Stretch), `Thao Tác` (140px Fixed - nút `✕ Hủy Mở`).
- **Nút lưu tổng thể**: `✓ Lưu Thay Đổi Lịch Rảnh` (42px, Primary).

### 5.3. Bảo Toàn Kiểm Thử Tự Động
- Cập nhật unit test `test_pt_portal_tabs_and_availability_grid` trong `UI/tests/test_phase5_ui.py`.
- Toàn bộ 50/50 tests PASSED ổn định. Flake8 0 lỗi.



