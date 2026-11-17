"""
Mock Data Store for Gym Management System.
Matches models and DTOs from GymManagement.Server.Core.DTOs.
"""
from datetime import datetime, date, timedelta

PACKAGES = [
    {
        "id": "PKG01",
        "name": "Gym Standard 1 Tháng",
        "price": 450000,
        "duration_days": 30,
        "has_pt": False,
        "pt_sessions": 0,
        "benefits": "Tập luyện không giới hạn khung giờ, phòng tắm nóng lạnh, tủ locker tiêu chuẩn.",
        "badge": "Phổ Biến"
    },
    {
        "id": "PKG02",
        "name": "Gym Standard 3 Tháng",
        "price": 1200000,
        "duration_days": 90,
        "has_pt": False,
        "pt_sessions": 0,
        "benefits": "Tiết kiệm 150K, tặng 01 bình lắc GymPro, miễn phí đo InBody định kỳ.",
        "badge": "Tiết Kiệm"
    },
    {
        "id": "PKG03",
        "name": "VIP Platinum 12 Tháng",
        "price": 4500000,
        "duration_days": 365,
        "has_pt": False,
        "pt_sessions": 2,
        "benefits": "Toàn quyền sử dụng Gym + Yoga + Xông hơi Sauna, tặng 02 buổi định hướng cùng PT.",
        "badge": "VIP Đẳng Cấp"
    },
    {
        "id": "PKG04",
        "name": "Gói HLV Kèm Riêng PT 1-1 (12 Buổi)",
        "price": 3600000,
        "duration_days": 60,
        "has_pt": True,
        "pt_sessions": 12,
        "benefits": "1 kèm 1 giáo án cá nhân hóa, đo chỉ số InBody mỗi tuần, cam kết form chuẩn.",
        "badge": "PT Chuyên Sâu"
    },
    {
        "id": "PKG05",
        "name": "Gói HLV Kèm Riêng PT 1-1 (24 Buổi)",
        "price": 6800000,
        "duration_days": 90,
        "has_pt": True,
        "pt_sessions": 24,
        "benefits": "Thực đơn dinh dưỡng chi tiết, theo dõi 24/7, cam kết tăng cơ giảm mỡ rõ rệt.",
        "badge": "PT Toàn Diện"
    }
]

MEMBERS = [
    {
        "code": "HV-1001",
        "name": "Nguyễn Hoàng Nam",
        "phone": "0987654321",
        "email": "nam.nguyen@gmail.com",
        "package_name": "VIP Platinum 12 Tháng",
        "package_id": "PKG03",
        "start_date": "2026-01-15",
        "expiry_date": "2027-01-15",
        "status": "Đang hoạt động",
        "sessions_left": 2,
        "pt_assigned": "Nguyễn Văn Hưng",
        "avatar": "Assets/Square150x150Logo.scale-200.png",
        "weight": 72.5,
        "height": 175,
        "body_fat": 16.8,
        "muscle_mass": 35.2,
        "bmi": 23.7
    },
    {
        "code": "HV-1002",
        "name": "Trần Thị Thu Thảo",
        "phone": "0912345678",
        "email": "thao.tran@yahoo.com",
        "package_name": "Gói HLV Kèm Riêng PT 1-1 (12 Buổi)",
        "package_id": "PKG04",
        "start_date": "2026-10-01",
        "expiry_date": "2026-12-01",
        "status": "Đang hoạt động",
        "sessions_left": 8,
        "pt_assigned": "Trần Thị Mai",
        "avatar": "Assets/Square150x150Logo.scale-200.png",
        "weight": 54.0,
        "height": 162,
        "body_fat": 22.1,
        "muscle_mass": 23.5,
        "bmi": 20.6
    },
    {
        "code": "HV-1003",
        "name": "Lê Anh Tuấn",
        "phone": "0909887766",
        "email": "tuan.le@outlook.com",
        "package_name": "Gym Standard 1 Tháng",
        "package_id": "PKG01",
        "start_date": "2026-10-10",
        "expiry_date": "2026-11-10",
        "status": "Hết hạn",
        "sessions_left": 0,
        "pt_assigned": "Chưa có",
        "avatar": "",
        "weight": 68.0,
        "height": 170,
        "body_fat": 20.5,
        "muscle_mass": 30.1,
        "bmi": 23.5
    },
    {
        "code": "HV-1004",
        "name": "Phạm Quốc Dũng",
        "phone": "0933445566",
        "email": "dung.pham@gmail.com",
        "package_name": "Gym Standard 3 Tháng",
        "package_id": "PKG02",
        "start_date": "2026-09-01",
        "expiry_date": "2026-12-01",
        "status": "Đang bảo lưu",
        "sessions_left": 0,
        "pt_assigned": "Chưa có",
        "avatar": "",
        "weight": 80.5,
        "height": 178,
        "body_fat": 24.2,
        "muscle_mass": 36.0,
        "bmi": 25.4
    }
]

