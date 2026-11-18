# DANH MỤC THÀNH PHẦN GIAO DIỆN (UI REFERENCE CATALOG)

> **Mục đích:** Thư mục `ui_ref/` chứa toàn bộ 100% định nghĩa giao diện người dùng (UI Components, Views, Modals, Dialogs, Styles, Assets) được bóc tách từ `src/Client/`, đã lược bỏ hoàn toàn tầng xử lý nghiệp vụ (ViewModels, Services, API Calls, Database).

---

## 1. TỔNG QUAN THỐNG KÊ (INVENTORY SUMMARY)

| Nền tảng | Thành phần giao diện | Số lượng | Định dạng file |
| :--- | :--- | :--- | :--- |
| **Desktop (WinUI 3)** | Màn hình chính (Views) | **9** | `.xaml` |
| | Hộp thoại & Wizard (Dialogs) | **15** | `.xaml` |
| | Khung ứng dụng & Cửa sổ (Root) | **3** | `App.xaml`, `MainWindow.xaml`, `MainPage.xaml` |
| | Bảng mã màu & Tokens (Styles) | **1** | `ColorTokens.xaml` |
| | Bộ chuyển đổi hiển thị (Converters) | **1** | `ValueConverters.cs` (chỉ chứa IValueConverter UI) |
| | Hình ảnh, Icon, Logo (Assets) | **9** | `.png`, `.ico` |
| **Web (Blazor Server)** | Khung điều hướng & Layout | **5** | `.razor`, `.razor.css` |
| | Modal & Widget Hội viên (Member) | **9** | `.razor` |
| | Modal & Widget HLV (PT) | **5** | `.razor` |
| | Trang người dùng (Pages) | **11** | `.razor` |
| | Cấu hình định tuyến & Khởi tạo (Root) | **3** | `App.razor`, `Routes.razor`, `_Imports.razor` |
| | Tài nguyên tĩnh (wwwroot) | **4** | `.css`, `.png`, `.map` |
| **TỔNG CỘNG** | **Toàn bộ giao diện hệ thống** | **76 file** | Đầy đủ 100% UI không thiếu thành phần |

---

## 2. CHI TIẾT GIAO DIỆN DESKTOP (WINUI 3 - FLUENT DESIGN DARK MODE)

### 2.1. Màn hình chính (`ui_ref/Desktop/Views/`)
1. **`CheckInCounterPage.xaml`**: Màn hình Quầy Điểm Danh & Check-in 2 cột (quét QR camera trực tiếp, nhập SĐT thủ công, hiển thị thẻ trạng thái Xanh/Đỏ lớn).
2. **`DashboardPage.xaml`**: Bảng điều khiển phân tích số liệu quản trị BI đa chiều (4 thẻ KPI doanh thu/check-in/hội viên/PT, biểu đồ cột lưu lượng theo giờ, biểu đồ tròn cơ cấu gói).
3. **`InvoiceHistoryPage.xaml`**: Màn hình Tra cứu & Quản lý lịch sử hóa đơn (bộ lọc ngày/trạng thái/tên, bảng hóa đơn tabular-nums, nút in và hoàn tiền).
4. **`LoginPage.xaml`**: Màn hình Đăng nhập Lễ tân & Quản trị viên (form căn giữa, hiệu ứng gradient nền, nút ẩn/hiện mật khẩu).
5. **`MembersPage.xaml`**: Màn hình Quản lý Danh sách Hội viên & Gói tập (bộ lọc tìm kiếm SĐT/tên, danh sách thẻ hội viên kèm chip trạng thái, thanh tác vụ gia hạn/bảo lưu/hủy gói).
6. **`PackagePlansPage.xaml`**: Màn hình Quản lý Danh mục Gói tập phòng gym (danh sách gói, thẻ giá niêm yết, công tắc kích hoạt/ngừng kinh doanh).
7. **`PosBillingPage.xaml`**: Màn hình Bán hàng POS & Thu tiền tại quầy (chọn nhanh hội viên, chọn gói tập, bộ 3 nút thanh toán Tiền mặt/VietQR/POS, xuất hóa đơn in nhiệt).
8. **`PtSchedulePage.xaml`**: Màn hình Quản lý & Xếp lịch làm việc cho HLV PT (lịch trực theo tuần/tháng, giám sát ca tập, xác nhận kết quả ca quá giờ).
9. **`SettingsPage.xaml`**: Màn hình Cài đặt Hệ thống & Phân quyền RBAC (form tạo nhân sự, danh sách tài khoản kèm chip vai trò, nút sửa và khóa/mở khóa tài khoản).

