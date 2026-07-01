"""
DP-700 Exam Prep — Flask Server Launcher
Runs Flask in a background thread alongside Streamlit.
"""

import threading
import time
import requests
from backend.app import create_app

FLASK_PORT = 5050
FLASK_URL = f"http://127.0.0.1:{FLASK_PORT}"

_server_started = False
_server_lock = threading.Lock()


def start_flask_server():
    """Start the Flask server in a background daemon thread."""
    global _server_started

    with _server_lock:
        if _server_started:
            return

        # Check if server is already running
        try:
            resp = requests.get(f"{FLASK_URL}/api/health", timeout=2)
            if resp.status_code == 200:
                _server_started = True
                return
        except Exception:
            pass

        app = create_app()

        def run():
            app.run(host="127.0.0.1", port=FLASK_PORT, debug=False, use_reloader=False)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

        # Wait for server to be ready
        for _ in range(30):
            try:
                resp = requests.get(f"{FLASK_URL}/api/health", timeout=1)
                if resp.status_code == 200:
                    _server_started = True
                    print(f"[Flask] Server started on {FLASK_URL}")
                    return
            except Exception:
                time.sleep(0.5)

        print("[Flask] Warning: Server may not have started properly")
        _server_started = True  # Proceed anyway


def get_api_url():
    """Get the Flask API base URL."""
    return FLASK_URL
