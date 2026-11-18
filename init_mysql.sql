-- ====================================================================
-- GYM MANAGEMENT SYSTEM - MYSQL 8.0 DDL & INITIAL SEED SCRIPT
-- Phù hợp 100% với Physical Data Model (doc/GymManagement_Physical_Model.sql)
-- Mã nguồn: Python 3.10.11 / MySQL 8.0 (InnoDB, UTF-8)
-- ====================================================================

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 1. XÓA BẢNG THEO THỨ TỰ TỪ BẢNG PHỤ THUỘC ĐẾN BẢNG GỐC
DROP TABLE IF EXISTS `Notification`;
DROP TABLE IF EXISTS `MemberBodyMetric`;
DROP TABLE IF EXISTS `Invoice`;
DROP TABLE IF EXISTS `CheckInLog`;
DROP TABLE IF EXISTS `MemberSubscription`;
DROP TABLE IF EXISTS `PTTrainingSession`;
DROP TABLE IF EXISTS `PTAvailability`;
DROP TABLE IF EXISTS `PackagePlan`;
DROP TABLE IF EXISTS `User`;
DROP TABLE IF EXISTS `Role`;

SET FOREIGN_KEY_CHECKS = 1;

-- --------------------------------------------------------------------
-- 2. TẠO CÁC BẢNG VẬT LÝ THEO CHUẨN DDL MYSQL 8.0
-- --------------------------------------------------------------------

