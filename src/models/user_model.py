"""User model — CRUD operations for the users table."""

from werkzeug.security import check_password_hash, generate_password_hash

from database.db_manager import get_db


class UserModel:
    """Handles all database operations for users."""

    @staticmethod
    def create(
        email: str,
        password: str,
        full_name: str,
        role: str = "customer",
        security_question: str = None,
        security_answer: str = None,
    ) -> int:
        """Create a new user and return the user ID."""
        db = get_db()
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        answer_hash = (
            generate_password_hash(
                security_answer.lower().strip(), method="pbkdf2:sha256"
            )
            if security_answer
            else None
        )

        return db.insert(
            """INSERT INTO users (email, password_hash, full_name, role,
                                  security_question, security_answer_hash)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                email.lower().strip(),
                password_hash,
                full_name.strip(),
                role,
                security_question,
                answer_hash,
            ),
        )

    @staticmethod
    def find_by_email(email: str) -> dict | None:
        """Find a user by email address."""
        db = get_db()
        return db.fetch_one(
            "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
        )

    @staticmethod
    def find_by_id(user_id: int) -> dict | None:
        """Find a user by ID."""
        db = get_db()
        return db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))

    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        """Verify a password against stored hash."""
        return check_password_hash(stored_hash, password)

    @staticmethod
    def verify_security_answer(stored_hash: str, answer: str) -> bool:
        """Verify security answer against stored hash."""
        return check_password_hash(stored_hash, answer.lower().strip())

    @staticmethod
    def update_password(user_id: int, new_password: str):
        """Update a user's password."""
        db = get_db()
        new_hash = generate_password_hash(new_password, method="pbkdf2:sha256")
        db.execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_hash, user_id),
        )

    @staticmethod
    def get_all(role: str = None) -> list[dict]:
        """Get all users, optionally filtered by role."""
        db = get_db()
        if role:
            return db.fetch_all(
                "SELECT id, email, full_name, role, created_at FROM users WHERE role = ? ORDER BY created_at DESC",
                (role,),
            )
        return db.fetch_all(
            "SELECT id, email, full_name, role, created_at FROM users ORDER BY created_at DESC"
        )
