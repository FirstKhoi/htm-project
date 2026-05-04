# 🏨 HMS Test Cases


---

## 1. LOGIN (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-LOGIN-001 | Auth | Login admin thành công | Account admin tồn tại trong DB | 1. Mở /auth/login 2. Nhập email=admin@group03hotel.com, pass=admin123 3. Click Login | Redirect /dashboard, flash "Welcome back, Concierge Admin!" | Critical |
| TC-LOGIN-002 | Auth | Login staff thành công | Account staff tồn tại | 1. Nhập email=staff@group03hotel.com, pass=staff123 2. Submit | Redirect /dashboard | Critical |
| TC-LOGIN-003 | Auth | Login customer thành công | Customer đã đăng ký | 1. Nhập email/pass customer 2. Submit | Redirect /rooms (không phải dashboard) | Critical |
| TC-LOGIN-004 | Auth | Login sai email | Không có account | 1. Nhập email=fake@test.com 2. Submit | Flash "No account found with that email address.", ở lại trang login | High |
| TC-LOGIN-005 | Auth | Login sai password | Account tồn tại | 1. Nhập đúng email, sai password 2. Submit | Flash "Incorrect password.", ở lại login | High |
| TC-LOGIN-006 | Auth | Login để trống email và password | — | 1. Không nhập gì 2. Submit | Flash "Please enter both email and password." | High |
| TC-LOGIN-007 | Auth | Login chỉ nhập email | — | 1. Nhập email, bỏ trống password 2. Submit | Flash "Please enter both email and password." | Medium |
| TC-LOGIN-008 | Auth | Login chỉ nhập password | — | 1. Bỏ trống email, nhập password 2. Submit | Flash "Please enter both email and password." | Medium |
| TC-LOGIN-009 | Auth | Login khi đã đăng nhập admin | Đã login admin | 1. Truy cập lại /auth/login | Auto redirect về /dashboard | Medium |
| TC-LOGIN-010 | Auth | Login khi đã đăng nhập customer | Đã login customer | 1. Truy cập lại /auth/login | Auto redirect về /rooms | Medium |

---

## 2. REGISTER (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-REG-001 | Auth | Register thành công đầy đủ thông tin | Email chưa được sử dụng | 1. Mở register 2. Nhập name=Nguyen Van A, email=new@test.com, pass=abc123, confirm=abc123, security Q/A 3. Submit | Flash "Registration successful!", redirect /auth/login. Tạo cả user (role=customer) + customer record | Critical |
| TC-REG-002 | Auth | Register không có security question | Email chưa dùng | 1. Nhập name, email, pass, confirm 2. Bỏ trống security Q/A 3. Submit | Vẫn register OK vì security Q/A là optional | High |
| TC-REG-003 | Auth | Register email đã tồn tại | Email đã dùng | 1. Nhập email đã có trong DB 2. Submit | Flash "This email address is already in use." | Critical |
| TC-REG-004 | Auth | Register password dưới 6 ký tự | — | 1. Nhập password="abc" 2. Submit | Flash "Password must be at least 6 characters long." | High |
| TC-REG-005 | Auth | Register confirm password không khớp | — | 1. pass="abc123", confirm="xyz789" 2. Submit | Flash "Password confirmation does not match." | High |
| TC-REG-006 | Auth | Register tên dưới 2 ký tự | — | 1. Nhập name="A" 2. Submit | Flash "Full name must be at least 2 characters long." | High |
| TC-REG-007 | Auth | Register email sai format | — | 1. Nhập email="khonghople" 2. Submit | Flash "Invalid email address." | High |
| TC-REG-008 | Auth | Register nhiều lỗi cùng lúc | — | 1. name="", email="bad", pass="ab", confirm="cd" 2. Submit | Flash tất cả lỗi cùng lúc | Medium |
| TC-REG-009 | Auth | Register email uppercase được normalize | — | 1. Nhập email="Test@GMAIL.COM" 2. Submit | DB lưu email="test@gmail.com" (lowercase) | Medium |
| TC-REG-010 | Auth | Register khi đã đăng nhập | Đã login | 1. Truy cập /auth/register | Auto redirect về dashboard hoặc rooms | Low |

