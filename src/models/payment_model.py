"""Payment model — CRUD operations for the payments table."""

from database.db_manager import get_db


class PaymentModel:
    """Handles all database operations for payments."""

    @staticmethod
    def create_refund(booking_id: int, amount: float) -> int:
        """Create a refund payment record."""
        db = get_db()
        return db.insert(
            """INSERT INTO payments (booking_id, amount, payment_method,
                                     status, transaction_ref)
               VALUES (?, ?, 'transfer', 'refunded', ?)""",
            (booking_id, amount, f"REFUND-{booking_id}"),
        )

    @staticmethod
    def get_by_booking(booking_id: int) -> list[dict]:
        """Get all payments for a booking."""
        db = get_db()
        return db.fetch_all(
            "SELECT * FROM payments WHERE booking_id = ? ORDER BY created_at DESC",
            (booking_id,),
        )

    @staticmethod
    def get_recent(
        limit: int = 10, start_date: str = None, end_date: str = None
    ) -> list[dict]:
        """Get recent payment activities, optionally filtered by date range."""
        db = get_db()
        query = """
            SELECT p.*, b.booking_code, c.full_name as customer_name,
                   r.room_number
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN customers c ON b.customer_id = c.id
            JOIN rooms r ON b.room_id = r.id
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND DATE(p.payment_date) >= DATE(?)"
            params.append(start_date)
        if end_date:
            query += " AND DATE(p.payment_date) <= DATE(?)"
            params.append(end_date)

        query += " ORDER BY p.created_at DESC LIMIT ?"
        params.append(limit)
        return db.fetch_all(query, tuple(params))

    @staticmethod
    def get_total_revenue(start_date: str = None, end_date: str = None) -> float:
        """Get total revenue, optionally filtered by date range."""
        db = get_db()
        query = "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'completed'"
        params = []

        if start_date:
            query += " AND DATE(payment_date) >= DATE(?)"
            params.append(start_date)
        if end_date:
            query += " AND DATE(payment_date) <= DATE(?)"
            params.append(end_date)

        return db.count(query, tuple(params))

    @staticmethod
    def get_today_revenue() -> float:
        """Get today's revenue."""
        db = get_db()
        return db.count(
            """SELECT COALESCE(SUM(amount), 0) FROM payments
               WHERE status = 'completed'
                 AND DATE(payment_date) = DATE('now')"""
        )

    @staticmethod
    def get_revenue_by_room_type(
        start_date: str = None, end_date: str = None
    ) -> list[dict]:
        """Get revenue breakdown by room type."""
        db = get_db()
        query = """
            SELECT r.room_type, COALESCE(SUM(p.amount), 0) as revenue
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN rooms r ON b.room_id = r.id
            WHERE p.status = 'completed'
        """
        params = []

        if start_date:
            query += " AND DATE(p.payment_date) >= DATE(?)"
            params.append(start_date)
        if end_date:
            query += " AND DATE(p.payment_date) <= DATE(?)"
            params.append(end_date)

        query += " GROUP BY r.room_type ORDER BY revenue DESC"
        return db.fetch_all(query, tuple(params))
