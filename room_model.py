"""Room model — CRUD operations for the rooms table."""
from database.db_manager import get_db


class RoomModel:
    """Handles all database operations for rooms."""

    @staticmethod
    def create(room_number: str, room_name: str, room_type: str,
               price_per_night: float, max_guests: int = 2,
               description: str = None, image_url: str = None,
               floor: str = None, wing: str = None) -> int:
        """Create a new room and return the room ID."""
        db = get_db()
        return db.insert(
            """INSERT INTO rooms (room_number, room_name, room_type,
                                  price_per_night, max_guests, description,
                                  image_url, floor, wing)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (room_number, room_name, room_type, price_per_night,
             max_guests, description, image_url, floor, wing)
        )

    @staticmethod
    def find_by_id(room_id: int) -> dict | None:
        """Find a room by ID."""
        db = get_db()
        return db.fetch_one("SELECT * FROM rooms WHERE id = ?", (room_id,))

    @staticmethod
    def find_by_number(room_number: str) -> dict | None:
        """Find a room by room number."""
        db = get_db()
        return db.fetch_one(
            "SELECT * FROM rooms WHERE room_number = ?", (room_number,)
        )

    @staticmethod
    def get_all(status: str = None, room_type: str = None) -> list[dict]:
        """Get all rooms with optional filtering."""
        db = get_db()
        query = "SELECT * FROM rooms WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)
        if room_type:
            query += " AND room_type = ?"
            params.append(room_type)

        query += " ORDER BY room_number"
        return db.fetch_all(query, tuple(params))

    @staticmethod
    def update(room_id: int, **kwargs) -> None:
        """Update room fields. Pass only fields to update."""
        db = get_db()
        allowed_fields = {'room_number', 'room_name', 'room_type',
                          'price_per_night', 'max_guests', 'status',
                          'description', 'image_url', 'floor', 'wing'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [room_id]

        db.execute(
            f"UPDATE rooms SET {set_clause} WHERE id = ?",
            tuple(values)
        )

    @staticmethod
    def delete(room_id: int) -> bool:
        """Delete a room. Returns False if room has active bookings."""
        db = get_db()
        # Check for active bookings
        active_count = db.count(
            """SELECT COUNT(*) FROM bookings
               WHERE room_id = ? AND status NOT IN ('cancelled', 'checked_out')""",
            (room_id,)
        )
        if active_count > 0:
            return False

        db.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        return True

    @staticmethod
    def update_status(room_id: int, status: str) -> None:
        """Update room status."""
        db = get_db()
        db.execute(
            "UPDATE rooms SET status = ? WHERE id = ?",
            (status, room_id)
        )

    @staticmethod
    def get_status_summary() -> dict:
        """Get count of rooms by status."""
        db = get_db()
        rows = db.fetch_all(
            "SELECT status, COUNT(*) as count FROM rooms GROUP BY status"
        )
        summary = {'available': 0, 'occupied': 0, 'cleaning': 0, 'maintenance': 0}
        for row in rows:
            summary[row['status']] = row['count']
        summary['total'] = sum(summary.values())
        return summary