---

## 3. FORGOT PASSWORD + LOGOUT (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-FORGOT-001 | Auth | Forgot password flow thành công | User có security question | 1. Nhập email 2. Trả lời đúng security question 3. Nhập pass mới + confirm 4. Submit | Flash "Password reset successful!", redirect login. Login bằng pass mới OK | Critical |
| TC-FORGOT-002 | Auth | Forgot password - email không tồn tại | — | 1. Nhập email không có trong DB 2. Submit | Flash "No account found with that email address." | High |
| TC-FORGOT-003 | Auth | Forgot password - user không có security Q | User không set security Q | 1. Nhập email user đó 2. Submit | Flash "This account does not have a security question set." | High |
| TC-FORGOT-004 | Auth | Forgot password - trả lời sai | User có security Q | 1. Nhập email 2. Trả lời sai answer 3. Submit | Flash "Incorrect answer." | High |
| TC-FORGOT-005 | Auth | Forgot password - new pass < 6 chars | Đã verify answer thành công | 1. Nhập new_password="ab" 2. Submit | Flash "Password must be at least 6 characters long." | High |
| TC-FORGOT-006 | Auth | Forgot password - confirm không khớp | Đã verify answer | 1. new_pass="abc123", confirm="xyz789" 2. Submit | Flash "Password confirmation does not match." | High |
| TC-FORGOT-007 | Auth | Forgot password - session expired | Không có reset_email trong session | 1. Trực tiếp POST step=verify_answer | Flash "Your session has expired. Please try again.", redirect forgot | Medium |
| TC-FORGOT-008 | Auth | Forgot password - security answer case insensitive | Answer lưu là "hanoi" | 1. Nhập "HANOI" hoặc "Hanoi" | Verify thành công (answer được lowercase trước khi check) | Medium |
| TC-FORGOT-009 | Auth | Logout thành công | Đã đăng nhập | 1. Truy cập /auth/logout | Session cleared, redirect /auth/login, flash "Logged out successfully." | High |
| TC-FORGOT-010 | Auth | Logout xóa sạch session | Đã đăng nhập admin | 1. Logout 2. Truy cập /dashboard | Redirect login (session không còn user_id) | High |

---

## 4. ROOM MANAGEMENT (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-ROOM-001 | Room | Tạo phòng thành công | Admin login | 1. Mở /rooms 2. Nhập room_number=R101, name=Test Room, type=Standard, price=200, max_guests=2 3. Submit | Phòng xuất hiện trong list, status=available, flash success | Critical |
| TC-ROOM-002 | Room | Tạo phòng - room_number trùng | Room R101 đã tồn tại | 1. Nhập room_number=R101 2. Submit | Flash "Room number R101 already exists." | Critical |
| TC-ROOM-003 | Room | Tạo phòng - thiếu room_number | Admin login | 1. Để trống room_number 2. Submit | Flash "Room number is required." | High |
| TC-ROOM-004 | Room | Tạo phòng - room_type không hợp lệ | Admin login | 1. Nhập type="Suite" (không trong VIP/Deluxe/Standard/Single) | Flash "Invalid room type." | High |
| TC-ROOM-005 | Room | Tạo phòng - price <= 0 | Admin login | 1. Nhập price=-100 2. Submit | Flash "Room price must be a positive number." | High |
| TC-ROOM-006 | Room | Tạo phòng - max_guests ngoài khoảng 1-10 | Admin login | 1. Nhập max_guests=15 2. Submit | Flash "Maximum guests must be between 1 and 10." | High |
| TC-ROOM-007 | Room | Update phòng thành công | Phòng tồn tại | 1. POST /rooms/update/{id} với room_name=New Name, price=300 | room_name và price cập nhật, flash "Room updated successfully." | High |
| TC-ROOM-008 | Room | Xóa phòng thành công | Phòng không có booking active | 1. POST /rooms/delete/{id} | Phòng bị xóa, flash success | High |
| TC-ROOM-009 | Room | Xóa phòng có active booking | Phòng có booking pending/confirmed/checked_in | 1. POST /rooms/delete/{id} | Flash "Unable to delete this room because it has active bookings." | Critical |
| TC-ROOM-010 | Room | Update room status thành công | Phòng tồn tại | 1. POST /rooms/status/{id} với status=maintenance | Status cập nhật thành maintenance, flash success | High |

