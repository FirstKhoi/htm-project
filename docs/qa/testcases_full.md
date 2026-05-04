# 🏨 HMS Test Cases

---

## 1. LOGIN (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-LOGIN-001 | Auth | Admin login success | Admin account exists in DB | 1. Open /auth/login 2. Enter email=admin@group03hotel.com, pass=admin123 3. Click Login | Redirect to /dashboard, flash "Welcome back, Concierge Admin!" | Critical |
| TC-LOGIN-002 | Auth | Staff login success | Staff account exists | 1. Enter email=staff@group03hotel.com, pass=staff123 2. Submit | Redirect to /dashboard | Critical |
| TC-LOGIN-003 | Auth | Customer login success | Customer registered | 1. Enter customer email/pass 2. Submit | Redirect to /rooms (not dashboard) | Critical |
| TC-LOGIN-004 | Auth | Login wrong email | Account does not exist | 1. Enter email=fake@test.com 2. Submit | Flash "No account found with that email address.", stay on login page | High |
| TC-LOGIN-005 | Auth | Login wrong password | Account exists | 1. Enter correct email, wrong password 2. Submit | Flash "Incorrect password.", stay on login page | High |
| TC-LOGIN-006 | Auth | Login empty email and password | — | 1. Leave fields empty 2. Submit | Flash "Please enter both email and password." | High |
| TC-LOGIN-007 | Auth | Login empty password | — | 1. Enter email, leave password empty 2. Submit | Flash "Please enter both email and password." | Medium |
| TC-LOGIN-008 | Auth | Login empty email | — | 1. Leave email empty, enter password 2. Submit | Flash "Please enter both email and password." | Medium |
| TC-LOGIN-009 | Auth | Login when already logged in as admin | Logged in as admin | 1. Revisit /auth/login | Auto redirect to /dashboard | Medium |
| TC-LOGIN-010 | Auth | Login when already logged in as customer | Logged in as customer | 1. Revisit /auth/login | Auto redirect to /rooms | Medium |

---

## 2. REGISTER (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-REG-001 | Auth | Register success full info | Email not used | 1. Open register 2. Enter name=Nguyen Van A, email=new@test.com, pass=abc123, confirm=abc123, security Q/A 3. Submit | Flash "Registration successful!", redirect /auth/login. Creates user (role=customer) + customer record | Critical |
| TC-REG-002 | Auth | Register without security question | Email not used | 1. Enter name, email, pass, confirm 2. Leave security Q/A empty 3. Submit | Register OK since security Q/A is optional | High |
| TC-REG-003 | Auth | Register email already exists | Email in use | 1. Enter existing email 2. Submit | Flash "This email address is already in use." | Critical |
| TC-REG-004 | Auth | Register password < 6 chars | — | 1. Enter password="abc" 2. Submit | Flash "Password must be at least 6 characters long." | High |
| TC-REG-005 | Auth | Register confirm password mismatch | — | 1. pass="abc123", confirm="xyz789" 2. Submit | Flash "Password confirmation does not match." | High |
| TC-REG-006 | Auth | Register name < 2 chars | — | 1. Enter name="A" 2. Submit | Flash "Full name must be at least 2 characters long." | High |
| TC-REG-007 | Auth | Register invalid email format | — | 1. Enter email="invalid" 2. Submit | Flash "Invalid email address." | High |
| TC-REG-008 | Auth | Register multiple errors simultaneously | — | 1. name="", email="bad", pass="ab", confirm="cd" 2. Submit | Flash all errors at once | Medium |
| TC-REG-009 | Auth | Register uppercase email normalized | — | 1. Enter email="Test@GMAIL.COM" 2. Submit | DB stores email="test@gmail.com" (lowercase) | Medium |
| TC-REG-010 | Auth | Register when already logged in | Logged in | 1. Visit /auth/register | Auto redirect to dashboard or rooms | Low |

---

