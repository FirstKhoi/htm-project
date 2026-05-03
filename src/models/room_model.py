"""Room model — CRUD and status operations."""
from database.db_manager import get_db


class RoomModel:

    @staticmethod
    def create(room_number: str, room_name: str, room_type: str,
               price_per_night: float, max_guests: int = 2,
               description: str = None, image_url: str = None,
               floor: str = None, wing: str = None) -> int:
        """Create room, return ID."""
        return get_db().insert(
            """INSERT INTO rooms (room_number, room_name, room_type,
                                  price_per_night, max_guests, description,
                                  image_url, floor, wing)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (room_number, room_name, room_type, price_per_night,
             max_guests, description, image_url, floor, wing),
        )

    @staticmethod
    def find_by_id(room_id: int) -> dict | None:
        return get_db().fetch_one("SELECT * FROM rooms WHERE id = ?", (room_id,))

    @staticmethod
    def find_by_number(room_number: str) -> dict | None:
        return get_db().fetch_one("SELECT * FROM rooms WHERE room_number = ?",
                                  (room_number,))

    @staticmethod
    def get_all(status: str = None, room_type: str = None) -> list[dict]:
        """Get rooms with optional filter."""
        query = "SELECT * FROM rooms WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if room_type:
            query += " AND room_type = ?"
            params.append(room_type)
        query += " ORDER BY room_number"
        return get_db().fetch_all(query, tuple(params))

    @staticmethod
    def update(room_id: int, **kwargs):
        """Update room fields dynamically."""
        allowed = {"room_number", "room_name", "room_type", "price_per_night",
                    "max_guests", "status", "description", "image_url", "floor", "wing"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [room_id]
        get_db().execute(f"UPDATE rooms SET {set_clause} WHERE id = ?", tuple(values))

    @staticmethod
    def delete(room_id: int) -> bool:
        """Delete room. Returns False if it has active bookings."""
        db = get_db()
        active = db.count(
            """SELECT COUNT(*) FROM bookings
               WHERE room_id = ? AND status NOT IN ('cancelled', 'checked_out')""",
            (room_id,),
        )
        if active > 0:
            return False
        db.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        return True

    @staticmethod
    def update_status(room_id: int, status: str):
        get_db().execute("UPDATE rooms SET status = ? WHERE id = ?", (status, room_id))

    @staticmethod
    def get_status_summary() -> dict:
        """Count rooms by status."""
        rows = get_db().fetch_all(
            "SELECT status, COUNT(*) as count FROM rooms GROUP BY status"
        )
        summary = {"available": 0, "occupied": 0, "cleaning": 0, "maintenance": 0}
        for row in rows:
            summary[row["status"]] = row["count"]
        summary["total"] = sum(summary.values())
        return summary