---

## 5. BOOKING - TẠO ĐẶT PHÒNG (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-BKADD-001 | Booking | Admin tạo booking thành công | Customer + Room tồn tại, không overlap | 1. Chọn customer, room, checkin=2026-06-01, checkout=2026-06-05, guests=2 2. Submit | Booking tạo, status=pending, total=price*4 đêm, flash success | Critical |
| TC-BKADD-002 | Booking | Tạo booking - customer không tồn tại | — | 1. customer_id=9999 2. Submit | Flash "Customer not found." | High |
| TC-BKADD-003 | Booking | Tạo booking - room không tồn tại | — | 1. room_id=9999 2. Submit | Flash "Room not found." | High |
| TC-BKADD-004 | Booking | Tạo booking - thiếu ngày | — | 1. Để trống check_in_date và check_out_date 2. Submit | Flash "Check-in and check-out dates are required." | High |
| TC-BKADD-005 | Booking | Tạo booking - checkout <= checkin | — | 1. checkin=2026-06-05, checkout=2026-06-03 2. Submit | Flash "Check-out date must be after check-in date." | High |
| TC-BKADD-006 | Booking | Tạo booking - guests vượt max | Room max_guests=2 | 1. num_guests=5 2. Submit | Flash "Number of guests (5) exceeds room capacity (2)." | High |
| TC-BKADD-007 | Booking | Tạo booking - overlap hoàn toàn | Booking active 01-05/06 cùng room | 1. Tạo booking cùng room 01-05/06 | Flash "This room is already booked for the selected dates." | Critical |
| TC-BKADD-008 | Booking | Tạo booking - overlap một phần | Booking active 01-05/06 | 1. Tạo booking 03-08/06 cùng room | Flash overlap | Critical |
| TC-BKADD-009 | Booking | Tạo booking - adjacent dates (không overlap) | Booking active 01-05/06 | 1. Tạo booking 05-08/06 cùng room | Tạo thành công (checkout cũ = checkin mới → không overlap) | Critical |
| TC-BKADD-010 | Booking | Tính total_amount đúng | Room price=200/đêm | 1. Tạo booking checkin 01/06, checkout 05/06 (4 đêm) | total_amount = 200 * 4 = 800.0 | High |

---

## 6. BOOKING WORKFLOW (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-BKWF-001 | Booking | Approve booking (pending→confirmed) | Booking status=pending | 1. POST /bookings/approve/{id} | Status→confirmed, flash "approved successfully" | Critical |
| TC-BKWF-002 | Booking | Approve booking không phải pending | Status=confirmed | 1. POST /bookings/approve/{id} | Flash "Only bookings with Pending status can be approved." | High |
| TC-BKWF-003 | Booking | Check-in (confirmed→checked_in) | Status=confirmed | 1. POST /bookings/checkin/{id} | Booking status→checked_in, Room status→occupied | Critical |
| TC-BKWF-004 | Booking | Check-in không phải confirmed | Status=pending | 1. POST /bookings/checkin/{id} | Flash "Only approved bookings (Confirmed) can be checked in." | High |
| TC-BKWF-005 | Booking | Checkout thành công (cash) | Status=checked_in | 1. POST /bookings/checkout/{id} payment_method=cash | Booking→checked_out, Room→cleaning, Payment record tạo (completed), Customer tier update | Critical |
| TC-BKWF-006 | Booking | Checkout - invalid payment method | Status=checked_in | 1. payment_method="bitcoin" | Flash "Invalid payment method." | High |
| TC-BKWF-007 | Booking | Cancel booking pending | Status=pending | 1. POST /bookings/cancel/{id} | Status→cancelled | High |
| TC-BKWF-008 | Booking | Cancel booking checked_in → free room | Status=checked_in | 1. Cancel | Status→cancelled, Room→available | High |
| TC-BKWF-009 | Booking | Cancel booking đã có payment → refund | Booking có completed payment | 1. Cancel | Refund payment record tạo, status=refunded | Critical |
| TC-BKWF-010 | Booking | Cancel booking đã checkout/cancelled | Status=checked_out | 1. Cancel | Flash "Unable to cancel a completed or already cancelled booking." | High |