## 3. FORGOT PASSWORD + LOGOUT (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-FORGOT-001 | Auth | Forgot password flow success | User has security question | 1. Enter email 2. Answer correctly 3. Enter new pass + confirm 4. Submit | Flash "Password reset successful!", redirect login. Login with new pass OK | Critical |
| TC-FORGOT-002 | Auth | Forgot password - email not exists | — | 1. Enter non-existent email 2. Submit | Flash "No account found with that email address." | High |
| TC-FORGOT-003 | Auth | Forgot password - no security Q | User did not set security Q | 1. Enter user's email 2. Submit | Flash "This account does not have a security question set." | High |
| TC-FORGOT-004 | Auth | Forgot password - wrong answer | User has security Q | 1. Enter email 2. Enter wrong answer 3. Submit | Flash "Incorrect answer." | High |
| TC-FORGOT-005 | Auth | Forgot password - new pass < 6 chars | Answer verified | 1. Enter new_password="ab" 2. Submit | Flash "Password must be at least 6 characters long." | High |
| TC-FORGOT-006 | Auth | Forgot password - confirm mismatch | Answer verified | 1. new_pass="abc123", confirm="xyz789" 2. Submit | Flash "Password confirmation does not match." | High |
| TC-FORGOT-007 | Auth | Forgot password - session expired | No reset_email in session | 1. Directly POST step=verify_answer | Flash "Your session has expired. Please try again.", redirect forgot | Medium |
| TC-FORGOT-008 | Auth | Forgot password - security answer case insensitive | Saved answer "hanoi" | 1. Enter "HANOI" or "Hanoi" | Verify success (answer is lowercased before check) | Medium |
| TC-FORGOT-009 | Auth | Logout success | Logged in | 1. Visit /auth/logout | Session cleared, redirect /auth/login, flash "Logged out successfully." | High |
| TC-FORGOT-010 | Auth | Logout clears session entirely | Logged in as admin | 1. Logout 2. Visit /dashboard | Redirect login (session has no user_id) | High |

---

## 4. ROOM MANAGEMENT (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-ROOM-001 | Room | Create room success | Admin login | 1. Open /rooms 2. Enter room_number=R101, name=Test Room, type=Standard, price=200, max_guests=2 3. Submit | Room appears in list, status=available, flash success | Critical |
| TC-ROOM-002 | Room | Create room - number exists | Room R101 exists | 1. Enter room_number=R101 2. Submit | Flash "Room number R101 already exists." | Critical |
| TC-ROOM-003 | Room | Create room - missing number | Admin login | 1. Leave room_number empty 2. Submit | Flash "Room number is required." | High |
| TC-ROOM-004 | Room | Create room - invalid type | Admin login | 1. Enter type="Suite" (not in VIP/Deluxe/Standard/Single) | Flash "Invalid room type." | High |
| TC-ROOM-005 | Room | Create room - price <= 0 | Admin login | 1. Enter price=-100 2. Submit | Flash "Room price must be a positive number." | High |
| TC-ROOM-006 | Room | Create room - max_guests out of bounds (1-10) | Admin login | 1. Enter max_guests=15 2. Submit | Flash "Maximum guests must be between 1 and 10." | High |
| TC-ROOM-007 | Room | Update room success | Room exists | 1. POST /rooms/update/{id} with room_name=New Name, price=300 | room_name and price updated, flash "Room updated successfully." | High |
| TC-ROOM-008 | Room | Delete room success | Room has no active booking | 1. POST /rooms/delete/{id} | Room deleted, flash success | High |
| TC-ROOM-009 | Room | Delete room with active booking | Room has pending/confirmed/checked_in booking | 1. POST /rooms/delete/{id} | Flash "Unable to delete this room because it has active bookings." | Critical |
| TC-ROOM-010 | Room | Update room status success | Room exists | 1. POST /rooms/status/{id} with status=maintenance | Status updated to maintenance, flash success | High |

---

## 5. BOOKING - CREATION (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-BKADD-001 | Booking | Admin create booking success | Customer + Room exist, no overlap | 1. Select customer, room, checkin=2026-06-01, checkout=2026-06-05, guests=2 2. Submit | Booking created, status=pending, total=price*4 nights, flash success | Critical |
| TC-BKADD-002 | Booking | Create booking - customer not found | — | 1. customer_id=9999 2. Submit | Flash "Customer not found." | High |
| TC-BKADD-003 | Booking | Create booking - room not found | — | 1. room_id=9999 2. Submit | Flash "Room not found." | High |
| TC-BKADD-004 | Booking | Create booking - missing dates | — | 1. Leave check_in_date and check_out_date empty 2. Submit | Flash "Check-in and check-out dates are required." | High |
| TC-BKADD-005 | Booking | Create booking - checkout <= checkin | — | 1. checkin=2026-06-05, checkout=2026-06-03 2. Submit | Flash "Check-out date must be after check-in date." | High |
| TC-BKADD-006 | Booking | Create booking - guests > max | Room max_guests=2 | 1. num_guests=5 2. Submit | Flash "Number of guests (5) exceeds room capacity (2)." | High |
| TC-BKADD-007 | Booking | Create booking - full overlap | Active booking 01-05/06 same room | 1. Create booking same room 01-05/06 | Flash "This room is already booked for the selected dates." | Critical |
| TC-BKADD-008 | Booking | Create booking - partial overlap | Active booking 01-05/06 | 1. Create booking 03-08/06 same room | Flash overlap error | Critical |
| TC-BKADD-009 | Booking | Create booking - adjacent dates (no overlap) | Active booking 01-05/06 | 1. Create booking 05-08/06 same room | Success (old checkout = new checkin → no overlap) | Critical |
| TC-BKADD-010 | Booking | Calculate total_amount correctly | Room price=200/night | 1. Create booking checkin 01/06, checkout 05/06 (4 nights) | total_amount = 200 * 4 = 800.0 | High |