### 2.2. Hộp thoại & Wizard (`ui_ref/Desktop/Dialogs/`)
1. **`CancelSubscriptionDialog.xaml`**: Hộp thoại xác nhận Hủy gói tập (nhập lý do tối thiểu 10 ký tự, cảnh báo mất quyền lợi).
2. **`FreezeSubscriptionDialog.xaml`**: Hộp thoại Bảo lưu gói tập (chọn khoảng ngày bảo lưu, kiểm tra định mức bảo lưu tối đa).
3. **`MemberDetailDialog.xaml`**: Hộp thoại Xem & Cập nhật thông tin chi tiết hồ sơ hội viên.
4. **`OverrideCheckInDialog.xaml`**: Hộp thoại Cho vào thủ công khi hội viên quên điện thoại hoặc cổng kẹt cơ khí (bắt buộc chọn lý do).
5. **`PackagePlanEditDialog.xaml`**: Hộp thoại Thêm/Sửa gói tập (Tên, đơn giá, thời hạn ngày, số lượt gym, số buổi PT, số ngày bảo lưu).
6. **`PtAssignDialog.xaml`**: Hộp thoại Phân công HLV PT phụ trách cố định cho hội viên.
7. **`ReceiptPreviewDialog.xaml`**: Hộp thoại Xem trước mẫu hóa đơn in nhiệt khổ K80 tiêu chuẩn.
8. **`RefundInvoiceDialog.xaml`**: Hộp thoại Xử lý Hủy & Hoàn tiền hóa đơn (nhập số tiền hoàn, lý do hoàn, chọn hình thức tiền mặt/chuyển khoản).
9. **`RegisterMemberWizard.xaml`**: Wizard Đăng ký hội viên mới kèm gói tập đa bước.
10. **`RenewUpgradeModal.xaml`**: Hộp thoại Gia hạn hoặc Nâng cấp gói tập lên hạng cao hơn.
11. **`SessionReviewDialog.xaml`**: Hộp thoại Rà soát ca dạy quá giờ (Hoàn thành, Học viên vắng, PT vắng, Hoãn ca).
12. **`TrainerListDialog.xaml`**: Hộp thoại Tra cứu danh sách và lịch rảnh của đội ngũ HLV.
13. **`TrainerProfileDialog.xaml`**: Hộp thoại Xem hồ sơ chuyên môn và danh sách học viên của HLV.
14. **`UserEditDialog.xaml`**: Hộp thoại Cập nhật thông tin nhân viên và phân quyền vai trò (có chốt chặn bảo vệ SuperAdmin).
15. **`VietQrPaymentDialog.xaml`**: Hộp thoại hiển thị mã QR động chuẩn VietQR tích hợp tự động khớp giao dịch.

### 2.3. Khung & Phong cách (`ui_ref/Desktop/`)
* **`Styles/ColorTokens.xaml`**: Hệ thống biến màu Dark Mode (`BgCanvasBrush`, `BgSurfaceBrush`, `AccentPrimaryBrush`, `StatusSuccessBrush`, `StatusDangerBrush`,...).
* **`Converters/ValueConverters.cs`**: Các bộ chuyển đổi hiển thị UI thuần túy (`StatusToBrushConverter`, `CurrencyFormatterConverter`, `LockButtonTextConverter`, `CanManageUserConverter`,...).
* **`Assets/`**: Đầy đủ 9 file tài nguyên ảnh, app icon, logo các kích thước, splash screen.
* **`App.xaml`**, **`MainWindow.xaml`**, **`MainPage.xaml`**: Khung cửa sổ ứng dụng và thanh điều hướng chính.

