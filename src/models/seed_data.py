"""Seed data — Populate database with demo data matching the existing UI."""
from werkzeug.security import generate_password_hash
from database.db_manager import get_db


def seed_database():
    """Insert demo data into the database."""
    db = get_db()

    # Check if already seeded
    if db.count("SELECT COUNT(*) FROM users") > 0:
        print("Database already has data. Skipping seed.")
        return

    print("Seeding database with demo data...")

    # ========== USERS ==========
    admin_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
    staff_hash = generate_password_hash('staff123', method='pbkdf2:sha256')
    customer_hash = generate_password_hash('customer123', method='pbkdf2:sha256')
    answer_hash = generate_password_hash('hanoi', method='pbkdf2:sha256')

    db.execute_many(
        """INSERT INTO users (email, password_hash, full_name, role,
                              security_question, security_answer_hash)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [
            ('admin@group03hotel.com', admin_hash, 'Concierge Admin', 'admin',
             'Thành phố yêu thích?', answer_hash),
            ('staff@group03hotel.com', staff_hash, 'Nguyen Van A', 'staff',
             'Tên thú cưng?', generate_password_hash('mimi', method='pbkdf2:sha256')),
            ('elena.r@vogue-estates.com', customer_hash, 'Elena Rostova', 'customer',
             None, None),
            ('j.thorne@atelier.global', customer_hash, 'Julian Thorne', 'customer',
             None, None),
        ]
    )

    # ========== ROOMS ==========
    db.execute_many(
        """INSERT INTO rooms (room_number, room_name, room_type, price_per_night,
                              max_guests, status, description, floor, wing)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            ('Suite 801', 'The Royal Atelier', 'VIP', 2450.00, 4, 'occupied',
             'Presidential suite with panoramic city view', 'Penthouse', 'Main Tower'),
            ('Suite 802', 'The Grand Atelier', 'VIP', 3100.00, 4, 'cleaning',
             'Opulent suite with marble floors and gold details', 'Penthouse', 'Main Tower'),
            ('Suite 402', 'Industrial Loft 402', 'Deluxe', 720.00, 3, 'maintenance',
             'High-ceiling industrial loft with skyline view', '4th Floor', 'Skyline Wing'),
            ('Room 304', 'Superior Courtyard', 'Deluxe', 850.00, 2, 'available',
             'Classic double room with garden view', '3rd Floor', 'Garden Wing'),
            ('Room 212', 'Solitaire Studio', 'Single', 450.00, 1, 'available',
             'Minimalist luxury single for solo traveler', '2nd Floor', 'Business Floor'),
            ('Room 215', 'Classic Superior', 'Standard', 350.00, 2, 'available',
             'Comfortable standard room with modern amenities', '2nd Floor', 'Garden Wing'),
            ('Room 301', 'Garden View Deluxe', 'Deluxe', 780.00, 2, 'available',
             'Spacious deluxe room overlooking the garden', '3rd Floor', 'Garden Wing'),
            ('Room 501', 'Sky Lounge Suite', 'VIP', 1800.00, 3, 'available',
             'Contemporary VIP suite with lounge area', '5th Floor', 'Main Tower'),
        ]
    )

    # ========== CUSTOMERS ==========
    db.execute_many(
        """INSERT INTO customers (user_id, full_name, email, phone, id_card,
                                   nationality, tier, total_spent, total_bookings, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (3, 'Elena Rostova', 'elena.r@vogue-estates.com', '+84 912 345 678',
             '123456789012', 'Russia', 'Gold', 18200.00, 12, 'active'),
            (4, 'Julian Thorne', 'j.thorne@atelier.global', '+84 987 654 321',
             '987654321098', 'UK', 'Platinum', 42500.00, 24, 'active'),
            (None, 'Marcus Chen', 'chen.m@silicon-suites.com', '+84 909 123 456',
             '456789012345', 'Singapore', 'Silver', 9450.00, 5, 'dormant'),
            (None, 'Sarah Jenkins', 's.jenkins@pr-boutique.com', '+84 933 456 789',
             '789012345678', 'USA', 'Platinum', 61000.00, 32, 'active'),
            (None, 'Alexander Voss', 'a.voss@business.de', '+84 977 111 222',
             '111222333444', 'Germany', 'Gold', 22000.00, 15, 'active'),
            (None, 'Julianne Moore', 'j.moore@actors.com', '+84 966 777 888',
             '555666777888', 'USA', 'Platinum', 55000.00, 28, 'active'),
        ]
    )

    # ========== BOOKINGS ==========
    db.execute_many(
        """INSERT INTO bookings (booking_code, customer_id, room_id, check_in_date,
                                  check_out_date, num_guests, status, total_amount, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            ('BK-20261024-0001', 1, 1, '2026-10-24', '2026-10-28', 2,
             'pending', 9800.00, 'VIP Diamond Member - White lilies for arrival'),
            ('BK-20261024-0002', 2, 6, '2026-10-24', '2026-10-27', 1,
             'pending', 1050.00, 'First time requesting Suite upgrade'),
            ('BK-20261010-0001', 5, 1, '2026-10-10', '2026-10-14', 1,
             'confirmed', 9800.00, 'Executive Wing preference'),
            ('BK-20261008-0001', 6, 1, '2026-10-08', '2026-10-12', 2,
             'checked_in', 9800.00, 'Skyloft Suite - 2 guests'),
            ('BK-20261015-0001', 3, 6, '2026-10-15', '2026-10-19', 2,
             'cancelled', 1400.00, 'Cancelled by guest'),
        ]
    )

    # ========== PAYMENTS ==========
    db.execute_many(
        """INSERT INTO payments (booking_id, amount, payment_method, status, transaction_ref)
           VALUES (?, ?, ?, ?, ?)""",
        [
            (4, 9800.00, 'card', 'completed', 'TXN-20261008-001'),
            (5, 1400.00, 'transfer', 'refunded', 'REFUND-5'),
        ]
    )

    print("Database seeded successfully!")
    print("  - Admin login: admin@group03hotel.com / admin123")
    print("  - Staff login: staff@group03hotel.com / staff123")
    print("  - Customer login: elena.r@vogue-estates.com / customer123")