---

## 6. BOOKING WORKFLOW (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-BKWF-001 | Booking | Approve booking (pending→confirmed) | Booking status=pending | 1. POST /bookings/approve/{id} | Status→confirmed, flash "approved successfully" | Critical |
| TC-BKWF-002 | Booking | Approve booking not pending | Status=confirmed | 1. POST /bookings/approve/{id} | Flash "Only bookings with Pending status can be approved." | High |
| TC-BKWF-003 | Booking | Check-in (confirmed→checked_in) | Status=confirmed | 1. POST /bookings/checkin/{id} | Booking status→checked_in, Room status→occupied | Critical |
| TC-BKWF-004 | Booking | Check-in not confirmed | Status=pending | 1. POST /bookings/checkin/{id} | Flash "Only approved bookings (Confirmed) can be checked in." | High |
| TC-BKWF-005 | Booking | Checkout success (cash) | Status=checked_in | 1. POST /bookings/checkout/{id} payment_method=cash | Booking→checked_out, Room→cleaning, Payment record created (completed), Customer tier updated | Critical |
| TC-BKWF-006 | Booking | Checkout - invalid payment method | Status=checked_in | 1. payment_method="bitcoin" | Flash "Invalid payment method." | High |
| TC-BKWF-007 | Booking | Cancel booking pending | Status=pending | 1. POST /bookings/cancel/{id} | Status→cancelled | High |
| TC-BKWF-008 | Booking | Cancel booking checked_in → free room | Status=checked_in | 1. Cancel | Status→cancelled, Room→available | High |
| TC-BKWF-009 | Booking | Cancel booking with payment → refund | Booking has completed payment | 1. Cancel | Refund payment record created, status=refunded | Critical |
| TC-BKWF-010 | Booking | Cancel booking already checked_out/cancelled | Status=checked_out | 1. Cancel | Flash "Unable to cancel a completed or already cancelled booking." | High |

---

## 7. CUSTOMER SELF-BOOKING (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-CSBOOK-001 | Booking | Customer self-book success | Customer login, room available | 1. POST /bookings/customer-book room_id, dates, guests 2. Submit | Booking created status=pending, flash "submitted! Please wait for admin confirmation." | Critical |
| TC-CSBOOK-002 | Booking | Customer self-book - room unavailable | Room status=occupied | 1. Select that room 2. Submit | Flash "This room is currently unavailable." | High |
| TC-CSBOOK-003 | Booking | Customer self-book - room not found | — | 1. room_id=9999 | Flash "Room not found." | High |
| TC-CSBOOK-004 | Booking | Customer self-book - profile missing | User login but no customer record | 1. Submit | Flash "Customer profile not found. Please contact an administrator." | High |
| TC-CSBOOK-005 | Booking | Customer self-book - checkin in past | — | 1. checkin = yesterday | Flash "Check-in date cannot be in the past." | High |
| TC-CSBOOK-006 | Booking | Customer self-book - checkout <= checkin | — | 1. checkout <= checkin | Flash "Check-out date must be after check-in date." | High |
| TC-CSBOOK-007 | Booking | Customer self-book - guests > max | Room max=2, guests=5 | 1. Submit | Flash "exceeds room capacity" | High |
| TC-CSBOOK-008 | Booking | Customer self-book - overlap | Room already booked same dates | 1. Submit | Flash "already booked for the selected dates." | Critical |
| TC-CSBOOK-009 | Booking | Customer self-book - missing dates | — | 1. Leave dates empty 2. Submit | Flash "dates are required" | Medium |
| TC-CSBOOK-010 | Booking | Customer self-book - concurrent overlap guard | 2 customers book same room simultaneously | 1. 2 concurrent requests | 1 success, 1 flash overlap error (enforce_overlap in transaction) | Critical |

---

