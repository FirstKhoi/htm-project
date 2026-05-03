"""Booking model — CRUD, overlap detection, and checkout workflow."""
import sqlite3
from datetime import date, datetime
from database.db_manager import get_db


class BookingModel:

    @staticmethod
    def _generate_booking_code(conn: sqlite3.Connection | None = None) -> str:
        """Generate code: BK-YYYYMMDD-XXXX."""
        db = get_db()
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"BK-{today}-"
        query = "SELECT booking_code FROM bookings WHERE booking_code LIKE ? ORDER BY id DESC LIMIT 1"

        if conn is None:
            last = db.fetch_one(query, (f"{prefix}%",))
        else:
            row = conn.execute(query, (f"{prefix}%",)).fetchone()
            last = dict(row) if row else None

        num = int(last["booking_code"].split("-")[-1]) + 1 if last else 1
        return f"{prefix}{num:04d}"

    @staticmethod
    def _check_overlap_with_conn(conn, room_id, check_in, check_out,
                                  exclude_booking_id=None) -> bool:
        """Check overlap using existing connection."""
        query = """
            SELECT COUNT(*) FROM bookings
            WHERE room_id = ? AND status NOT IN ('cancelled', 'checked_out')
              AND check_in_date < ? AND check_out_date > ?
        """
        params = [room_id, check_out, check_in]
        if exclude_booking_id:
            query += " AND id != ?"
            params.append(exclude_booking_id)
        result = conn.execute(query, tuple(params)).fetchone()
        return (result[0] if result else 0) > 0

    @staticmethod
    def check_overlap(room_id: int, check_in: str, check_out: str,
                      exclude_booking_id: int = None) -> bool:
        """True if room has overlapping bookings for given dates."""
        conn = get_db().get_connection()
        try:
            return BookingModel._check_overlap_with_conn(
                conn, room_id, check_in, check_out, exclude_booking_id)
        finally:
            conn.close()

    @staticmethod
    def create(customer_id: int, room_id: int, check_in_date: str,
               check_out_date: str, num_guests: int, total_amount: float,
               notes: str = None, enforce_overlap: bool = False,
               max_retries: int = 3) -> int:
        """Create booking with overlap guard. Returns booking ID."""
        conn = get_db().get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE")

            if enforce_overlap and BookingModel._check_overlap_with_conn(
                    conn, room_id, check_in_date, check_out_date):
                raise ValueError("OVERLAP_BOOKING")

            for _ in range(max_retries):
                code = BookingModel._generate_booking_code(conn)
                try:
                    cursor = conn.execute(
                        """INSERT INTO bookings (booking_code, customer_id, room_id,
                                                 check_in_date, check_out_date, num_guests,
                                                 total_amount, notes)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (code, customer_id, room_id, check_in_date,
                         check_out_date, num_guests, total_amount, notes),
                    )
                    conn.commit()
                    return cursor.lastrowid
                except sqlite3.IntegrityError as exc:
                    if "booking_code" in str(exc).lower():
                        continue
                    raise

            raise RuntimeError("FAILED_TO_GENERATE_BOOKING_CODE")
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def checkout_booking(booking_id: int, payment_method: str) -> dict:
        """Atomic checkout: update booking + room + payment + customer tier."""
        from models.customer_model import CustomerModel

        method = (payment_method or "").strip().lower()
        if method not in {"cash", "card", "transfer"}:
            raise ValueError("INVALID_PAYMENT_METHOD")

        conn = get_db().get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE")

            row = conn.execute(
                """SELECT b.*, c.full_name as customer_name, r.room_number
                   FROM bookings b
                   JOIN customers c ON b.customer_id = c.id
                   JOIN rooms r ON b.room_id = r.id
                   WHERE b.id = ?""", (booking_id,)
            ).fetchone()

            if not row:
                raise ValueError("BOOKING_NOT_FOUND")
            booking = dict(row)
            if booking["status"] != "checked_in":
                raise ValueError("INVALID_STATUS")

            # Update booking status
            conn.execute(
                "UPDATE bookings SET status = 'checked_out', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (booking_id,))
            # Set room to cleaning
            conn.execute("UPDATE rooms SET status = 'cleaning' WHERE id = ?",
                         (booking["room_id"],))
            # Create payment
            conn.execute(
                """INSERT INTO payments (booking_id, amount, payment_method, status, transaction_ref)
                   VALUES (?, ?, ?, 'completed', NULL)""",
                (booking_id, booking["total_amount"], method))

            # Update customer tier
            cust = conn.execute(
                "SELECT total_spent, total_bookings FROM customers WHERE id = ?",
                (booking["customer_id"],)).fetchone()
            if cust:
                new_spent = cust["total_spent"] + booking["total_amount"]
                new_bookings = cust["total_bookings"] + 1
                new_tier = CustomerModel.calculate_tier(new_spent, new_bookings)
                conn.execute(
                    """UPDATE customers SET total_spent = ?, total_bookings = ?, tier = ?,
                       updated_at = CURRENT_TIMESTAMP WHERE id = ?""",
                    (new_spent, new_bookings, new_tier, booking["customer_id"]))

            conn.commit()
            return booking
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def find_by_id(booking_id: int) -> dict | None:
        """Find booking with customer and room details."""
        return get_db().fetch_one(
            """SELECT b.*, c.full_name as customer_name, c.email as customer_email,
                      c.tier as customer_tier,
                      r.room_number, r.room_name, r.room_type, r.price_per_night
               FROM bookings b
               JOIN customers c ON b.customer_id = c.id
               JOIN rooms r ON b.room_id = r.id
               WHERE b.id = ?""", (booking_id,))

    @staticmethod
    def get_all(status: str = None, search: str = None) -> list[dict]:
        """Get all bookings with optional filter."""
        query = """
            SELECT b.*, c.full_name as customer_name, c.email as customer_email,
                   c.tier as customer_tier, r.room_number, r.room_name, r.room_type
            FROM bookings b
            JOIN customers c ON b.customer_id = c.id
            JOIN rooms r ON b.room_id = r.id WHERE 1=1
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
        return get_db().fetch_all(query, tuple(params))

    @staticmethod
    def get_recent(limit: int = 5) -> list[dict]:
        return get_db().fetch_all(
            """SELECT b.*, c.full_name as customer_name, c.tier as customer_tier,
                      r.room_number, r.room_name, r.room_type
               FROM bookings b
               JOIN customers c ON b.customer_id = c.id
               JOIN rooms r ON b.room_id = r.id
               ORDER BY b.created_at DESC LIMIT ?""", (limit,))

    @staticmethod
    def update_status(booking_id: int, new_status: str):
        get_db().execute(
            "UPDATE bookings SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_status, booking_id))

    @staticmethod
    def get_pending_count() -> int:
        return get_db().count("SELECT COUNT(*) FROM bookings WHERE status = 'pending'")

    @staticmethod
    def get_today_checkins() -> list[dict]:
        """Bookings confirmed for check-in today."""
        return get_db().fetch_all(
            """SELECT b.*, c.full_name as customer_name, r.room_number, r.room_name
               FROM bookings b
               JOIN customers c ON b.customer_id = c.id
               JOIN rooms r ON b.room_id = r.id
               WHERE b.check_in_date = ? AND b.status = 'confirmed'
               ORDER BY b.created_at""", (date.today().isoformat(),))

    @staticmethod
    def calculate_total(price_per_night: float, check_in: str, check_out: str) -> float:
        nights = (date.fromisoformat(check_out) - date.fromisoformat(check_in)).days
        return nights * price_per_night