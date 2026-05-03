"""Seed data — initial admin/staff users and rooms."""
from werkzeug.security import generate_password_hash
from database.db_manager import get_db


def seed_database():
    """Insert demo users + rooms on first run."""
    db = get_db()

    if db.count("SELECT COUNT(*) FROM users") > 0:
        print("Database already has data. Skipping seed.")
        return

    print("Seeding database with initial data...")

    admin_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
    staff_hash = generate_password_hash('staff123', method='pbkdf2:sha256')
    answer_hash = generate_password_hash('hanoi', method='pbkdf2:sha256')

    db.execute_many(
        """INSERT INTO users (email, password_hash, full_name, role,
                              security_question, security_answer_hash)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [
            ('admin@group03hotel.com', admin_hash, 'Concierge Admin', 'admin',
             'What is your favorite city?', answer_hash),
            ('staff@group03hotel.com', staff_hash, 'Nguyen Van A', 'staff',
             'What is your pet\'s name?',
             generate_password_hash('mimi', method='pbkdf2:sha256')),
        ]
    )

    db.execute_many(
        """INSERT INTO rooms (room_number, room_name, room_type, price_per_night,
                              max_guests, status, description, floor, wing)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            ('Suite 801', 'The Royal Atelier', 'VIP', 2450.00, 4, 'available',
             'Presidential suite with panoramic city view', 'Penthouse', 'Main Tower'),
            ('Suite 802', 'The Grand Atelier', 'VIP', 3100.00, 4, 'available',
             'Opulent suite with marble floors and gold details', 'Penthouse', 'Main Tower'),
            ('Suite 402', 'Industrial Loft 402', 'Deluxe', 720.00, 3, 'available',
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

    print("Database seeded successfully!")
    print("  - Admin:  admin@group03hotel.com / admin123")
    print("  - Staff:  staff@group03hotel.com / staff123")
    print("  (No customers — they register themselves)")
