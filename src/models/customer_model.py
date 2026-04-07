"""Customer model — CRUD operations for the customers table."""

from database.db_manager import get_db


class CustomerModel:
    """Handles all database operations for customers."""

    @staticmethod
    def create(
        full_name: str,
        email: str,
        phone: str = None,
        id_card: str = None,
        nationality: str = "Vietnam",
        user_id: int = None,
    ) -> int:
        """Create a new customer and return their ID."""
        db = get_db()
        return db.insert(
            """INSERT INTO customers (user_id, full_name, email, phone,
                                      id_card, nationality)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                full_name.strip(),
                email.lower().strip(),
                phone,
                id_card,
                nationality,
            ),
        )

    @staticmethod
    def find_by_id(customer_id: int) -> dict | None:
        """Find a customer by ID."""
        db = get_db()
        return db.fetch_one("SELECT * FROM customers WHERE id = ?", (customer_id,))

    @staticmethod
    def find_by_email(email: str) -> dict | None:
        """Find a customer by email."""
        db = get_db()
        return db.fetch_one(
            "SELECT * FROM customers WHERE email = ?", (email.lower().strip(),)
        )

    @staticmethod
    def find_by_user_id(user_id: int) -> dict | None:
        """Find customer linked to a user account."""
        db = get_db()
        return db.fetch_one("SELECT * FROM customers WHERE user_id = ?", (user_id,))

    @staticmethod
    def get_paginated(
        page: int = 1, per_page: int = 10, search: str = None
    ) -> tuple[list[dict], int]:
        """Get paginated list of customers. Returns (rows, total_count)."""
        db = get_db()
        offset = (page - 1) * per_page

        if search:
            search_pattern = f"%{search}%"
            count_query = """SELECT COUNT(*) FROM customers
                            WHERE full_name LIKE ? OR email LIKE ? OR phone LIKE ?"""
            total = db.count(
                count_query, (search_pattern, search_pattern, search_pattern)
            )

            data_query = """SELECT * FROM customers
                           WHERE full_name LIKE ? OR email LIKE ? OR phone LIKE ?
                           ORDER BY created_at DESC LIMIT ? OFFSET ?"""
            rows = db.fetch_all(
                data_query,
                (search_pattern, search_pattern, search_pattern, per_page, offset),
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
        """Get all customers."""
        db = get_db()
        return db.fetch_all("SELECT * FROM customers ORDER BY created_at DESC")

    @staticmethod
    def update(customer_id: int, **kwargs) -> None:
        """Update customer fields."""
        db = get_db()
        allowed_fields = {
            "full_name",
            "email",
            "phone",
            "id_card",
            "nationality",
            "tier",
            "status",
            "total_spent",
            "total_bookings",
        }
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return

        updates["updated_at"] = "CURRENT_TIMESTAMP"
        set_parts = []
        values = []
        for k, v in updates.items():
            if v == "CURRENT_TIMESTAMP":
                set_parts.append(f"{k} = CURRENT_TIMESTAMP")
            else:
                set_parts.append(f"{k} = ?")
                values.append(v)

        values.append(customer_id)
        db.execute(
            f"UPDATE customers SET {', '.join(set_parts)} WHERE id = ?", tuple(values)
        )

    @staticmethod
    def delete(customer_id: int) -> bool:
        """Delete a customer. Returns False if they have active bookings."""
        db = get_db()
        active_count = db.count(
            """SELECT COUNT(*) FROM bookings
               WHERE customer_id = ?
                 AND status NOT IN ('cancelled', 'checked_out')""",
            (customer_id,),
        )
        if active_count > 0:
            return False

        db.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        return True

    @staticmethod
    def calculate_tier(total_spent: float, total_bookings: int) -> str:
        """Auto-calculate customer tier based on spending and bookings."""
        if total_spent >= 50000 and total_bookings >= 20:
            return "Platinum"
        elif total_spent >= 20000 and total_bookings >= 10:
            return "Gold"
        elif total_spent >= 5000 and total_bookings >= 3:
            return "Silver"
        return "Standard"

    @staticmethod
    def update_after_checkout(customer_id: int, amount: float) -> None:
        """Update customer stats after a booking checkout."""
        db = get_db()
        customer = CustomerModel.find_by_id(customer_id)
        if not customer:
            return

        new_spent = customer["total_spent"] + amount
        new_bookings = customer["total_bookings"] + 1
        new_tier = CustomerModel.calculate_tier(new_spent, new_bookings)

        CustomerModel.update(
            customer_id,
            total_spent=new_spent,
            total_bookings=new_bookings,
            tier=new_tier,
        )

    @staticmethod
    def get_stats() -> dict:
        """Get aggregate customer statistics."""
        db = get_db()
        total = db.count("SELECT COUNT(*) FROM customers")
        active = db.count("SELECT COUNT(*) FROM customers WHERE status = 'active'")
        tier_counts = db.fetch_all(
            "SELECT tier, COUNT(*) as count FROM customers GROUP BY tier"
        )
        tiers = {row["tier"]: row["count"] for row in tier_counts}

        return {
            "total": total,
            "active": active,
            "platinum": tiers.get("Platinum", 0),
            "gold": tiers.get("Gold", 0),
            "silver": tiers.get("Silver", 0),
            "standard": tiers.get("Standard", 0),
        }
