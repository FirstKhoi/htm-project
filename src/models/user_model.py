"""User model — authentication and user CRUD."""
from werkzeug.security import check_password_hash, generate_password_hash
from database.db_manager import get_db


class UserModel:

    @staticmethod
    def create(email: str, password: str, full_name: str, role: str = "customer",
               security_question: str = None, security_answer: str = None) -> int:
        """Create user, return ID."""
        db = get_db()
        pw_hash = generate_password_hash(password, method="pbkdf2:sha256")
        ans_hash = (
            generate_password_hash(security_answer.lower().strip(), method="pbkdf2:sha256")
            if security_answer else None
        )
        return db.insert(
            """INSERT INTO users (email, password_hash, full_name, role,
                                  security_question, security_answer_hash)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (email.lower().strip(), pw_hash, full_name.strip(),
             role, security_question, ans_hash),
        )

    @staticmethod
    def find_by_email(email: str) -> dict | None:
        return get_db().fetch_one("SELECT * FROM users WHERE email = ?",
                                  (email.lower().strip(),))

    @staticmethod
    def find_by_id(user_id: int) -> dict | None:
        return get_db().fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))

    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        return check_password_hash(stored_hash, password)

    @staticmethod
    def verify_security_answer(stored_hash: str, answer: str) -> bool:
        return check_password_hash(stored_hash, answer.lower().strip())

    @staticmethod
    def update_password(user_id: int, new_password: str):
        new_hash = generate_password_hash(new_password, method="pbkdf2:sha256")
        get_db().execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_hash, user_id),
        )

    @staticmethod
    def get_all(role: str = None) -> list[dict]:
        db = get_db()
        if role:
            return db.fetch_all(
                "SELECT id, email, full_name, role, created_at FROM users WHERE role = ? ORDER BY created_at DESC",
                (role,),
            )
        return db.fetch_all(
            "SELECT id, email, full_name, role, created_at FROM users ORDER BY created_at DESC"
        )