TRAINERS = [
    {
        "id": "PT01",
        "name": "Nguyễn Văn Hưng",
        "phone": "0944112233",
        "specialty": "Tăng cơ & Thể hình chuyên nghiệp (Bodybuilding)",
        "rating": 4.9,
        "active_students": 14,
        "experience": "6 năm kinh nghiệm, Chứng chỉ Quốc tế NASM CPT"
    },
    {
        "id": "PT02",
        "name": "Trần Thị Mai",
        "phone": "0944223344",
        "specialty": "Giảm mỡ toàn thân, HIIT & Pilates định hình vóc dáng",
        "rating": 5.0,
        "active_students": 16,
        "experience": "5 năm kinh nghiệm, HLV Trưởng nữ vóc dáng"
    },
    {
        "id": "PT03",
        "name": "Lê Quốc Tuấn",
        "phone": "0944334455",
        "specialty": "Phục hồi chấn thương & Sức mạnh cốt lõi (Powerlifting)",
        "rating": 4.8,
        "active_students": 11,
        "experience": "7 năm kinh nghiệm, VĐV Powerlifting quốc gia"
    }
]

INVOICES = [
    {
        "code": "HD-20261117-001",
        "member_name": "Nguyễn Hoàng Nam",
        "package_name": "VIP Platinum 12 Tháng",
        "amount": 4500000,
        "payment_method": "VietQR Chuyển khoản",
        "date": "2026-11-17 08:30",
        "status": "Đã thanh toán",
        "cashier": "Admin Lễ Tân"
    },
    {
        "code": "HD-20261116-042",
        "member_name": "Trần Thị Thu Thảo",
        "package_name": "Gói HLV Kèm Riêng PT 1-1 (12 Buổi)",
        "amount": 3600000,
        "payment_method": "VietQR Chuyển khoản",
        "date": "2026-11-16 16:45",
        "status": "Đã thanh toán",
        "cashier": "Admin Lễ Tân"
    },
    {
        "code": "HD-20261115-018",
        "member_name": "Phạm Quốc Dũng",
        "package_name": "Gym Standard 3 Tháng",
        "amount": 1200000,
        "payment_method": "Tiền mặt",
        "date": "2026-11-15 10:15",
        "status": "Đã thanh toán",
        "cashier": "Thu Ngân 01"
    }
]

CHECKIN_LOGS = [
    {"time": "08:15:22", "code": "HV-1001", "name": "Nguyễn Hoàng Nam", "method": "Quét Mã QR", "status": "Hợp Lệ"},
    {"time": "08:42:10", "code": "HV-1002", "name": "Trần Thị Thu Thảo", "method": "Quét Mã QR", "status": "Hợp Lệ"},
    {"time": "09:05:44", "code": "HV-1003", "name": "Lê Anh Tuấn", "method": "Nhập Mã", "status": "Gói Hết Hạn"},
    {"time": "09:20:11", "code": "HV-1004", "name": "Phạm Quốc Dũng", "method": "Quét Mã QR", "status": "Đang Bảo Lưu"}
]

SCHEDULE_SLOTS = [
    {"pt": "Nguyễn Văn Hưng", "time": "07:00 - 08:00", "member": "Nguyễn Hoàng Nam", "status": "Đã xác nhận"},
    {"pt": "Nguyễn Văn Hưng", "time": "09:00 - 10:00", "member": "Hoàng Văn Đạt", "status": "Đã xác nhận"},
    {"pt": "Nguyễn Văn Hưng", "time": "15:00 - 16:00", "member": "", "status": "Còn trống"},
    {"pt": "Nguyễn Văn Hưng", "time": "18:00 - 19:00", "member": "Lê Quốc Thịnh", "status": "Đã xác nhận"},
    {"pt": "Trần Thị Mai", "time": "08:00 - 09:00", "member": "Trần Thị Thu Thảo", "status": "Đã xác nhận"},
    {"pt": "Trần Thị Mai", "time": "10:00 - 11:00", "member": "Vũ Mai Phương", "status": "Đã xác nhận"},
    {"pt": "Trần Thị Mai", "time": "16:00 - 17:00", "member": "", "status": "Còn trống"},
    {"pt": "Trần Thị Mai", "time": "17:30 - 18:30", "member": "Đỗ Bích Ngọc", "status": "Đã xác nhận"}
]
