# KẾ HOẠCH TRIỂN KHAI CHI TIẾT (TASK.MD)
## Tính năng: Đăng ký Hội viên kèm Gói tập (UC02.1 + UC05.1) & Điểm danh Hội viên (UC03)
**Tài liệu lược đồ gốc:** [`doc/GymManagement_Physical_Model.sql`](../doc/GymManagement_Physical_Model.sql)  
**Nền tảng:** Python (PyQt6) • **Cơ sở dữ liệu:** MySQL (Docker Container) • **Mô hình kiến trúc:** Layered OOP (Entity - Repository - Service - View)

---

## 1. MỤC TIÊU VÀ PHẠM VI TRIỂN KHAI

Áp dụng chính xác 100% lược đồ thực thể vật lý từ [`doc/GymManagement_Physical_Model.sql`](../doc/GymManagement_Physical_Model.sql) vào hệ thống Python Desktop hiện tại, triển khai trọn vẹn 2 luồng nghiệp vụ cốt lõi:

1. **Đăng ký hội viên mới cùng gói tập (UC02.1 + UC05.1):**
   * Tạo bản ghi `User` (Role = `MEMBER`, SĐT, Email, CCCD/UserName, Họ tên, Trạng thái `ACTIVE`).
   * Chọn `PackagePlan`, tính giá trị hóa đơn.
   * Tạo bản ghi `Invoice` (TransactionType = `NEW_REGISTRATION`, PaymentMethod = Tiền mặt / VietQR / POS, Status = `PAID`).
   * Tạo bản ghi `MemberSubscription` (Status = `ACTIVE`, tính `StartDate`, `EndDate`, `RemainingCheckInSessions`, sinh mã token `QrCode`).
   * Tạo bản ghi `Notification` chào mừng hội viên mới.
2. **Điểm danh hội viên vào phòng tập (UC03.1 & UC03.2):**
   * Quét mã `QrCode` từ camera (UC 3.1) hoặc nhập thủ công `UserName` / `Phone` của hội viên (UC 3.2).
   * Tra cứu `MemberSubscription` đang có trạng thái `ACTIVE` của hội viên.
   * Kiểm tra điều kiện: `EndDate >= Ngày hiện tại`, `RemainingCheckInSessions > 0`.
   * Trừ 1 lượt `RemainingCheckInSessions` (nếu gói tính theo lượt).
   * Ghi bản ghi vào bảng `CheckInLog` (`Status` = `SUCCESS` hoặc `DENIED`, kèm `DenialReason`).

---

## 2. MA TRẬN ÁNH XẠ SCHEMA VẬT LÝ VÀO CÁC MODEL OOP (PHYSICAL SCHEMA TO OOP MODELS)

Toàn bộ các thực thể liên quan đến 2 tính năng được ánh xạ trực tiếp từ [`doc/GymManagement_Physical_Model.sql`](../doc/GymManagement_Physical_Model.sql):

| Bảng CSDL (Table Name) | Tệp Tin Model OOP (Python) | Thuộc Tính Chính (OOP Fields) | Vai Trò Nghiệp Vụ Trong 2 Feature |
| :--- | :--- | :--- | :--- |
| **`Role`** | `UI/models/role.py` | `role_id: str`, `role_name: str` | Định danh quyền `MEMBER`, `ADMIN`. |
| **`User`** | `UI/models/user.py` | `username: str`, `role_id: str`, `full_name: str`, `phone: str`, `email: str`, `password_hash: str`, `gender: int`, `status: str`, `created_at: date` | Lưu hồ sơ cá nhân hội viên và nhân viên lễ tân xác nhận. |
| **`PackagePlan`** | `UI/models/package_plan.py` | `plan_id: str`, `name: str`, `description: str`, `duration_days: int`, `price: float`, `max_check_in_sessions: int`, `is_pt_included: int`, `total_pt_sessions: int`, `is_active: int` | Danh mục gói dịch vụ gym niêm yết. |
| **`MemberSubscription`** | `UI/models/member_subscription.py` | `subscription_id: str`, `qr_code: str`, `start_date: date`, `end_date: date`, `remaining_check_in_sessions: int`, `remaining_pt_sessions: int`, `freeze_start_date: date`, `freeze_end_date: date`, `status: str`, `created_at: date`, `username: str`, `assigned_pt_id: str`, `plan_id: str`, `pt_session_id: str` | Quản lý vòng đời thẻ tập, thời hạn, lượt check-in còn lại và chuỗi mã QR. |
| **`Invoice`** | `UI/models/invoice.py` | `invoice_id: str`, `invoice_code: str`, `transaction_type: str`, `subtotal_amount: float`, `total_amount: int`, `payment_method: str`, `status: str`, `refund_amount: float`, `refund_reason: str`, `paid_at: date`, `username: str`, `subscription_id: str`, `created_by_admin_id: str`, `check_in_log_id: str` | Hóa đơn thu tiền khi đăng ký gói hoặc thanh toán POS. |
| **`CheckInLog`** | `UI/models/check_in_log.py` | `check_in_id: str`, `check_in_at: datetime`, `status: str`, `denial_reason: str`, `subscription_id: str`, `verified_by_admin_id: str`, `username: str` | Nhật ký mỗi lượt vào phòng tập (hợp lệ hoặc từ chối). |
| **`Notification`** | `UI/models/notification.py` | `notification_id: str`, `title: str`, `message: str`, `is_read: bool`, `created_at: datetime`, `username: str` | Thông báo gửi tới hội viên khi kích hoạt gói thành công. |

