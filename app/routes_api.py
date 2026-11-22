import random
from flask import Blueprint, request, jsonify
from app.database import SessionLocal
from app.models import (
    User, Client, Supplier, Booking, Installment,
    TreasuryTransaction, OperatingExpense, AuditLog
)
from app.auth import verify_password, hash_password, get_permissions

api_bp = Blueprint("api", __name__, url_prefix="/api")

def get_db_session():
    return SessionLocal()

# ----------------------------------------------------
# 1. Authentication & Users
# ----------------------------------------------------
@api_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    db = get_db_session()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"success": False, "message": "اسم المستخدم أو كلمة المرور غير صحيحة"}), 401

        # Audit log
        log = AuditLog(
            user_name=user.full_name,
            action="تسجيل دخول",
            details=f"تم تسجيل الدخول بنجاح بصلاحية: {user.role_label}"
        )
        db.add(log)
        db.commit()

        user_dict = user.to_dict()
        user_dict["permissions"] = get_permissions(user.role)
        return jsonify({"success": True, "user": user_dict})
    finally:
        db.close()

@api_bp.route("/users", methods=["GET", "POST"])
def manage_users():
    db = get_db_session()
    try:
        if request.method == "GET":
            users = db.query(User).all()
            return jsonify([u.to_dict() for u in users])

        # POST: Create new user
        data = request.get_json() or {}
        username = data.get("username")
        full_name = data.get("full_name")
        password = data.get("password", "1234")
        role = data.get("role", "ticketing")
        email = data.get("email")

        if not username or not full_name:
            return jsonify({"success": False, "message": "الاسم واسم المستخدم مطلوبان"}), 400

        existing = db.query(User).filter(User.username == username).first()
        if existing:
            return jsonify({"success": False, "message": "اسم المستخدم مسجل مسبقاً"}), 400

        role_labels = {
            "admin": "مدير النظام (Super Admin)",
            "ticketing": "موظف حجز طيران",
            "umrah": "مسؤول برامج عمرة وحج",
            "accountant": "رئيس الحسابات والضرائب"
        }
        avatars = {"admin": "👑", "ticketing": "✈️", "umrah": "🕋", "accountant": "💼"}

        new_user = User(
            username=username,
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role=role,
            role_label=role_labels.get(role, "موظف"),
            avatar=avatars.get(role, "👤")
        )
        db.add(new_user)
        db.commit()
        return jsonify({"success": True, "user": new_user.to_dict()})
    finally:
        db.close()

# ----------------------------------------------------
# 2. KPI Stats
# ----------------------------------------------------
@api_bp.route("/stats", methods=["GET"])
def get_stats():
    db = get_db_session()
    try:
        bookings = db.query(Booking).all()
        clients = db.query(Client).all()

        total_sales_egp = sum(b.sell_price for b in bookings if b.currency == "ج.م")
        total_profit_egp = sum(b.profit for b in bookings if b.currency == "ج.م")
        total_debts_egp = sum(c.balance_due for c in clients)

        # Foreign currencies
        sar_balance = sum(b.sell_price for b in bookings if b.currency == "ريال") + 10300 # mock baseline
        usd_balance = sum(b.sell_price for b in bookings if b.currency == "دولار") + 3200

        return jsonify({
            "total_sales_egp": total_sales_egp,
            "total_profit_egp": total_profit_egp,
            "total_debts_egp": total_debts_egp,
            "sar_balance": sar_balance,
            "usd_balance": usd_balance,
            "bookings_count": len(bookings)
        })
    finally:
        db.close()

# ----------------------------------------------------
# 3. Bookings & ETA Invoices
# ----------------------------------------------------
@api_bp.route("/bookings", methods=["GET", "POST"])
def handle_bookings():
    db = get_db_session()
    try:
        if request.method == "GET":
            bookings = db.query(Booking).order_by(Booking.id.desc()).all()
            return jsonify([b.to_dict() for b in bookings])

        # POST: New Booking
        data = request.get_json() or {}
        client_name = data.get("client_name", "").strip()
        service_type = data.get("service_type", "").strip()
        sell_price = float(data.get("sell_price", 0))
        cost_price = float(data.get("cost_price", 0))
        currency = data.get("currency", "ج.م")
        pnr = data.get("file_pnr") or f"TRV-{random.randint(1000, 9999)}"
        created_by = data.get("created_by", "أحمد شريف")
        supplier_name = data.get("supplier_name", "مصر للطيران")

        profit = sell_price - cost_price

        # Service category auto-classification
        category = "flights"
        if "عمرة" in service_type or "حج" in service_type:
            category = "umrah"
        elif "فندق" in service_type:
            category = "hotels"
        elif "بكج" in service_type or "سياحة" in service_type:
            category = "packages"

        booking = Booking(
            file_pnr=pnr,
            client_name=client_name,
            service_type=service_type,
            service_category=category,
            supplier_name=supplier_name,
            sell_price=sell_price,
            cost_price=cost_price,
            currency=currency,
            profit=profit,
            payment_status="paid",
            paid_amount=sell_price,
            created_by=created_by
        )
        db.add(booking)

        # Audit log
        log = AuditLog(
            user_name=created_by,
            action="تسجيل حجز جديد",
            details=f"حجز {service_type} للعميل {client_name} بمبلغ {sell_price:,} {currency}"
        )
        db.add(log)

        db.commit()
        return jsonify({"success": True, "booking": booking.to_dict()})
    finally:
        db.close()

