# Giao Diện Python • Hệ Thống Quản Lý Phòng Tập Gym

Đã tách thành **3 ứng dụng độc lập**, dùng chung giao diện chuẩn đăng nhập [LoginWindow](file:///c:/Users/ASUS/OneDrive/Desktop/Gym/UI/components/login_window.py), không dùng cổng chung:

---

## 🚀 Khởi Chạy 3 Giao Diện Độc Lập

### 1. Cổng Quản Trị Viên (Admin Desktop)
- **Chạy file**: [run_admin.bat](file:///c:/Users/ASUS/OneDrive/Desktop/Gym/run_admin.bat)
- **Lệnh Python**: `& .venv\Scripts\python.exe UI\main_admin.py`
- **Màn hình**:
  - Giao diện đăng nhập quản trị (Tài khoản mẫu: `admin`).
  - Quầy điểm danh (Quét mã QR qua Webcam & nhập tay).
  - Bán gói tập & thanh toán POS (VietQR, Tiền mặt).
  - Lịch sử hóa đơn giao dịch & in bill.
  - Quản lý danh sách hội viên & đăng ký mới.
  - Điều phối lịch huấn luyện viên PT.
  - Báo cáo KPI & doanh thu (biểu đồ Matplotlib).
  - Danh mục gói tập & quản lý phân quyền nhân sự.

---

### 2. Cổng Hội Viên Thể Thao (Member Web Portal)
- **Chạy file**: [run_member.bat](file:///c:/Users/ASUS/OneDrive/Desktop/Gym/run_member.bat)
- **Lệnh Python**: `& .venv\Scripts\python.exe UI\main_member.py`
- **Màn hình**:
  - Giao diện đăng nhập hội viên (Tài khoản mẫu: `HV-1001`, `0987654321`).
  - Thẻ hội viên điện tử & mã QR cá nhân check-in.
  - Danh mục gói tập & mua gói quét mã VietQR.
  - Wizard đặt lịch hẹn với Huấn luyện viên PT.
  - Bảng chỉ số thể trạng InBody & biểu đồ so sánh mục tiêu.
  - Lịch sử buổi tập & hóa đơn thanh toán.

---

### 3. Cổng Huấn Luyện Viên Cá Nhân (Trainer PT Web Portal)
- **Chạy file**: [run_pt.bat](file:///c:/Users/ASUS/OneDrive/Desktop/Gym/run_pt.bat)
- **Lệnh Python**: `& .venv\Scripts\python.exe UI\main_pt.py`
- **Màn hình**:
  - Giao diện đăng nhập HLV (Tài khoản mẫu: `pt_hung`, `pt_mai`).
  - Lịch dạy trong tuần & xác nhận hoàn tất buổi tập.
  - Quản lý danh sách học viên đang theo kèm & số buổi còn lại.
  - Hộp thoại nhập chỉ số đo InBody cho học viên.
  - Thiết lập ca rảnh hàng tuần cho hội viên đăng ký.
  - Hồ sơ cá nhân, chuyên môn và đánh giá sao từ học viên.