## 8. CUSTOMER MANAGEMENT (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-CUST-001 | Customer | Create customer success | Admin login | 1. POST /customers/add name=Nguyen A, email=a@test.com, phone=0901234567 | Customer created, tier=Standard, status=active, flash success | Critical |
| TC-CUST-002 | Customer | Create customer - name < 2 chars | — | 1. name="A" 2. Submit | Flash "Full name must be at least 2 characters long." | High |
| TC-CUST-003 | Customer | Create customer - missing email | — | 1. Leave email empty 2. Submit | Flash "Email is required." | High |
| TC-CUST-004 | Customer | Create customer - duplicate email | Email exists | 1. Enter existing email | Flash "This email address is already in use." | Critical |
| TC-CUST-005 | Customer | Update customer success | Customer exists | 1. POST /customers/update/{id} full_name=New Name, phone=0909999999 | Info updated, flash "updated successfully" | High |
| TC-CUST-006 | Customer | Update customer - duplicate email | New email belongs to another customer | 1. Change email to existing one | Flash "already in use" | High |
| TC-CUST-007 | Customer | Delete customer success | Customer has no active booking | 1. POST /customers/delete/{id} | Deleted, flash "deleted successfully" | High |
| TC-CUST-008 | Customer | Delete customer with active booking | Has pending/confirmed booking | 1. POST /customers/delete/{id} | Flash "Unable to delete... active bookings." | Critical |
| TC-CUST-009 | Customer | Search customer by name | Customer Alice exists | 1. GET /customers?search=Alice | Only shows customer whose name contains "Alice" | Medium |
| TC-CUST-010 | Customer | Export CSV | Customers exist | 1. GET /customers/export | Download CSV file, header: ID,Full Name,Email,Phone,ID Card,Nationality,Tier,Total Spent,Total Bookings,Status,Created At | Medium |

---

## 9. TIER SYSTEM + PAYMENT + REPORTS (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-TIER-001 | Customer | Tier = Standard | spent=0, bookings=0 | Call calculate_tier(0, 0) | Return "Standard" | High |
| TC-TIER-002 | Customer | Tier = Silver | spent≥5000, bookings≥3 | Call calculate_tier(5000, 3) | Return "Silver" | High |
| TC-TIER-003 | Customer | Tier = Gold | spent≥20000, bookings≥10 | Call calculate_tier(20000, 10) | Return "Gold" | High |
| TC-TIER-004 | Customer | Tier = Platinum | spent≥50000, bookings≥20 | Call calculate_tier(50000, 20) | Return "Platinum" | High |
| TC-TIER-005 | Customer | Tier boundary - not enough for Silver | spent=4999, bookings=2 | Call calculate_tier(4999, 2) | Return "Standard" (did not meet both conditions) | High |
| TC-TIER-006 | Payment | Checkout creates correct payment | Booking checked_in, amount=800 | 1. Checkout method=card | Payment: amount=800, method=card, status=completed | Critical |
| TC-TIER-007 | Payment | Refund on cancel with payment | Completed payment=800 | 1. Cancel booking | Refund record: amount=800, status=refunded, ref=REFUND-{id} | Critical |
| TC-TIER-008 | Reports | Dashboard metrics display correctly | Data exists | 1. GET /dashboard | room_summary, pending_count, today_revenue, recent_bookings, today_checkins all present | High |
| TC-TIER-009 | Reports | Revenue report with date filter | Payments across days | 1. GET /reports?start=2026-01-01&end=2026-06-30 | Metrics calculated only within that date range | High |
| TC-TIER-010 | Reports | Report empty data - no crash | DB is empty | 1. GET /reports | Revenue=0, Occupancy=0%, page displays normally | Medium |

---

## 10. SECURITY & AUTHORIZATION (10 TC)

| TC_ID | Module | Title | Precondition | Steps | Expected Result | Priority |
|---|---|---|---|---|---|---|
| TC-SEC-001 | Security | POST missing CSRF token → 403 | App running | 1. POST /auth/login without csrf_token | HTTP 403 "Missing CSRF token." | Critical |
| TC-SEC-002 | Security | POST valid CSRF token → OK | App running | 1. GET /auth/login to get token 2. POST with csrf_token | Request processes normally (no 403) | Critical |
| TC-SEC-003 | Security | POST invalid CSRF token → 403 | App running | 1. POST with csrf_token="fake123" | HTTP 403 "Invalid CSRF token." | Critical |
| TC-SEC-004 | Security | Access /dashboard without login | Not logged in | 1. GET /dashboard | Redirect to /auth/login, flash "Please sign in" | High |
| TC-SEC-005 | Security | Customer access /dashboard | Logged in as customer | 1. GET /dashboard | Session cleared, redirect login, flash "do not have permission" | High |
| TC-SEC-006 | Security | Customer POST /rooms/add | Logged in as customer | 1. POST /rooms/add | Rejected by admin_required decorator | High |
| TC-SEC-007 | Security | Customer POST /customers/delete | Logged in as customer | 1. POST /customers/delete/1 | Rejected by admin_required | High |
| TC-SEC-008 | Security | Password stored as hash | — | 1. Register user 2. Check DB | password_hash starts with "pbkdf2:sha256:", not plaintext | Critical |
| TC-SEC-009 | Security | Security answer stored as hash | User has security Q/A | 1. Check DB | security_answer_hash is hashed, not plaintext | High |
| TC-SEC-010 | Security | Access /reports without login | Not logged in | 1. GET /reports | Redirect to /auth/login | High |
