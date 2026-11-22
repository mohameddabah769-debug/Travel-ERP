import os
from flask import Flask, send_from_directory, jsonify
from app.database import init_db
from app.seed import seed_database
from app.routes_api import api_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "sanad-travel-erp-secret-key-2026")

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

# Proposal Web Route -> proposal.html
@app.route("/proposal")
@app.route("/proposal.html")
def proposal():
    return send_from_directory(BASE_DIR, "proposal.html")

# Health check
@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "Sanad Travel ERP", "version": "1.2.0"})

def main():
    print("=" * 65)
    print(" 🕋  شركة الحرمين للسياحة والسفر - نظام الإدارة والحسابات")
    print("     Al-Haramain Travel ERP | Powered by Sanad Digital")
    print("=" * 65)
    
    # Initialize DB & Seed if empty
    init_db()
    seed_database()

    port = int(os.getenv("PORT", 5000))
    print(f"\n🚀 السيستم يعمل الآن بنجاح على الرابط التالي:")
    print(f"👉 http://localhost:{port}")
    print(f"👉 http://127.0.0.1:{port}")
    print(f"\n📄 العرض الفني والمالي (Proposal):")
    print(f"👉 http://localhost:{port}/proposal.html")
    print("\nاضغط Ctrl+C لإيقاف السيرفر في أي وقت.\n" + "=" * 65)

    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
