"""Web server — headless Flask entry point for Docker."""
import os
from app import create_app
from seed_data import seed_database

app = create_app(os.environ.get("FLASK_CONFIG", "development"))
seed_database()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