---

## 3. CÂY THƯ MỤC CÁC TỆP TIN SỬ DỤNG (PROJECT DIRECTORY TREE)

```text
c:\Users\nguye\Desktop\Gym\
├── docker-compose.yml                                  # [TẠO MỚI] Cấu hình Docker chạy MySQL 8.0
├── init_mysql.sql                                      # [TẠO MỚI] DDL MySQL chuyển đổi 1:1 từ GymManagement_Physical_Model.sql
├── requirements.txt                                    # [CẬP NHẬT] Thêm mysql-connector-python>=8.2.0
│
└── UI/
    ├── task.md                                         # [TỆP NÀY] Kế hoạch chi tiết theo Physical Model
    │
    ├── database/                                       # [TẠO MỚI] Quản lý kết nối MySQL
    │   ├── __init__.py
    │   └── db_connection.py                            # Class DatabaseConnection (Singleton Connection Pool)
    │
    ├── models/                                         # [TẠO MỚI] Tầng Entity OOP tương ứng bảng SQL
    │   ├── __init__.py
    │   ├── base_model.py                               # Base Model hỗ trợ serialization/dict mapping
    │   ├── role.py                                     # Class Role (bảng Role)
    │   ├── user.py                                     # Class User (bảng User)
    │   ├── package_plan.py                             # Class PackagePlan (bảng PackagePlan)
    │   ├── member_subscription.py                      # Class MemberSubscription (bảng MemberSubscription)
    │   ├── invoice.py                                  # Class Invoice (bảng Invoice)
    │   ├── check_in_log.py                             # Class CheckInLog (bảng CheckInLog)
    │   └── notification.py                             # Class Notification (bảng Notification)
    │
    ├── repositories/                                   # [TẠO MỚI] Tầng Data Access Object (DAO Pattern)
    │   ├── __init__.py
    │   ├── base_repository.py                          # Generic BaseRepository[T]
    │   ├── user_repository.py                          # UserRepository (Tra cứu UserName, Phone, Email)
    │   ├── package_plan_repository.py                  # PackagePlanRepository (Lấy gói tập Active)
    │   ├── subscription_repository.py                  # SubscriptionRepository (Tìm gói Active, trừ CheckIn sessions)
    │   ├── invoice_repository.py                       # InvoiceRepository (Tạo hóa đơn, tìm theo mã)
    │   ├── check_in_repository.py                      # CheckInRepository (Lưu log, lấy danh sách hôm nay)
    │   └── notification_repository.py                  # NotificationRepository (Lưu thông báo)
    │
    ├── services/                                       # [TẠO MỚI] Tầng Nghiệp Vụ (Transaction & Rules)
    │   ├── __init__.py
    │   ├── member_service.py                           # MemberService: Đăng ký User + Subscription + Invoice + Notification
    │   └── checkin_service.py                          # CheckInService: Quét QR / SĐT -> Kiểm tra điều kiện -> Trừ lượt -> Ghi log
    │
    └── desktop_portal/                                 # [GIAO DIỆN PYQT6 CẦN TÍCH HỢP]
        ├── dialogs/
        │   └── register_member_dialog.py               # [CẬP NHẬT] Dùng MemberService để đăng ký & kích hoạt
        └── views/
            ├── checkin_counter_page.py                 # [CẬP NHẬT] Dùng CheckInService để kiểm tra và trừ lượt
            ├── members_page.py                         # [CẬP NHẬT] Tải danh sách User/Subscription thật từ CSDL
            └── pos_billing_page.py                     # [CẬP NHẬT] Tải danh mục PackagePlan và tạo Invoice vào CSDL
```