@api_bp.route("/bookings/<int:booking_id>/eta", methods=["POST"])
def issue_eta_invoice(booking_id):
    db = get_db_session()
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return jsonify({"success": False, "message": "الحجز غير موجود"}), 404

        uuid = f"ETA-{random.randint(1000, 9999)}"
        booking.eta_invoice_id = uuid
        booking.eta_status = "certified"

        log = AuditLog(
            user_name="رئيس الحسابات",
            action="اعتماد فاتورة ETA",
            details=f"تم اعتماد وتوليد الـ UUID ({uuid}) لملف الحجز {booking.file_pnr}"
        )
        db.add(log)
        db.commit()

        return jsonify({"success": True, "uuid": uuid, "booking": booking.to_dict()})
    finally:
        db.close()

# ----------------------------------------------------
# 4. Clients & Suppliers Accounts
# ----------------------------------------------------
@api_bp.route("/clients", methods=["GET"])
def get_clients():
    db = get_db_session()
    try:
        clients = db.query(Client).all()
        return jsonify([c.to_dict() for c in clients])
    finally:
        db.close()

@api_bp.route("/suppliers", methods=["GET"])
def get_suppliers():
    db = get_db_session()
    try:
        suppliers = db.query(Supplier).all()
        return jsonify([s.to_dict() for s in suppliers])
    finally:
        db.close()

@api_bp.route("/installments", methods=["GET"])
def get_installments():
    db = get_db_session()
    try:
        insts = db.query(Installment).all()
        return jsonify([i.to_dict() for i in insts])
    finally:
        db.close()

# ----------------------------------------------------
# 5. Treasury Vouchers (سندات القبض والصرف)
# ----------------------------------------------------
@api_bp.route("/transactions", methods=["GET", "POST"])
def handle_transactions():
    db = get_db_session()
    try:
        if request.method == "GET":
            txs = db.query(TreasuryTransaction).order_by(TreasuryTransaction.id.desc()).all()
            return jsonify([t.to_dict() for t in txs])

        data = request.get_json() or {}
        v_type = data.get("voucher_type", "receipt") # receipt (قبض) or payment (صرف)
        party = data.get("party_name", "").strip()
        amount = float(data.get("amount", 0))
        currency = data.get("currency", "ج.م")
        treasury = data.get("treasury_account", "خزينة الفرع كاش")
        desc = data.get("description", "")
        v_num = f"VCH-{random.randint(10000, 99999)}"

        tx = TreasuryTransaction(
            voucher_type=v_type,
            voucher_number=v_num,
            party_name=party,
            amount=amount,
            currency=currency,
            treasury_account=treasury,
            description=desc,
            created_by=data.get("created_by", "أحمد شريف")
        )
        db.add(tx)

        log = AuditLog(
            user_name=tx.created_by,
            action="إصدار سند مالي",
            details=f"سند {'قبض' if v_type == 'receipt' else 'صرف'} بمبلغ {amount:,} {currency} للطرف: {party}"
        )
        db.add(log)
        db.commit()

        return jsonify({"success": True, "transaction": tx.to_dict()})
    finally:
        db.close()

# ----------------------------------------------------
# 6. Expenses & Profit Reports
# ----------------------------------------------------
@api_bp.route("/expenses", methods=["GET", "POST"])
def handle_expenses():
    db = get_db_session()
    try:
        if request.method == "GET":
            expenses = db.query(OperatingExpense).all()
            return jsonify([e.to_dict() for e in expenses])

        data = request.get_json() or {}
        exp = OperatingExpense(
            title=data.get("title", ""),
            category=data.get("category", "utilities"),
            amount=float(data.get("amount", 0)),
            currency=data.get("currency", "ج.م"),
            notes=data.get("notes", "")
        )
        db.add(exp)
        db.commit()
        return jsonify({"success": True, "expense": exp.to_dict()})
    finally:
        db.close()

@api_bp.route("/reports/profit-summary", methods=["GET"])
def get_profit_summary():
    db = get_db_session()
    try:
        bookings = db.query(Booking).all()
        expenses = db.query(OperatingExpense).all()

        flights_profit = sum(b.profit for b in bookings if b.service_category == "flights" and b.currency == "ج.م")
        umrah_profit = sum(b.profit for b in bookings if b.service_category == "umrah")
        hotels_profit = sum(b.profit for b in bookings if b.service_category in ["hotels", "packages"] and b.currency == "ج.م")

        gross_profit = flights_profit + hotels_profit
        total_expenses = sum(e.amount for e in expenses if e.currency == "ج.م")
        net_profit = gross_profit - total_expenses

        return jsonify({
            "flights_profit": flights_profit,
            "umrah_profit": umrah_profit,
            "hotels_profit": hotels_profit,
            "gross_profit_egp": gross_profit,
            "total_expenses_egp": total_expenses,
            "net_profit_egp": net_profit
        })
    finally:
        db.close()

# ----------------------------------------------------
# 7. Audit Logs
# ----------------------------------------------------
@api_bp.route("/audit-logs", methods=["GET"])
def get_audit_logs():
    db = get_db_session()
    try:
        logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(20).all()
        return jsonify([l.to_dict() for l in logs])
    finally:
        db.close()
