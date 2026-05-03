"""Customer model — CRUD, tier system, and statistics."""
from database.db_manager import get_db


class CustomerModel:

    @staticmethod
    def create(full_name: str, email: str, phone: str = None,
               id_card: str = None, nationality: str = "Vietnam",
               user_id: int = None) -> int:
        """Create customer, return ID."""
        return get_db().insert(
            """INSERT INTO customers (user_id, full_name, email, phone, id_card, nationality)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, full_name.strip(), email.lower().strip(),
             phone, id_card, nationality),
        )

    @staticmethod
    def find_by_id(customer_id: int) -> dict | None:
        return get_db().fetch_one("SELECT * FROM customers WHERE id = ?", (customer_id,))

    @staticmethod
    def find_by_email(email: str) -> dict | None:
        return get_db().fetch_one("SELECT * FROM customers WHERE email = ?",
                                  (email.lower().strip(),))

    @staticmethod
    def get_paginated(page: int = 1, per_page: int = 10,
                      search: str = None) -> tuple[list[dict], int]:
        """Paginated customer list. Returns (rows, total_count)."""
        db = get_db()
        offset = (page - 1) * per_page

        if search:
            pattern = f"%{search}%"
            where = "WHERE full_name LIKE ? OR email LIKE ? OR phone LIKE ?"
            total = db.count(f"SELECT COUNT(*) FROM customers {where}",
                             (pattern, pattern, pattern))
            rows = db.fetch_all(
                f"SELECT * FROM customers {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (pattern, pattern, pattern, per_page, offset),
            )
        else:
            total = db.count("SELECT COUNT(*) FROM customers")
            rows = db.fetch_all(
                "SELECT * FROM customers ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (per_page, offset),
            )
        return rows, total

    @staticmethod
    def get_all() -> list[dict]:
        return get_db().fetch_all("SELECT * FROM customers ORDER BY created_at DESC")

    @staticmethod
    def update(customer_id: int, **kwargs):
        """Update customer fields dynamically."""
        allowed = {"full_name", "email", "phone", "id_card", "nationality",
                    "tier", "status", "total_spent", "total_bookings"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return

        if "email" in updates and updates["email"]:
            updates["email"] = updates["email"].lower().strip()

        updates["updated_at"] = "CURRENT_TIMESTAMP"
        set_parts, values = [], []
        for k, v in updates.items():
            if v == "CURRENT_TIMESTAMP":
                set_parts.append(f"{k} = CURRENT_TIMESTAMP")
            else:
                set_parts.append(f"{k} = ?")
                values.append(v)

        values.append(customer_id)
        get_db().execute(
            f"UPDATE customers SET {', '.join(set_parts)} WHERE id = ?", tuple(values)
        )

    @staticmethod
    def delete(customer_id: int) -> bool:
        """Delete customer. Returns False if they have active bookings."""
        db = get_db()
        active = db.count(
            """SELECT COUNT(*) FROM bookings
               WHERE customer_id = ? AND status NOT IN ('cancelled', 'checked_out')""",
            (customer_id,),
        )
        if active > 0:
            return False
        db.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        return True

    @staticmethod
    def calculate_tier(total_spent: float, total_bookings: int) -> str:
        """Auto-tier based on spending and booking count."""
        if total_spent >= 50000 and total_bookings >= 20:
            return "Platinum"
        elif total_spent >= 20000 and total_bookings >= 10:
            return "Gold"
        elif total_spent >= 5000 and total_bookings >= 3:
            return "Silver"
        return "Standard"

    @staticmethod
    def get_stats() -> dict:
        """Aggregate customer statistics."""
        db = get_db()
        total = db.count("SELECT COUNT(*) FROM customers")
        active = db.count("SELECT COUNT(*) FROM customers WHERE status = 'active'")
        tiers = {r["tier"]: r["count"] for r in db.fetch_all(
            "SELECT tier, COUNT(*) as count FROM customers GROUP BY tier"
        )}
        return {
            "total": total, "active": active,
            "platinum": tiers.get("Platinum", 0), "gold": tiers.get("Gold", 0),
            "silver": tiers.get("Silver", 0), "standard": tiers.get("Standard", 0),
        }