---

## 4. THIẾT KẾ CHI TIẾT CÁC LỚP OOP (CLASS DETAILED DESIGN)

### 4.1. Tầng Thực Thể (Domain Entities - `UI/models/`)

#### 1. `User` (`UI/models/user.py`)
```python
class User(BaseModel):
    def __init__(self, username: str, role_id: str, full_name: str, phone: str = None, 
                 email: str = None, password_hash: str = None, gender: int = 1, 
                 status: str = "ACTIVE", created_at: date = None):
        self.username = username
        self.role_id = role_id
        self.full_name = full_name
        self.phone = phone
        self.email = email
        self.password_hash = password_hash
        self.gender = gender
        self.status = status
        self.created_at = created_at or date.today()
    
    def is_active(self) -> bool:
        return self.status == "ACTIVE"
```

#### 2. `PackagePlan` (`UI/models/package_plan.py`)
```python
class PackagePlan(BaseModel):
    def __init__(self, plan_id: str, name: str, description: str = None, 
                 duration_days: int = 30, price: float = 0.0, 
                 max_check_in_sessions: int = None, is_pt_included: int = 0, 
                 total_pt_sessions: int = 0, is_active: int = 1):
        self.plan_id = plan_id
        self.name = name
        self.description = description
        self.duration_days = duration_days
        self.price = price
        self.max_check_in_sessions = max_check_in_sessions
        self.is_pt_included = is_pt_included
        self.total_pt_sessions = total_pt_sessions
        self.is_active = is_active
```

#### 3. `MemberSubscription` (`UI/models/member_subscription.py`)
```python
class MemberSubscription(BaseModel):
    def __init__(self, subscription_id: str, username: str, plan_id: str,
                 qr_code: str = None, start_date: date = None, end_date: date = None,
                 remaining_check_in_sessions: int = None, remaining_pt_sessions: int = 0,
                 freeze_start_date: date = None, freeze_end_date: date = None,
                 status: str = "ACTIVE", created_at: date = None,
                 assigned_pt_id: str = None, pt_session_id: str = None):
        self.subscription_id = subscription_id
        self.username = username
        self.plan_id = plan_id
        self.qr_code = qr_code
        self.start_date = start_date or date.today()
        self.end_date = end_date
        self.remaining_check_in_sessions = remaining_check_in_sessions
        self.remaining_pt_sessions = remaining_pt_sessions
        self.freeze_start_date = freeze_start_date
        self.freeze_end_date = freeze_end_date
        self.status = status
        self.created_at = created_at or date.today()
        self.assigned_pt_id = assigned_pt_id
        self.pt_session_id = pt_session_id

    def is_eligible_for_checkin(self, target_date: date = None) -> tuple[bool, str]:
        today = target_date or date.today()
        if self.status != "ACTIVE":
            return False, f"Gói tập đang ở trạng thái '{self.status}'"
        if self.end_date and self.end_date < today:
            return False, f"Gói tập đã hết hạn từ ngày {self.end_date}"
        if self.remaining_check_in_sessions is not None and self.remaining_check_in_sessions <= 0:
            return False, "Gói tập đã hết số lượt vào phòng"
        return True, "Hợp lệ"
```

#### 4. `CheckInLog` (`UI/models/check_in_log.py`)
```python
class CheckInLog(BaseModel):
    def __init__(self, check_in_id: str, subscription_id: str, username: str,
                 check_in_at: datetime = None, status: str = "SUCCESS", 
                 denial_reason: str = None, verified_by_admin_id: str = None):
        self.check_in_id = check_in_id
        self.subscription_id = subscription_id
        self.username = username
        self.check_in_at = check_in_at or datetime.now()
        self.status = status
        self.denial_reason = denial_reason
        self.verified_by_admin_id = verified_by_admin_id
```