---

## 7. CUSTOMER SELF-BOOKING (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-CSBOOK-001 | Booking | Customer tự đặt phòng thành công | Customer login, room available | 1. POST /bookings/customer-book room_id, dates, guests 2. Submit | Booking tạo status=pending, flash "submitted! Please wait for admin confirmation." | Critical |
| TC-CSBOOK-002 | Booking | Customer đặt phòng - room unavailable | Room status=occupied | 1. Chọn room đó 2. Submit | Flash "This room is currently unavailable." | High |
| TC-CSBOOK-003 | Booking | Customer đặt phòng - room không tồn tại | — | 1. room_id=9999 | Flash "Room not found." | High |
| TC-CSBOOK-004 | Booking | Customer đặt phòng - customer profile missing | User login nhưng không có customer record | 1. Submit | Flash "Customer profile not found. Please contact an administrator." | High |
| TC-CSBOOK-005 | Booking | Customer đặt phòng - checkin trong quá khứ | — | 1. checkin = ngày hôm qua | Flash "Check-in date cannot be in the past." | High |
| TC-CSBOOK-006 | Booking | Customer đặt phòng - checkout <= checkin | — | 1. checkout <= checkin | Flash "Check-out date must be after check-in date." | High |
| TC-CSBOOK-007 | Booking | Customer đặt phòng - guests > max | Room max=2, guests=5 | 1. Submit | Flash "exceeds room capacity" | High |
| TC-CSBOOK-008 | Booking | Customer đặt phòng - overlap | Room đã có booking cùng ngày | 1. Submit | Flash "already booked for the selected dates." | Critical |
| TC-CSBOOK-009 | Booking | Customer đặt phòng - thiếu ngày | — | 1. Để trống dates 2. Submit | Flash "dates are required" | Medium |
| TC-CSBOOK-010 | Booking | Customer đặt phòng - concurrent overlap guard | 2 customer đặt cùng lúc cùng phòng | 1. 2 request đồng thời | 1 thành công, 1 flash overlap (enforce_overlap trong transaction) | Critical |

---

## 8. CUSTOMER MANAGEMENT (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-CUST-001 | Customer | Tạo customer thành công | Admin login | 1. POST /customers/add name=Nguyen A, email=a@test.com, phone=0901234567 | Customer tạo, tier=Standard, status=active, flash success | Critical |
| TC-CUST-002 | Customer | Tạo customer - tên < 2 ký tự | — | 1. name="A" 2. Submit | Flash "Full name must be at least 2 characters long." | High |
| TC-CUST-003 | Customer | Tạo customer - thiếu email | — | 1. Để trống email 2. Submit | Flash "Email is required." | High |
| TC-CUST-004 | Customer | Tạo customer - email trùng | Email đã tồn tại | 1. Nhập email trùng | Flash "This email address is already in use." | Critical |
| TC-CUST-005 | Customer | Update customer thành công | Customer tồn tại | 1. POST /customers/update/{id} full_name=New Name, phone=0909999999 | Thông tin cập nhật, flash "updated successfully" | High |
| TC-CUST-006 | Customer | Update customer - email trùng | Email mới đã thuộc customer khác | 1. Sửa email thành email đã có | Flash "already in use" | High |
| TC-CUST-007 | Customer | Xóa customer thành công | Customer không có active booking | 1. POST /customers/delete/{id} | Xóa, flash "deleted successfully" | High |
| TC-CUST-008 | Customer | Xóa customer có active booking | Có booking pending/confirmed | 1. POST /customers/delete/{id} | Flash "Unable to delete... active bookings." | Critical |
| TC-CUST-009 | Customer | Search customer theo tên | Có customer Alice | 1. GET /customers?search=Alice | Chỉ hiện customer tên chứa "Alice" | Medium |
| TC-CUST-010 | Customer | Export CSV | Có customers | 1. GET /customers/export | Download file CSV, header: ID,Full Name,Email,Phone,ID Card,Nationality,Tier,Total Spent,Total Bookings,Status,Created At | Medium |

