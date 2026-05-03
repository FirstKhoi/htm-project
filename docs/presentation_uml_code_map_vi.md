# UML to Code Map - HMS

## Mục đích

File này dùng để trả lời nhanh câu hỏi: **"Sơ đồ này map vào code nào?"**

## 1. Context DFD map vào đâu?

### Process 0: Hotel Management System
- `src/app.py`: tạo app, khởi tạo database, đăng ký blueprint, CSRF
- `src/controllers/`: nơi xử lý toàn bộ luồng nghiệp vụ
- `src/models/`: nơi xử lý business logic
- `src/database/`: nơi lưu schema và truy cập SQLite

### External actor: Admin / Staff
- `src/controllers/dashboard_controller.py`
- `src/controllers/room_controller.py`
- `src/controllers/booking_controller.py`
- `src/controllers/customer_controller.py`
- `src/controllers/report_controller.py`

### External actor: Customer
- `src/controllers/auth_controller.py`
- `src/controllers/room_controller.py`
- `src/controllers/booking_controller.py`

### Data store: SQLite Database
- `src/database/schema.sql`
- `src/database/db_manager.py`

## 2. Level 1 DFD map vào đâu?

### 1.0 Auth & Session
- Controller: `src/controllers/auth_controller.py`
- Model: `src/models/user_model.py`
- Model phụ: `src/models/customer_model.py`
- View: `src/templates/Login.html`

### 2.0 Room Management
- Controller: `src/controllers/room_controller.py`
- Model: `src/models/room_model.py`
- View: `src/templates/Rooms_Booking.html`

### 3.0 Booking Workflow
- Controller: `src/controllers/booking_controller.py`
- Model chính: `src/models/booking_model.py`
- Model liên quan: `src/models/room_model.py`, `src/models/customer_model.py`, `src/models/payment_model.py`
- View: `src/templates/Booking_Management.html`, `src/templates/Rooms_Booking.html`

### 4.0 Customer Management
- Controller: `src/controllers/customer_controller.py`
- Model: `src/models/customer_model.py`
- View: `src/templates/Customers.html`

### 5.0 Payment & Reporting
- Controller: `src/controllers/report_controller.py`
- Model: `src/models/payment_model.py`
- Model liên quan: `src/models/room_model.py`
- Query bổ sung: `get_db()` trong `src/database/db_manager.py`
- View: `src/templates/View_Reports.html`

## 3. Use Case map vào đâu?

### Login / Logout / Register / Forgot Password
- `src/controllers/auth_controller.py`
- `src/models/user_model.py`
- `src/models/customer_model.py`
- `src/templates/Login.html`

### View Dashboard
- `src/controllers/dashboard_controller.py`
- `src/models/room_model.py`
- `src/models/booking_model.py`
- `src/models/payment_model.py`
- `src/templates/Admin_Dashboard.html`

### Manage Rooms
- `src/controllers/room_controller.py`
- `src/models/room_model.py`
- `src/templates/Rooms_Booking.html`

### Manage Bookings
- `src/controllers/booking_controller.py`
- `src/models/booking_model.py`
- `src/models/payment_model.py`
- `src/templates/Booking_Management.html`

### Manage Customers
- `src/controllers/customer_controller.py`
- `src/models/customer_model.py`
- `src/templates/Customers.html`

### View Reports
- `src/controllers/report_controller.py`
- `src/models/payment_model.py`
- `src/templates/View_Reports.html`

### Browse Rooms / Request Booking
- `src/controllers/room_controller.py`
- `src/controllers/booking_controller.py`
- `src/models/room_model.py`
- `src/models/booking_model.py`
- `src/templates/Rooms_Booking.html`

## 4. Class Diagram map vào đâu?

### AppFactory
- `src/app.py`

### DatabaseManager
- `src/database/db_manager.py`

### UserModel
- `src/models/user_model.py`

### RoomModel
- `src/models/room_model.py`

### CustomerModel
- `src/models/customer_model.py`

### BookingModel
- `src/models/booking_model.py`

### PaymentModel
- `src/models/payment_model.py`

### Blueprint modules
- `auth_bp` -> `src/controllers/auth_controller.py`
- `dashboard_bp` -> `src/controllers/dashboard_controller.py`
- `rooms_bp` -> `src/controllers/room_controller.py`
- `bookings_bp` -> `src/controllers/booking_controller.py`
- `customers_bp` -> `src/controllers/customer_controller.py`
- `reports_bp` -> `src/controllers/report_controller.py`

## 5. ERD map vào đâu?

### users
- Schema: `src/database/schema.sql`
- Logic thao tác: `src/models/user_model.py`

### rooms
- Schema: `src/database/schema.sql`
- Logic thao tác: `src/models/room_model.py`

### customers
- Schema: `src/database/schema.sql`
- Logic thao tác: `src/models/customer_model.py`

### bookings
- Schema: `src/database/schema.sql`
- Logic thao tác: `src/models/booking_model.py`

### payments
- Schema: `src/database/schema.sql`
- Logic thao tác: `src/models/payment_model.py`

## 6. Câu trả lời cực nhanh khi bị hỏi

### Nếu bị hỏi: "Use case có đi xuống code thật không?"
Trả lời ngắn:

> Dạ có. Mỗi use case chính đều map xuống controller, model và template tương ứng. Ví dụ `Request Booking` map vào `booking_controller.py`, dùng `BookingModel`, `RoomModel`, `CustomerModel` và render từ `Rooms_Booking.html`.

### Nếu bị hỏi: "DFD level 1 thể hiện đúng code chưa?"
Trả lời ngắn:

> Dạ hiện tại đã khớp. Phần `Booking Workflow` trong code không chỉ tạo booking mà còn cập nhật trạng thái phòng, tạo payment/refund và cập nhật tier khách hàng; còn `Payment & Reporting` chủ yếu đọc dữ liệu để tính report.

### Nếu bị hỏi: "ERD có liên kết với business logic không?"
Trả lời ngắn:

> Dạ có. ERD mô tả các bảng `users`, `rooms`, `customers`, `bookings`, `payments`, còn phần thao tác thực tế nằm tương ứng ở các model `UserModel`, `RoomModel`, `CustomerModel`, `BookingModel`, `PaymentModel`.

### Nếu bị hỏi: "Class diagram có phải copy lý thuyết không?"
Trả lời ngắn:

> Dạ không. Class diagram hiện đã được chỉnh để bám implementation thật: `AppFactory` nằm ở `app.py`, `DatabaseManager` ở `db_manager.py`, các service model ở `src/models`, và phần controller đang được thể hiện đúng dưới dạng Flask blueprints.

## 7. Thứ tự trả lời an toàn khi bị hỏi bất kỳ sơ đồ nào

1. Nói sơ đồ đó mô tả phần nào của hệ thống.
2. Chỉ ngay controller hoặc model tương ứng trong code.
3. Nếu là UI thì nói thêm template.
4. Nếu là dữ liệu thì nói thêm `schema.sql`.

## 8. Câu chốt mẫu

> Điểm nhóm em cố gắng làm là không để UML đứng riêng với code. Mỗi sơ đồ đều có mapping xuống file implementation cụ thể, nên khi nhìn vào tài liệu có thể trace ngược lại được code thật trong project.