---

## 3. CHI TIẾT GIAO DIỆN WEB (BLAZOR SERVER - RESPONSIVE MOBILE & DESKTOP)

### 3.1. Khung điều hướng & Layout (`ui_ref/Web/Components/Layout/`)
1. **`MainLayout.razor` & `.css`**: Khung giao diện dùng chung, thanh Top-bar (thương hiệu, badge vai trò, chuông thông báo, nút Đăng xuất).
2. **`NavMenu.razor` & `.css`**: Thanh điều hướng đáy (Bottom Navigation) tối ưu cho thiết bị di động, tự động đổi menu theo vai trò `Member` hoặc `PT`.
3. **`NotificationBell.razor`**: Hộp thông báo thời gian thực dạng popover kèm bộ lọc Đã đọc/Chưa đọc.

### 3.2. Thành phần Hội viên (`ui_ref/Web/Components/Member/`)
1. **`DigitalSubscriptionWidget.razor`**: Thẻ hội viên điện tử hiển thị mã QR cá nhân dùng để quét tại quầy check-in, số buổi còn lại, hạn sử dụng.
2. **`InBodyDashboard.razor`**: Bảng theo dõi chỉ số thể hình InBody (Cân nặng, BMI, Tỷ lệ mỡ, Khối lượng cơ) dạng timeline.
3. **`PackageCatalog.razor`**: Danh mục lưới thẻ gói tập hiển thị quyền lợi và giá bán.
4. **`PtBookingWizard.razor`**: Giao diện Đặt lịch tập với PT (chọn ngày, chọn khung giờ rảnh khả dụng, xác nhận ca tập).
5. **`CancelBookingModal.razor`**: Modal hủy lịch tập với quy tắc hủy trước 2 tiếng.
6. **`RescheduleBookingModal.razor`**: Modal dời lịch tập sang khung giờ rảnh khác của PT.
7. **`SessionRatingModal.razor`**: Modal đánh giá chất lượng buổi tập (1 - 5 sao và nhận xét phản hồi).
8. **`VietQrModal.razor`**: Modal thanh toán gói tập qua mã VietQR trên cổng web.
9. **`WorkoutHistoryTimeline.razor`**: Dòng thời gian lịch sử các buổi tập đã hoàn thành.

### 3.3. Thành phần Huấn luyện viên PT (`ui_ref/Web/Components/PT/`)
1. **`PtWeeklySchedule.razor`**: Lịch dạy tuần của PT hiển thị trực quan các ca tập đã đặt, ca hoàn thành, ca trống.
2. **`PtAvailabilityGrid.razor`**: Lưới chọn và đăng ký khung giờ rảnh trong tuần cho học viên đặt lịch.
3. **`PtProfileSummaryWidget.razor`**: Thẻ tóm tắt thông tin HLV, tổng số học viên phụ trách và số ca dạy hoàn thành.
4. **`PtStudentsList.razor`**: Danh sách học viên được phân công đồng hành cùng PT.
5. **`InBodyEntryModal.razor`**: Modal nhập liệu chỉ số InBody đo trực tiếp cho học viên tại phòng tập.

### 3.4. Các trang người dùng (`ui_ref/Web/Components/Pages/`)
* **Chung:** `Login.razor` (đăng nhập hội viên & PT), `Home.razor` (điều hướng theo vai trò), `Error.razor`.
* **Phân hệ Member:** `Dashboard.razor`, `PtBooking.razor`, `InBody.razor`, `History.razor`, `Packages.razor`.
* **Phân hệ PT:** `Schedule.razor`, `Availability.razor`, `Students.razor`, `Profile.razor`.
* **Tài nguyên tĩnh:** `ui_ref/Web/wwwroot/` chứa `app.css`, `bootstrap.min.css`, `favicon.png`.