---

## 9. TIER SYSTEM + PAYMENT + REPORTS (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-TIER-001 | Customer | Tier = Standard | spent=0, bookings=0 | Gọi calculate_tier(0, 0) | Return "Standard" | High |
| TC-TIER-002 | Customer | Tier = Silver | spent≥5000, bookings≥3 | Gọi calculate_tier(5000, 3) | Return "Silver" | High |
| TC-TIER-003 | Customer | Tier = Gold | spent≥20000, bookings≥10 | Gọi calculate_tier(20000, 10) | Return "Gold" | High |
| TC-TIER-004 | Customer | Tier = Platinum | spent≥50000, bookings≥20 | Gọi calculate_tier(50000, 20) | Return "Platinum" | High |
| TC-TIER-005 | Customer | Tier boundary - chưa đủ Silver | spent=4999, bookings=2 | Gọi calculate_tier(4999, 2) | Return "Standard" (chưa đạt cả 2 điều kiện) | High |
| TC-TIER-006 | Payment | Checkout tạo payment đúng | Booking checked_in, amount=800 | 1. Checkout method=card | Payment: amount=800, method=card, status=completed | Critical |
| TC-TIER-007 | Payment | Refund khi cancel có payment | Completed payment=800 | 1. Cancel booking | Refund record: amount=800, status=refunded, ref=REFUND-{id} | Critical |
| TC-TIER-008 | Reports | Dashboard metrics hiển thị đúng | Có data | 1. GET /dashboard | room_summary, pending_count, today_revenue, recent_bookings, today_checkins đều có | High |
| TC-TIER-009 | Reports | Revenue report có filter date | Payments nhiều ngày | 1. GET /reports?start=2026-01-01&end=2026-06-30 | Metrics chỉ tính trong khoảng ngày đó | High |
| TC-TIER-010 | Reports | Report không data - không crash | DB trống | 1. GET /reports | Revenue=0, Occupancy=0%, trang hiển thị bình thường | Medium |

---

## 10. SECURITY & AUTHORIZATION (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-SEC-001 | Security | POST không CSRF token → 403 | App running | 1. POST /auth/login không có csrf_token | HTTP 403 "Missing CSRF token." | Critical |
| TC-SEC-002 | Security | POST có CSRF token hợp lệ → OK | App running | 1. GET /auth/login lấy token 2. POST kèm csrf_token | Request xử lý bình thường (không 403) | Critical |
| TC-SEC-003 | Security | POST có CSRF token sai → 403 | App running | 1. POST với csrf_token="fake123" | HTTP 403 "Invalid CSRF token." | Critical |
| TC-SEC-004 | Security | Truy cập /dashboard không login | Chưa login | 1. GET /dashboard | Redirect /auth/login, flash "Please sign in" | High |
| TC-SEC-005 | Security | Customer truy cập /dashboard | Login customer | 1. GET /dashboard | Session clear, redirect login, flash "do not have permission" | High |
| TC-SEC-006 | Security | Customer POST /rooms/add | Login customer | 1. POST /rooms/add | Reject bởi admin_required decorator | High |
| TC-SEC-007 | Security | Customer POST /customers/delete | Login customer | 1. POST /customers/delete/1 | Reject bởi admin_required | High |
| TC-SEC-008 | Security | Password lưu dạng hash | — | 1. Register user 2. Kiểm tra DB | password_hash bắt đầu bằng "pbkdf2:sha256:", không phải plaintext | Critical |
| TC-SEC-009 | Security | Security answer lưu dạng hash | User có security Q/A | 1. Kiểm tra DB | security_answer_hash là hash, không phải plaintext | High |
| TC-SEC-010 | Security | Truy cập /reports không login | Chưa login | 1. GET /reports | Redirect /auth/login | High |
