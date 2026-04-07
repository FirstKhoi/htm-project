"""Booking model — CRUD operations + overlap detection for bookings table."""

from datetime import date, datetime

from database.db_manager import get_db


class BookingModel:
    """Handles all database operations for bookings."""

    @staticmethod
    def _generate_booking_code() -> str:
        """Generate a unique booking code: BK-YYYYMMDD-XXXX."""
        db = get_db()
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"BK-{today}-"

        # Find the last booking code for today
        last = db.fetch_one(
            "SELECT booking_code FROM bookings WHERE booking_code LIKE ? ORDER BY id DESC LIMIT 1",
            (f"{prefix}%",),
        )
        if last:
            last_num = int(last["booking_code"].split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"

    @staticmethod
    def check_overlap(
        room_id: int, check_in: str, check_out: str, exclude_booking_id: int = None
    ) -> bool:
        """
        Check if a room has overlapping bookings for the given dates.

        Two date ranges [A_start, A_end) and [B_start, B_end) overlap when:
        A_start < B_end AND B_start < A_end

        Returns True if there IS an overlap.
        """
        db = get_db()
        query = """
            SELECT COUNT(*) FROM bookings
            WHERE room_id = ?
              AND status NOT IN ('cancelled', 'checked_out')
              AND check_in_date < ?
              AND check_out_date > ?
        """
        params = [room_id, check_out, check_in]

        if exclude_booking_id:
            query += " AND id != ?"
            params.append(exclude_booking_id)

        return db.count(query, tuple(params)) > 0

    @staticmethod
    def create(
        customer_id: int,
        room_id: int,
        check_in_date: str,
        check_out_date: str,
        num_guests: int,
        total_amount: float,
        notes: str = None,
    ) -> int:
        """Create a new booking and return its ID."""
        db = get_db()
        booking_code = BookingModel._generate_booking_code()

        return db.insert(
            """INSERT INTO bookings (booking_code, customer_id, room_id,
                                     check_in_date, check_out_date, num_guests,
                                     total_amount, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                booking_code,
                customer_id,
                room_id,
                check_in_date,
                check_out_date,
                num_guests,
                total_amount,
                notes,
            ),
        )

    @staticmethod
    def find_by_id(booking_id: int) -> dict | None:
        """Find a booking by ID with customer and room details."""
        db = get_db()
        return db.fetch_one(
            """SELECT b.*, c.full_name as customer_name, c.email as customer_email,
                      c.tier as customer_tier,
                      r.room_number, r.room_name, r.room_type, r.price_per_night
               FROM bookings b
               JOIN customers c ON b.customer_id = c.id
               JOIN rooms r ON b.room_id = r.id
               WHERE b.id = ?""",
            (booking_id,),
        )

    @staticmethod
    def get_all(status: str = None, search: str = None) -> list[dict]:
        """Get all bookings with optional filtering."""
        db = get_db()
        query = """
            SELECT b.*, c.full_name as customer_name, c.email as customer_email,
                   c.tier as customer_tier,
                   r.room_number, r.room_name, r.room_type
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            JOIN rooms r ON b.room_id = r.id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND b.status = ?"
            params.append(status)

        if search:
            query += " AND (c.full_name LIKE ? OR r.room_number LIKE ? OR b.booking_code LIKE ?)"
            pattern = f"%{search}%"
            params.extend([pattern, pattern, pattern])

        query += " ORDER BY b.created_at DESC"
        return db.fetch_all(query, tuple(params))

    @staticmethod
    def get_recent(limit: int = 5) -> list[dict]:
        """Get the most recent bookings."""
        db = get_db()
        return db.fetch_all(
            """SELECT b.*, c.full_name as customer_name, c.tier as customer_tier,
                      r.room_number, r.room_name, r.room_type
               FROM bookings b
               JOIN customers c ON b.customer_id = c.id
               JOIN rooms r ON b.room_id = r.id
               ORDER BY b.created_at DESC LIMIT ?""",
            (limit,),
        )

    @staticmethod
    def update_status(booking_id: int, new_status: str) -> None:
        """Update booking status."""
        db = get_db()
        db.execute(
            """UPDATE bookings SET status = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (new_status, booking_id),
        )

    @staticmethod
    def get_pending_count() -> int:
        """Count of bookings awaiting approval."""
        db = get_db()
        return db.count("SELECT COUNT(*) FROM bookings WHERE status = 'pending'")

    @staticmethod
    def get_today_checkins() -> list[dict]:
        """Get bookings that should check in today."""
        db = get_db()
        today = date.today().isoformat()
        return db.fetch_all(
            """SELECT b.*, c.full_name as customer_name, r.room_number, r.room_name
               FROM bookings b
               JOIN customers c ON b.customer_id = c.id
               JOIN rooms r ON b.room_id = r.id
               WHERE b.check_in_date = ? AND b.status = 'confirmed'
               ORDER BY b.created_at""",
            (today,),
        )

    @staticmethod
    def calculate_total(price_per_night: float, check_in: str, check_out: str) -> float:
        """Calculate total amount from dates and price."""
        d_in = date.fromisoformat(check_in)
        d_out = date.fromisoformat(check_out)
        nights = (d_out - d_in).days
        return nights * price_per_night