"""
HMS Test Suite — 20 Test Cases
Tests all major functionality: Auth, Rooms, Customers, Bookings, Reports
Run: cd src && python test_suite.py
"""
import os
import sys
import sqlite3
from datetime import date, timedelta

# Add src to path
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Remove old database to start fresh
db_path = os.path.join(src_dir, 'database', 'hotel.db')
if os.path.exists(db_path):
    os.remove(db_path)

from app import create_app
from seed_data import seed_database

# ── Helpers ──────────────────────────────────────────────
PASS = 0
FAIL = 0
RESULTS = []

def report(test_num: int, name: str, passed: bool, detail: str = ''):
    global PASS, FAIL
    status = '✅ PASS' if passed else '❌ FAIL'
    if passed:
        PASS += 1
    else:
        FAIL += 1
    line = f"  TC{test_num:02d} | {status} | {name}"
    if detail:
        line += f"  →  {detail}"
    print(line)
    RESULTS.append((test_num, name, passed, detail))


def login(client, email, password):
    """Login helper, returns response."""
    return client.post('/auth/login', data={'email': email, 'password': password}, follow_redirects=True)


def admin_login(client):
    return login(client, 'admin@group03hotel.com', 'admin123')


def staff_login(client):
    return login(client, 'staff@group03hotel.com', 'staff123')


def logout(client):
    return client.get('/auth/logout', follow_redirects=True)


# ── Setup ────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  🧪 HMS TEST SUITE — 20 Test Cases")
print("=" * 70)

app = create_app('testing')
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

# Seed database
seed_database()
print("  Database seeded with demo data.\n")

print("-" * 70)
print(f"  {'#':<5} | {'Status':<8} | {'Test Case Description'}")
print("-" * 70)

