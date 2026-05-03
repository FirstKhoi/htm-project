"""App factory — Flask application setup, blueprints, CSRF, and template helpers."""
import hmac
import os
import secrets
import socket
import sys
import threading

src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from flask import Flask, abort, request, session
from config import config_map
from database.db_manager import init_app as init_db


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def create_app(config_name: str = "default") -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_map.get(config_name, config_map["default"]))
    init_db(app.config["DATABASE_PATH"])

    csrf_key = "_csrf_token"

    def get_csrf_token() -> str:
        token = session.get(csrf_key)
        if not token:
            token = secrets.token_urlsafe(32)
            session[csrf_key] = token
        return token

    @app.before_request
    def validate_csrf():
        """Block POST requests with missing/invalid CSRF token."""
        if request.method != "POST":
            return
        s_token = session.get(csrf_key, "")
        f_token = request.form.get("csrf_token", "")
        if not s_token or not f_token:
            abort(403, description="Missing CSRF token.")
        if not hmac.compare_digest(str(s_token), str(f_token)):
            abort(403, description="Invalid CSRF token.")

    @app.errorhandler(403)
    def forbidden(_error):
        return "Forbidden (403): Missing or invalid CSRF token.", 403

    # Register blueprints
    from controllers.auth_controller import auth_bp
    from controllers.booking_controller import bookings_bp
    from controllers.customer_controller import customers_bp
    from controllers.dashboard_controller import dashboard_bp
    from controllers.report_controller import reports_bp
    from controllers.room_controller import rooms_bp

    for bp in [auth_bp, dashboard_bp, rooms_bp, customers_bp, bookings_bp, reports_bp]:
        app.register_blueprint(bp)

    # Template globals
    @app.context_processor
    def inject_globals():
        return {
            "current_user": {
                "name": session.get("user_name", ""),
                "email": session.get("user_email", ""),
                "role": session.get("role", ""),
                "logged_in": "user_id" in session,
            },
            "current_endpoint": request.endpoint or "",
            "csrf_token": get_csrf_token,
        }

    # Jinja2 filters
    @app.template_filter("currency")
    def currency_filter(value):
        try:
            return f"${float(value):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    @app.template_filter("number")
    def number_filter(value):
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return "0"

    return app


def start_flask(app: Flask, port: int):
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    import webview

    app = create_app("development")

    from seed_data import seed_database
    seed_database()

    port = find_free_port()
    url = f"http://127.0.0.1:{port}/auth/login"

    print("\n🏨 Hotel Management System — Group 03")
    print("=" * 46)
    print(f"  Desktop App starting on port {port}...")
    print("  Admin:   admin@group03hotel.com / admin123")
    print("  Staff:   staff@group03hotel.com / staff123")
    print("=" * 46)

    flask_thread = threading.Thread(target=start_flask, args=(app, port), daemon=True)
    flask_thread.start()

    window = webview.create_window(
        title="Group03 Hotel Management System",
        url=url, width=1400, height=900,
        min_size=(1024, 700), resizable=True, text_select=True,
    )
    webview.start(debug=False)
    print("\n👋 Application closed. Goodbye!")