-- 2.1. Bảng Role (Phân quyền: ADMIN, MEMBER, PT)
CREATE TABLE `Role` (
    `RoleID` VARCHAR(10) NOT NULL,
    `RoleName` VARCHAR(50) NULL,
    PRIMARY KEY (`RoleID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.2. Bảng User (Tài khoản người dùng: Quản trị viên, Hội viên, HLV)
-- Lưu ý: Từ khóa 'User' được bọc bằng backtick để tránh xung đột cú pháp MySQL
CREATE TABLE `User` (
    `UserName` VARCHAR(10) NOT NULL,
    `RoleID` VARCHAR(10) NOT NULL,
    `FullName` VARCHAR(50) NULL,
    `Phone` VARCHAR(20) NULL,
    `Email` VARCHAR(255) NULL,
    `PasswordHash` VARCHAR(255) NULL,
    `Gender` TINYINT NULL,
    `Status` VARCHAR(20) NULL DEFAULT 'ACTIVE',
    `created_at` DATE NULL,
    PRIMARY KEY (`UserName`),
    UNIQUE KEY `UQ_User_Phone` (`Phone`),
    CONSTRAINT `FK_User_Role` FOREIGN KEY (`RoleID`) REFERENCES `Role` (`RoleID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.3. Bảng PackagePlan (Danh mục gói tập niêm yết)
CREATE TABLE `PackagePlan` (
    `PlanId` VARCHAR(10) NOT NULL,
    `Name` VARCHAR(50) NULL,
    `Description` VARCHAR(255) NULL,
    `DurationDays` INT NULL,
    `Price` DECIMAL(19, 0) NULL,
    `MaxCheckInSessions` INT NULL,
    `is_PtIncluded` TINYINT DEFAULT 0,
    `TotalPtSessions` INT DEFAULT 0,
    `is_Active` TINYINT DEFAULT 1,
    PRIMARY KEY (`PlanId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.4. Bảng PTAvailability (Lịch rảnh của Huấn luyện viên PT)
CREATE TABLE `PTAvailability` (
    `AvailabilityId` VARCHAR(10) NOT NULL,
    `AvailableDate` DATE NULL,
    `StartTime` TIME NULL,
    `EndTime` TIME NULL,
    `is_Booked` TINYINT DEFAULT 0,
    `PtID` VARCHAR(10) NOT NULL,
    PRIMARY KEY (`AvailabilityId`),
    CONSTRAINT `FK_PTAvailability_User` FOREIGN KEY (`PtID`) REFERENCES `User` (`UserName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.5. Bảng PTTrainingSession (Ca tập 1-1 giữa Hội viên và PT)
CREATE TABLE `PTTrainingSession` (
    `PTSessionId` VARCHAR(10) NOT NULL,
    `SessionStartTime` DATETIME NULL,
    `SessionEndTime` DATETIME NULL,
    `Status` VARCHAR(20) NULL,
    `WorkoutNotes` VARCHAR(255) NULL,
    `RatingStars` TINYINT NULL,
    `ReviewComment` VARCHAR(255) NULL,
    `completed_at` DATETIME NULL,
    `MemberID` VARCHAR(10) NOT NULL,
    `PtID` VARCHAR(10) NOT NULL,
    `AvailabilityId` VARCHAR(10) NULL,
    PRIMARY KEY (`PTSessionId`),
    CONSTRAINT `FK_PTTrainingSession_Member` FOREIGN KEY (`MemberID`) REFERENCES `User` (`UserName`),
    CONSTRAINT `FK_PTTrainingSession_PT` FOREIGN KEY (`PtID`) REFERENCES `User` (`UserName`),
    CONSTRAINT `FK_PTTrainingSession_Availability` FOREIGN KEY (`AvailabilityId`) REFERENCES `PTAvailability` (`AvailabilityId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.6. Bảng MemberSubscription (Hợp đồng/Gói đăng ký của Hội viên)
CREATE TABLE `MemberSubscription` (
    `SubscriptionId` VARCHAR(10) NOT NULL,
    `QrCode` VARCHAR(255) NULL,
    `StartDate` DATE NULL,
    `EndDate` DATE NULL,
    `RemainingCheckInSessions` INT NULL,
    `RemainingPtSessions` INT NULL,
    `FreezeStartDate` DATE NULL,
    `FreezeEndDate` DATE NULL,
    `Status` VARCHAR(20) NULL DEFAULT 'ACTIVE',
    `created_at` DATE NULL,
    `UserName` VARCHAR(10) NOT NULL,
    `AssignedPtId` VARCHAR(10) NULL,
    `PlanId` VARCHAR(10) NOT NULL,
    `PTSessionId` VARCHAR(10) NULL,
    PRIMARY KEY (`SubscriptionId`),
    UNIQUE KEY `UQ_MemberSubscription_QrCode` (`QrCode`),
    CONSTRAINT `FK_MemberSubscription_User` FOREIGN KEY (`UserName`) REFERENCES `User` (`UserName`),
    CONSTRAINT `FK_MemberSubscription_AssignedPt` FOREIGN KEY (`AssignedPtId`) REFERENCES `User` (`UserName`),
    CONSTRAINT `FK_MemberSubscription_PackagePlan` FOREIGN KEY (`PlanId`) REFERENCES `PackagePlan` (`PlanId`),
    CONSTRAINT `FK_MemberSubscription_PTSession` FOREIGN KEY (`PTSessionId`) REFERENCES `PTTrainingSession` (`PTSessionId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.7. Bảng CheckInLog (Nhật ký điểm danh vào phòng tập)
CREATE TABLE `CheckInLog` (
    `CheckInId` VARCHAR(10) NOT NULL,
    `check_in_at` DATETIME NULL,
    `Status` VARCHAR(20) NULL,
    `DenialReason` VARCHAR(100) NULL,
    `SubscriptionId` VARCHAR(10) NOT NULL,
    `VerifiedByAdminId` VARCHAR(10) NULL,
    `UserName` VARCHAR(10) NOT NULL,
    PRIMARY KEY (`CheckInId`),
    CONSTRAINT `FK_CheckInLog_Subscription` FOREIGN KEY (`SubscriptionId`) REFERENCES `MemberSubscription` (`SubscriptionId`),
    CONSTRAINT `FK_CheckInLog_User` FOREIGN KEY (`UserName`) REFERENCES `User` (`UserName`),
    CONSTRAINT `FK_CheckInLog_Admin` FOREIGN KEY (`VerifiedByAdminId`) REFERENCES `User` (`UserName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.8. Bảng Invoice (Hóa đơn thanh toán)
CREATE TABLE `Invoice` (
    `InvoiceId` VARCHAR(10) NOT NULL,
    `InvoiceCode` VARCHAR(255) NULL,
    `TransactionType` VARCHAR(50) NULL,
    `SubtotalAmount` DECIMAL(19, 0) NULL,
    `TotalAmount` INT NULL,
    `PaymentMethod` VARCHAR(100) NULL,
    `Status` VARCHAR(20) NULL,
    `RefundAmount` DECIMAL(19, 0) NULL,
    `RefundReason` VARCHAR(255) NULL,
    `paid_at` DATETIME NULL,
    `UserName` VARCHAR(10) NOT NULL,
    `SubscriptionId` VARCHAR(10) NOT NULL,
    `CreatedByAdminId` VARCHAR(10) NULL,
    `CheckInLogCheckInId` VARCHAR(10) NULL,
    PRIMARY KEY (`InvoiceId`),
    UNIQUE KEY `UQ_Invoice_InvoiceCode` (`InvoiceCode`),
    CONSTRAINT `FK_Invoice_User` FOREIGN KEY (`UserName`) REFERENCES `User` (`UserName`),
    CONSTRAINT `FK_Invoice_Subscription` FOREIGN KEY (`SubscriptionId`) REFERENCES `MemberSubscription` (`SubscriptionId`),
    CONSTRAINT `FK_Invoice_Admin` FOREIGN KEY (`CreatedByAdminId`) REFERENCES `User` (`UserName`),
    CONSTRAINT `FK_Invoice_CheckInLog` FOREIGN KEY (`CheckInLogCheckInId`) REFERENCES `CheckInLog` (`CheckInId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.9. Bảng MemberBodyMetric (Chỉ số thể hình InBody của Hội viên)
CREATE TABLE `MemberBodyMetric` (
    `BodyMetricId` VARCHAR(10) NOT NULL,
    `WeightKg` DECIMAL(19, 0) NULL,
    `HeightCm` DECIMAL(19, 0) NULL,
    `SkeletalMuscleMass` DECIMAL(19, 0) NULL,
    `BodyFatPercentage` DECIMAL(19, 0) NULL,
    `Bmi` DECIMAL(19, 0) NULL,
    `Notes` VARCHAR(255) NULL,
    `measured_at` DATE NULL,
    `UserName` VARCHAR(10) NOT NULL,
    `PTSessionId` VARCHAR(10) NULL,
    `RecordedByPtId` VARCHAR(10) NULL,
    PRIMARY KEY (`BodyMetricId`),
    CONSTRAINT `FK_MemberBodyMetric_User` FOREIGN KEY (`UserName`) REFERENCES `User` (`UserName`),
    CONSTRAINT `FK_MemberBodyMetric_PTSession` FOREIGN KEY (`PTSessionId`) REFERENCES `PTTrainingSession` (`PTSessionId`),
    CONSTRAINT `FK_MemberBodyMetric_RecordedByPt` FOREIGN KEY (`RecordedByPtId`) REFERENCES `User` (`UserName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.10. Bảng Notification (Thông báo hệ thống)
CREATE TABLE `Notification` (
    `NotificationId` VARCHAR(10) NOT NULL,
    `Title` VARCHAR(255) NOT NULL,
    `Message` TEXT NOT NULL,
    `IsRead` TINYINT(1) NOT NULL DEFAULT 0,
    `CreatedAt` DATE NOT NULL DEFAULT (CURRENT_DATE),
    `UserName` VARCHAR(10) NOT NULL,
    PRIMARY KEY (`NotificationId`),
    KEY `IX_Notification_UserName_IsRead` (`UserName`, `IsRead`),
    CONSTRAINT `FK_Notification_User` FOREIGN KEY (`UserName`) REFERENCES `User` (`UserName`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------
-- 3. NẠP DỮ LIỆU BAN ĐẦU (SEED DATA NỀN TẢNG)
-- --------------------------------------------------------------------

-- 3.1. Roles
INSERT INTO `Role` (`RoleID`, `RoleName`) VALUES
('ADMIN', 'Quản Trị Viên'),
('MEMBER', 'Hội Viên Phòng Tập'),
('PT', 'Huấn Luyện Viên Cá Nhân');

-- 3.2. PackagePlan (5 Gói tập chuẩn từ mock_data.py)
INSERT INTO `PackagePlan` (`PlanId`, `Name`, `Description`, `DurationDays`, `Price`, `MaxCheckInSessions`, `is_PtIncluded`, `TotalPtSessions`, `is_Active`) VALUES
('PKG01', 'Gym Standard 1 Tháng', 'Tập luyện không giới hạn khung giờ, phòng tắm nóng lạnh, tủ locker tiêu chuẩn.', 30, 450000, 30, 0, 0, 1),
('PKG02', 'Gym Standard 3 Tháng', 'Tiết kiệm 150K, tặng 01 bình lắc GymPro, miễn phí đo InBody định kỳ.', 90, 1200000, 90, 0, 0, 1),
('PKG03', 'VIP Platinum 12 Tháng', 'Toàn quyền sử dụng Gym + Yoga + Xông hơi Sauna, tặng 02 buổi định hướng cùng PT.', 365, 4500000, 365, 0, 2, 1),
('PKG04', 'Gói HLV Kèm Riêng PT 1-1 (12 Buổi)', '1 kèm 1 giáo án cá nhân hóa, đo chỉ số InBody mỗi tuần, cam kết form chuẩn.', 60, 3600000, 12, 1, 12, 1),
('PKG05', 'Gói HLV Kèm Riêng PT 1-1 (24 Buổi)', 'Thực đơn dinh dưỡng chi tiết, theo dõi 24/7, cam kết tăng cơ giảm mỡ rõ rệt.', 90, 6800000, 24, 1, 24, 1);

-- 3.3. Tài khoản Quản trị viên (Admin) & Huấn luyện viên (PT) mẫu
INSERT INTO `User` (`UserName`, `RoleID`, `FullName`, `Phone`, `Email`, `PasswordHash`, `Gender`, `Status`, `created_at`) VALUES
('admin', 'ADMIN', 'Quản trị viên hệ thống', '0900000001', 'admin@gymsystem.vn', 'admin123', 1, 'ACTIVE', '2026-01-01'),
('pt_hung', 'PT', 'Nguyễn Văn Hưng', '0900000002', 'hung.pt@gymsystem.vn', 'pt123', 1, 'ACTIVE', '2026-01-01');

-- 3.4. Dữ liệu Hội viên mẫu (Hỗ trợ kiểm thử Điểm danh & Đăng ký gói ngay)
INSERT INTO `User` (`UserName`, `RoleID`, `FullName`, `Phone`, `Email`, `PasswordHash`, `Gender`, `Status`, `created_at`) VALUES
('nam.nguyen', 'MEMBER', 'Nguyễn Hoàng Nam', '0987654321', 'nam.nguyen@gmail.com', 'member123', 1, 'ACTIVE', '2026-01-15'),
('thao.tran', 'MEMBER', 'Trần Thị Thu Thảo', '0912345678', 'thao.tran@yahoo.com', 'member123', 0, 'ACTIVE', '2026-10-01');

-- 3.5. Hợp đồng Gói tập đang ACTIVE của Hội viên mẫu
INSERT INTO `MemberSubscription` (`SubscriptionId`, `QrCode`, `StartDate`, `EndDate`, `RemainingCheckInSessions`, `RemainingPtSessions`, `Status`, `created_at`, `UserName`, `AssignedPtId`, `PlanId`) VALUES
('SUB001', 'QR-HV1001-PKG03-ACTIVE', '2026-01-15', '2027-01-15', 350, 2, 'ACTIVE', '2026-01-15', 'nam.nguyen', 'pt_hung', 'PKG03'),
('SUB002', 'QR-HV1002-PKG04-ACTIVE', '2026-10-01', '2026-12-01', 8, 8, 'ACTIVE', '2026-10-01', 'thao.tran', 'pt_hung', 'PKG04');

-- 3.6. Hóa đơn mẫu cho Hội viên
INSERT INTO `Invoice` (`InvoiceId`, `InvoiceCode`, `TransactionType`, `SubtotalAmount`, `TotalAmount`, `PaymentMethod`, `Status`, `paid_at`, `UserName`, `SubscriptionId`, `CreatedByAdminId`) VALUES
('INV001', 'INV-20260115-001', 'PACKAGE_REGISTRATION', 4500000, 4500000, 'VIETQR', 'PAID', '2026-01-15 10:00:00', 'nam.nguyen', 'SUB001', 'admin'),
('INV002', 'INV-20261001-002', 'PACKAGE_REGISTRATION', 3600000, 3600000, 'CASH', 'PAID', '2026-10-01 09:30:00', 'thao.tran', 'SUB002', 'admin');