#### 5. `Invoice` (`UI/models/invoice.py`)
```python
class Invoice(BaseModel):
    def __init__(self, invoice_id: str, invoice_code: str, username: str, 
                 subscription_id: str, subtotal_amount: float, total_amount: int, 
                 payment_method: str = "CASH", transaction_type: str = "NEW_REGISTRATION",
                 status: str = "PAID", paid_at: date = None, created_by_admin_id: str = None,
                 refund_amount: float = None, refund_reason: str = None, check_in_log_id: str = None):
        self.invoice_id = invoice_id
        self.invoice_code = invoice_code
        self.username = username
        self.subscription_id = subscription_id
        self.subtotal_amount = subtotal_amount
        self.total_amount = total_amount
        self.payment_method = payment_method
        self.transaction_type = transaction_type
        self.status = status
        self.paid_at = paid_at or date.today()
        self.created_by_admin_id = created_by_admin_id
        self.refund_amount = refund_amount
        self.refund_reason = refund_reason
        self.check_in_log_id = check_in_log_id
```

---

### 4.2. Tầng Nghiệp Vụ Xử Lý (Service Layer - `UI/services/`)

#### `MemberService` (`UI/services/member_service.py` - UC02.1 & UC05.1)
* **Phương thức:** `register_new_member(member_dto: dict, admin_username: str) -> tuple[bool, str, dict]`
* **Quy trình Transaction:**
  1. Kiểm tra định dạng `phone`, `email`.
  2. Kiểm tra `User` tồn tại qua `user_repository.find_by_phone(phone)` hoặc `find_by_username(username)`. Nếu trùng -> Rollback và trả về lỗi.
  3. Lấy thông tin `PackagePlan` từ `package_plan_repository.get_by_id(plan_id)`.
  4. Tính `EndDate = StartDate + timedelta(days=plan.duration_days)`.
  5. Sinh mã token `QrCode = f"GYM-QR-{username}-{uuid4().hex[:8]}"`.
  6. Lưu `User` mới vào bảng `User`.
  7. Lưu `MemberSubscription` mới vào bảng `MemberSubscription`.
  8. Lập `Invoice` trạng thái `PAID` vào bảng `Invoice`.
  9. Tạo thông báo chào mừng trong bảng `Notification`.
  10. `COMMIT` transaction và trả về đối tượng kết quả kèm mã QR để hiển thị lên UI.

#### `CheckInService` (`UI/services/checkin_service.py` - UC03.1 & UC03.2)
* **Phương thức:** `execute_checkin(search_key: str, method: str, admin_username: str) -> tuple[bool, str, dict]`
* **Quy trình:**
  1. Nếu `method == "QR_SCAN"`: Tìm kiếm subscription qua `subscription_repository.find_by_qrcode(search_key)`.
  2. Nếu `method == "MANUAL"`: Tìm kiếm `User` qua `user_repository.find_by_phone_or_username(search_key)`, sau đó lấy `MemberSubscription` mới nhất của User đó.
  3. Nếu không tìm thấy: Tạo `CheckInLog` thất bại (`status='DENIED'`, `denial_reason='Mã hoặc SĐT không tồn tại'`).
  4. Nếu tìm thấy: Gọi `subscription.is_eligible_for_checkin()`.
     * Nếu **Không hợp lệ**: Lưu `CheckInLog` thất bại (`status='DENIED'`, `denial_reason=lý_do`).
     * Nếu **Hợp lệ**:
       * Trừ lượt: nếu `remaining_check_in_sessions > 0` thì gọi `subscription_repository.decrement_sessions(sub_id)`.
       * Lưu `CheckInLog` thành công (`status='SUCCESS'`).
  5. Trả về thông tin hội viên (Họ tên, Gói tập, Số buổi còn lại, Hạn dùng) để UI cập nhật bảng hiển thị màu xanh/đỏ.

---

## 5. DDL CHUYỂN ĐỔI CHUẨN TỪ `GymManagement_Physical_Model.sql` SANG MYSQL

File `init_mysql.sql` sẽ được dựng từ chính xác các bảng liên quan trong `doc/GymManagement_Physical_Model.sql`:

```sql
-- 1. Bảng Role
CREATE TABLE IF NOT EXISTS Role (
    RoleID VARCHAR(10) NOT NULL,
    RoleName VARCHAR(50) NULL,
    PRIMARY KEY (RoleID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Bảng User
CREATE TABLE IF NOT EXISTS `User` (
    UserName VARCHAR(10) NOT NULL,
    RoleID VARCHAR(10) NOT NULL,
    FullName VARCHAR(50) NULL,
    Phone VARCHAR(20) NULL,
    Email VARCHAR(255) NULL,
    PasswordHash VARCHAR(255) NULL,
    Gender TINYINT NULL,
    Status VARCHAR(20) NULL,
    created_at DATE NULL,
    PRIMARY KEY (UserName),
    UNIQUE KEY UQ_User_Phone (Phone),
    KEY IX_User_RoleID (RoleID),
    CONSTRAINT FK_User_Role FOREIGN KEY (RoleID) REFERENCES Role (RoleID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Bảng PackagePlan
CREATE TABLE IF NOT EXISTS PackagePlan (
    PlanId VARCHAR(10) NOT NULL,
    Name VARCHAR(50) NULL,
    Description VARCHAR(255) NULL,
    DurationDays INT NULL,
    Price DECIMAL(19, 0) NULL,
    MaxCheckInSessions INT NULL,
    is_PtIncluded TINYINT NULL,
    TotalPtSessions INT NULL,
    is_Active TINYINT NULL,
    PRIMARY KEY (PlanId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Bảng MemberSubscription
CREATE TABLE IF NOT EXISTS MemberSubscription (
    SubscriptionId VARCHAR(10) NOT NULL,
    QrCode VARCHAR(255) NULL,
    StartDate DATE NULL,
    EndDate DATE NULL,
    RemainingCheckInSessions INT NULL,
    RemainingPtSessions INT NULL,
    FreezeStartDate DATE NULL,
    FreezeEndDate DATE NULL,
    Status VARCHAR(20) NULL,
    created_at DATE NULL,
    UserName VARCHAR(10) NOT NULL,
    AssignedPtId VARCHAR(10) NULL,
    PlanId VARCHAR(10) NOT NULL,
    PTSessionId VARCHAR(10) NULL,
    PRIMARY KEY (SubscriptionId),
    UNIQUE KEY UQ_MemberSubscription_QrCode (QrCode),
    KEY IX_MemberSubscription_UserName (UserName),
    CONSTRAINT FK_MemberSubscription_User FOREIGN KEY (UserName) REFERENCES `User` (UserName),
    CONSTRAINT FK_MemberSubscription_PackagePlan FOREIGN KEY (PlanId) REFERENCES PackagePlan (PlanId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Bảng CheckInLog
CREATE TABLE IF NOT EXISTS CheckInLog (
    CheckInId VARCHAR(10) NOT NULL,
    check_in_at DATETIME NULL,
    Status VARCHAR(20) NULL,
    DenialReason VARCHAR(100) NULL,
    SubscriptionId VARCHAR(10) NOT NULL,
    VerifiedByAdminId VARCHAR(10) NULL,
    UserName VARCHAR(10) NOT NULL,
    PRIMARY KEY (CheckInId),
    KEY IX_CheckInLog_Sub (SubscriptionId),
    KEY IX_CheckInLog_User (UserName),
    CONSTRAINT FK_CheckInLog_Subscription FOREIGN KEY (SubscriptionId) REFERENCES MemberSubscription (SubscriptionId),
    CONSTRAINT FK_CheckInLog_User FOREIGN KEY (UserName) REFERENCES `User` (UserName)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Bảng Invoice
CREATE TABLE IF NOT EXISTS Invoice (
    InvoiceId VARCHAR(10) NOT NULL,
    InvoiceCode VARCHAR(255) NULL,
    TransactionType VARCHAR(50) NULL,
    SubtotalAmount DECIMAL(19, 0) NULL,
    TotalAmount INT NULL,
    PaymentMethod VARCHAR(100) NULL,
    Status VARCHAR(20) NULL,
    RefundAmount DECIMAL(19, 0) NULL,
    RefundReason VARCHAR(255) NULL,
    paid_at DATETIME NULL,
    UserName VARCHAR(10) NOT NULL,
    SubscriptionId VARCHAR(10) NOT NULL,
    CreatedByAdminId VARCHAR(10) NULL,
    CheckInLogCheckInId VARCHAR(10) NULL,
    PRIMARY KEY (InvoiceId),
    UNIQUE KEY UQ_Invoice_InvoiceCode (InvoiceCode),
    CONSTRAINT FK_Invoice_User FOREIGN KEY (UserName) REFERENCES `User` (UserName),
    CONSTRAINT FK_Invoice_Subscription FOREIGN KEY (SubscriptionId) REFERENCES MemberSubscription (SubscriptionId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Bảng Notification
CREATE TABLE IF NOT EXISTS Notification (
    NotificationId VARCHAR(10) NOT NULL,
    Title VARCHAR(255) NOT NULL,
    Message VARCHAR(2000) NOT NULL,
    IsRead TINYINT(1) NOT NULL DEFAULT 0,
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UserName VARCHAR(10) NOT NULL,
    PRIMARY KEY (NotificationId),
    KEY IX_Notification_UserName_IsRead (UserName, IsRead),
    CONSTRAINT FK_Notification_User FOREIGN KEY (UserName) REFERENCES `User` (UserName) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 6. LỘ TRÌNH THỰC HIỆN CỤ THỂ (TASK ROADMAP)

| Mã Task | Hạng Mục | Mô Tả Thực Hiện | Tệp Tin Tác Động |
| :--- | :--- | :--- | :--- |
| **TSK-01** | **Docker & MySQL DDL** | Tạo `docker-compose.yml` và `init_mysql.sql` dựa trên `GymManagement_Physical_Model.sql` (bảng Role, User, PackagePlan, MemberSubscription, CheckInLog, Invoice, Notification + seed roles và gói tập mẫu). | `docker-compose.yml`, `init_mysql.sql` |
| **TSK-02** | **Cấu hình Thư viện** | Bổ sung `mysql-connector-python>=8.2.0` vào `requirements.txt`. | `requirements.txt` |
| **TSK-03** | **Kết nối CSDL Singleton** | Xây dựng class `DatabaseConnection` quản lý MySQL pool, commit/rollback transaction. | `UI/database/db_connection.py` |
| **TSK-04** | **OOP Models** | Viết 7 thực thể model tương ứng 7 bảng: `Role`, `User`, `PackagePlan`, `MemberSubscription`, `CheckInLog`, `Invoice`, `Notification`. | `UI/models/*.py` |
| **TSK-05** | **Tầng Repository** | Viết các lớp DAO: `UserRepository`, `PackagePlanRepository`, `SubscriptionRepository`, `InvoiceRepository`, `CheckInRepository`. | `UI/repositories/*.py` |
| **TSK-06** | **Tầng Nghiệp Vụ** | Xây dựng `MemberService` (đăng ký kèm thanh toán) và `CheckInService` (quét QR / nhập tay, trừ lượt, kiểm tra điều kiện). | `UI/services/*.py` |
| **TSK-07** | **Ghép Giao Diện Đăng Ký** | Kết nối `RegisterMemberDialog` với `MemberService` (lưu dữ liệu thật vào MySQL và hiển thị thông báo thành công kèm mã QR). | `UI/desktop_portal/dialogs/register_member_dialog.py` |
| **TSK-08** | **Ghép Giao Diện Điểm Danh** | Kết nối `CheckInCounterPage` với `CheckInService` (quét camera QR & tra cứu SĐT, trừ số buổi trên CSDL và hiển thị thẻ trạng thái). | `UI/desktop_portal/views/checkin_counter_page.py` |
| **TSK-09** | **Đồng Bộ Dữ Liệu Bảng** | Cập nhật `MembersPage` và `PosBillingPage` đọc dữ liệu thật từ MySQL thay vì `mock_data.py`. | `UI/desktop_portal/views/members_page.py`, `pos_billing_page.py` |
| **TSK-10** | **Kiểm Thử Tích Hợp** | Tạo script kiểm thử tự động quy trình: Tạo User -> Mua gói -> Quét QR điểm danh -> Kiểm tra trừ buổi trên CSDL. | `UI/tests/test_flow.py` |
