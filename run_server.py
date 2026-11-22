import os
from flask import Flask, send_from_directory, jsonify
from app.database import init_db
from app.seed import seed_database
from app.routes_api import api_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "al-haramain-travel-erp-secret-key-2026")

# Enable CORS for all API endpoints
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

# Register API Blueprint
app.register_blueprint(api_bp)

# Root Web Route -> index.html
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

# Health check
@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "Al-Haramain Travel ERP", "version": "2.4.0"})

def main():
    # Initialize DB & Seed if empty
    init_db()
    seed_database()

    port = int(os.getenv("PORT", 5000))
    print("=" * 65)
    print(" [AL-HARAMAIN TRAVEL ERP] - Enterprise System v2.4")
    print(" Al-Haramain Travel & Tourism | Powered by Sanad Digital")
    print("=" * 65)
    print(f" -> Dashboard URL: http://localhost:{port}")
    print(f" -> Local IP URL:  http://127.0.0.1:{port}")
    print("=" * 65)
    print(" Server is running. Press CTRL+C to stop.\n")

    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