with app.test_client() as c:

    # ═══════════════════════════════════════════════
    # PHASE 1: AUTHENTICATION (TC01-TC05)
    # ═══════════════════════════════════════════════

    # TC01: Admin login succeeds
    rv = login(c, 'admin@group03hotel.com', 'admin123')
    passed = rv.status_code == 200 and 'Dashboard' in rv.data.decode('utf-8', errors='replace')
    report(1, "Admin login → Dashboard", passed,
           f"Status={rv.status_code}")
    logout(c)

    # TC02: Wrong password → stay on login
    rv = login(c, 'admin@group03hotel.com', 'wrongpassword')
    html = rv.data.decode('utf-8', errors='replace')
    passed = rv.status_code == 200 and ('không chính xác' in html or 'Login' in html)
    report(2, "Wrong password rejected", passed)
    logout(c)

    # TC03: Register new customer
    rv = c.post('/auth/register', data={
        'full_name': 'Test Customer',
        'email': 'test@customer.com',
        'password': 'test123',
        'confirm_password': 'test123',
        'security_question': 'Tên thú cưng?',
        'security_answer': 'mèo'
    }, follow_redirects=True)
    html = rv.data.decode('utf-8', errors='replace')
    passed = rv.status_code == 200 and ('thành công' in html or 'Login' in html)
    report(3, "Customer registration", passed)

    # TC04: Login with new customer → Rooms page
    rv = login(c, 'test@customer.com', 'test123')
    html = rv.data.decode('utf-8', errors='replace')
    passed = rv.status_code == 200 and ('Rooms' in html or 'Suites' in html)
    report(4, "Customer login → Rooms page", passed)
    logout(c)

    # TC05: Duplicate email registration fails
    rv = c.post('/auth/register', data={
        'full_name': 'Duplicate',
        'email': 'test@customer.com',
        'password': 'test123',
        'confirm_password': 'test123',
    }, follow_redirects=True)
    html = rv.data.decode('utf-8', errors='replace')
    passed = 'đã được sử dụng' in html
    report(5, "Duplicate email blocked", passed,
           "Correct error message shown" if passed else "Missing error")

    # ═══════════════════════════════════════════════
    # PHASE 2: ROOM MANAGEMENT (TC06-TC08)
    # ═══════════════════════════════════════════════

    admin_login(c)

    # TC06: Add new room
    rv = c.post('/rooms/add', data={
        'room_number': 'TEST-101',
        'room_name': 'Test Suite Deluxe',
        'room_type': 'Deluxe',
        'price_per_night': '250.00',
        'max_guests': '3',
        'floor': '1st Floor',
        'description': 'Test room for validation'
    }, follow_redirects=True)
    html = rv.data.decode('utf-8', errors='replace')
    passed = rv.status_code == 200 and 'TEST-101' in html
    report(6, "Add new room", passed,
           "Room TEST-101 visible" if passed else "Room not found in page")

    # TC07: Duplicate room number blocked
    rv = c.post('/rooms/add', data={
        'room_number': 'TEST-101',
        'room_name': 'Duplicate Room',
        'room_type': 'Standard',
        'price_per_night': '100.00',
        'max_guests': '2',
    }, follow_redirects=True)
    html = rv.data.decode('utf-8', errors='replace')
    passed = 'đã tồn tại' in html
    report(7, "Duplicate room number blocked", passed)

    # TC08: Update room status
    # Find room ID for TEST-101
    from models.room_model import RoomModel
    test_room = RoomModel.find_by_number('TEST-101')
    if test_room:
        rv = c.post(f'/rooms/status/{test_room["id"]}', data={'status': 'maintenance'},
                    follow_redirects=True)
        updated = RoomModel.find_by_id(test_room['id'])
        passed = updated and updated['status'] == 'maintenance'
        report(8, "Room status → maintenance", passed,
               f"Status={updated['status']}" if updated else "Room not found")
        # Reset to available for later booking tests
        c.post(f'/rooms/status/{test_room["id"]}', data={'status': 'available'})
    else:
        report(8, "Room status → maintenance", False, "Test room not found")

    logout(c)

    # ═══════════════════════════════════════════════
    # PHASE 3: CUSTOMER MANAGEMENT (TC09-TC10)
    # ═══════════════════════════════════════════════

    admin_login(c)

    # TC09: Add new customer (admin)
    rv = c.post('/customers/add', data={
        'full_name': 'Trần Văn B',
        'email': 'tranvanb@test.com',
        'phone': '+84 912 345 678',
        'id_card': '012345678901',
        'nationality': 'Vietnam'
    }, follow_redirects=True)
    html = rv.data.decode('utf-8', errors='replace')
    from models.customer_model import CustomerModel
    cust = CustomerModel.find_by_email('tranvanb@test.com')
    passed = cust is not None and cust['full_name'] == 'Trần Văn B'
    report(9, "Add customer (admin)", passed,
           f"ID={cust['id']}, Tier={cust['tier']}" if cust else "Not created")

    # TC10: Customer tier is Standard for new customer
    passed = cust is not None and cust['tier'] == 'Standard'
    report(10, "New customer tier = Standard", passed,
           f"Tier={cust['tier']}" if cust else "N/A")

    logout(c)

    # ═══════════════════════════════════════════════
    # PHASE 4: BOOKING WORKFLOW (TC11-TC16)
    # Use the TEST-101 room and Trần Văn B customer
    # created earlier to avoid seed data conflicts.
    # ═══════════════════════════════════════════════

    admin_login(c)

    # Get clean test data
    from models.booking_model import BookingModel
    from models.payment_model import PaymentModel

    test_room = RoomModel.find_by_number('TEST-101')
    test_cust = CustomerModel.find_by_email('tranvanb@test.com')

    today = date.today()
    checkin = (today + timedelta(days=1)).isoformat()
    checkout = (today + timedelta(days=4)).isoformat()  # 3 nights

    # TC11: Create booking (admin) — 3 nights at $250/night = $750
    if test_room and test_cust:
        test_room_id = test_room['id']
        test_customer_id = test_cust['id']
        test_room_price = test_room['price_per_night']

        rv = c.post('/bookings/add', data={
            'customer_id': test_customer_id,
            'room_id': test_room_id,
            'check_in_date': checkin,
            'check_out_date': checkout,
            'num_guests': 2,
            'notes': 'Test booking from test suite'
        }, follow_redirects=True)

        # Find the booking we just created for TEST-101
        all_bookings = BookingModel.get_all()
        booking = None
        for bk in all_bookings:
            if bk.get('room_id') == test_room_id and bk['status'] == 'pending':
                booking = bk
                break

        expected_total = test_room_price * 3  # 3 nights
        passed = (booking is not None
                  and booking['status'] == 'pending'
                  and abs(booking['total_amount'] - expected_total) < 0.01)
        report(11, "Create booking (3 nights)", passed,
               f"Code={booking['booking_code']}, Total=${booking['total_amount']:.2f}, Expected=${expected_total:.2f}" if booking else "No booking created")
        booking_id = booking['id'] if booking else None
    else:
        report(11, "Create booking (3 nights)", False, "Test room or customer not found")
        booking_id = None
        test_room_id = None

    # TC12: Approve booking (pending → confirmed)
    if booking_id:
        rv = c.post(f'/bookings/approve/{booking_id}', follow_redirects=True)
        booking = BookingModel.find_by_id(booking_id)
        passed = booking and booking['status'] == 'confirmed'
        report(12, "Approve booking → confirmed", passed,
               f"Status={booking['status']}" if booking else "Not found")
    else:
        report(12, "Approve booking → confirmed", False, "No booking to approve")

    # TC13: Check-in (confirmed → checked_in, room → occupied)
    if booking_id:
        rv = c.post(f'/bookings/checkin/{booking_id}', follow_redirects=True)
        booking = BookingModel.find_by_id(booking_id)
        room_after = RoomModel.find_by_id(test_room_id)
        b_ok = booking and booking['status'] == 'checked_in'
        r_ok = room_after and room_after['status'] == 'occupied'
        passed = b_ok and r_ok
        report(13, "Check-in → room occupied", passed,
               f"Booking={booking['status']}, Room={room_after['status']}" if booking and room_after else "Error")
    else:
        report(13, "Check-in → room occupied", False, "No booking")

    # TC14: Check-out (checked_in → checked_out, room → cleaning, payment created)
    if booking_id:
        rv = c.post(f'/bookings/checkout/{booking_id}', data={'payment_method': 'card'},
                    follow_redirects=True)
        booking = BookingModel.find_by_id(booking_id)
        room_after = RoomModel.find_by_id(test_room_id)
        payments = PaymentModel.get_by_booking(booking_id)
        b_ok = booking and booking['status'] == 'checked_out'
        r_ok = room_after and room_after['status'] == 'cleaning'
        p_ok = len(payments) > 0 and payments[0]['status'] == 'completed'
        passed = b_ok and r_ok and p_ok
        report(14, "Check-out → payment + room cleaning", passed,
               f"Payment=${payments[0]['amount']:.2f}, Method={payments[0]['payment_method']}" if p_ok else f"B={booking['status'] if booking else '?'}, R={room_after['status'] if room_after else '?'}, P={len(payments)}")
    else:
        report(14, "Check-out → payment + room cleaning", False, "No booking")

    # TC15: Booking overlap detection
    # Reset room to available first
    if test_room_id:
        c.post(f'/rooms/status/{test_room_id}', data={'status': 'available'})

    overlap_checkin = (today + timedelta(days=50)).isoformat()
    overlap_checkout = (today + timedelta(days=53)).isoformat()
    if test_room and test_cust:
        # First booking for overlap test
        c.post('/bookings/add', data={
            'customer_id': test_customer_id,
            'room_id': test_room_id,
            'check_in_date': overlap_checkin,
            'check_out_date': overlap_checkout,
            'num_guests': 1,
        }, follow_redirects=True)

        # Overlapping booking (should fail)
        overlap_mid = (today + timedelta(days=51)).isoformat()
        overlap_mid_out = (today + timedelta(days=55)).isoformat()
        rv = c.post('/bookings/add', data={
            'customer_id': test_customer_id,
            'room_id': test_room_id,
            'check_in_date': overlap_mid,
            'check_out_date': overlap_mid_out,
            'num_guests': 1,
        }, follow_redirects=True)
        html = rv.data.decode('utf-8', errors='replace')
        passed = 'đã được đặt' in html
        report(15, "Overlapping booking rejected", passed,
               "Overlap correctly detected" if passed else "Overlap NOT detected!")
    else:
        report(15, "Overlapping booking rejected", False, "No test room")

    # TC16: Cancel booking
    cancel_in = (today + timedelta(days=60)).isoformat()
    cancel_out = (today + timedelta(days=62)).isoformat()
    if test_room and test_cust:
        c.post('/bookings/add', data={
            'customer_id': test_customer_id,
            'room_id': test_room_id,
            'check_in_date': cancel_in,
            'check_out_date': cancel_out,
            'num_guests': 1,
        }, follow_redirects=True)

        # Find the newest pending booking for this room
        all_bk = BookingModel.get_all()
        cancel_booking = None
        for bk in all_bk:
            if bk.get('room_id') == test_room_id and bk['status'] == 'pending':
                cancel_booking = bk
                break

        if cancel_booking:
            rv = c.post(f'/bookings/cancel/{cancel_booking["id"]}', follow_redirects=True)
            updated = BookingModel.find_by_id(cancel_booking['id'])
            passed = updated and updated['status'] == 'cancelled'
            report(16, "Cancel booking", passed,
                   f"Status={updated['status']}" if updated else "Error")
        else:
            report(16, "Cancel booking", False, "No pending booking found")
    else:
        report(16, "Cancel booking", False, "No test room")

    logout(c)

    # ═══════════════════════════════════════════════
    # PHASE 5: CUSTOMER SELF-BOOKING (TC17-TC18)
    # ═══════════════════════════════════════════════

    # TC17: Customer self-booking from Rooms page
    # Use the seed customer (already has a customer record linked)
    login(c, 'elena.r@vogue-estates.com', 'customer123')

    # Find an available room (exclude TEST-101 which might be in 'cleaning' status)
    available_rooms = RoomModel.get_all(status='available')
    if available_rooms:
        cust_room = available_rooms[0]
        cust_in = (today + timedelta(days=100)).isoformat()
        cust_out = (today + timedelta(days=102)).isoformat()

        rv = c.post('/bookings/customer-book', data={
            'room_id': cust_room['id'],
            'check_in_date': cust_in,
            'check_out_date': cust_out,
            'num_guests': 1,
            'notes': 'Đặt phòng từ customer'
        }, follow_redirects=True)
        html = rv.data.decode('utf-8', errors='replace')
        passed = 'đã được gửi' in html or 'Yêu cầu đặt phòng' in html
        report(17, "Customer self-booking", passed,
               f"Room={cust_room['room_number']}" if passed else "Flash not found in response")
    else:
        report(17, "Customer self-booking", False, "No available rooms")

    # TC18: Customer can't access Dashboard
    rv = c.get('/dashboard', follow_redirects=True)
    html = rv.data.decode('utf-8', errors='replace')
    # Should be redirected to login (session cleared by admin_required)
    passed = 'Login' in html or 'đăng nhập' in html.lower()
    report(18, "Customer blocked from Dashboard", passed,
           "Correctly denied access" if passed else "Access was granted!")
    logout(c)

    # ═══════════════════════════════════════════════
    # PHASE 6: REPORTS & REVENUE (TC19-TC20)
    # ═══════════════════════════════════════════════

    admin_login(c)

    # TC19: Reports page loads with valid data
    rv = c.get('/reports/', follow_redirects=True)
    html = rv.data.decode('utf-8', errors='replace')
    passed = rv.status_code == 200 and 'Revenue' in html
    report(19, "Reports page loads", passed)

    # TC20: Revenue calculation matches payments
    # Directly verify from DB
    total_revenue = PaymentModel.get_total_revenue()
    all_payments = PaymentModel.get_recent(limit=100)
    manual_sum = sum(p['amount'] for p in all_payments if p['status'] == 'completed')

    passed = abs(total_revenue - manual_sum) < 0.01
    report(20, "Revenue = sum of payments", passed,
           f"Model Total=${total_revenue:.2f}, Manual Sum=${manual_sum:.2f}")

    logout(c)

# ── Summary ──────────────────────────────────────────
print("-" * 70)
print(f"\n  📊 Results:  {PASS} passed  /  {FAIL} failed  /  {PASS + FAIL} total")
if FAIL == 0:
    print("  🎉 ALL TESTS PASSED!")
else:
    print(f"\n  ⚠️  Failed tests:")
    for num, name, ok, detail in RESULTS:
        if not ok:
            print(f"     TC{num:02d}: {name} — {detail}")
print("=" * 70 + "\n")

sys.exit(0 if FAIL == 0 else 1)
