from datetime import datetime, timedelta
from app.database import SessionLocal, init_db
from app.models import (
    User, Client, Supplier, Booking, Installment,
    TreasuryTransaction, OperatingExpense, AuditLog
)
from app.auth import hash_password

def seed_database():
    """Seed initial realistic data for travel agency ERP."""
    init_db()
    db = SessionLocal()

    try:
        # Check if users already seeded
        if db.query(User).first():
            print("Database already contains records. Skipping seed.")
            return

        print("Seeding initial ERP data...")

        # 1. Staff Users
        users = [
            User(
                username="admin",
                full_name="أحمد شريف",
                email="a.sherif@sanadtravel.com",
                password_hash=hash_password("1234"),
                role="admin",
                role_label="مدير النظام (Super Admin)",
                avatar="👑"
            ),
            User(
                username="reham",
                full_name="ريهام إبراهيم",
                email="reham@sanadtravel.com",
                password_hash=hash_password("1234"),
                role="ticketing",
                role_label="موظف حجز طيران",
                avatar="✈️"
            ),
            User(
                username="elgohary",
                full_name="محمود الجوهري",
                email="elgohary@sanadtravel.com",
                password_hash=hash_password("1234"),
                role="umrah",
                role_label="مسؤول برامج عمرة وحج",
                avatar="🕋"
            ),
            User(
                username="tareq",
                full_name="أ. طارق ممدوح",
                email="tareq@sanadtravel.com",
                password_hash=hash_password("1234"),
                role="accountant",
                role_label="رئيس الحسابات والضرائب",
                avatar="💼"
            )
        ]
        db.add_all(users)

        # 2. Clients
        clients = [
            Client(
                name="شركة النور للتجارة والتوريدات",
                phone="01012345678",
                company="مجموعة النور",
                total_sales=18500.0,
                total_paid=18500.0,
                balance_due=0.0
            ),
            Client(
                name="مجموعة الأهرام تورز",
                phone="01187654321",
                company="الأهرام جروب",
                total_sales=50000.0,
                total_paid=35000.0,
                balance_due=15000.0
            ),
            Client(
                name="الحاج عبد الله السعيد",
                phone="01244556677",
                company="فردي - برنامج عمرة",
                total_sales=28000.0,
                total_paid=20000.0,
                balance_due=8000.0
            ),
            Client(
                name="شركة الفارس للاستيراد",
                phone="01599887766",
                company="الفارس التجارية",
                total_sales=42000.0,
                total_paid=33800.0,
                balance_due=8200.0
            ),
            Client(
                name="د. سارة المنشاوي",
                phone="01099881122",
                company="فردي - سياحة داخلية",
                total_sales=24000.0,
                total_paid=24000.0,
                balance_due=0.0
            )
        ]
        db.add_all(clients)

        # 3. Suppliers & Airlines
        suppliers = [
            Supplier(
                name="مصر للطيران (EgyptAir GDS)",
                supplier_type="airline",
                phone="0226966777",
                currency="ج.م",
                total_transactions=142000.0,
                balance_due=18500.0
            ),
            Supplier(
                name="شركة دار الإيمان للفنادق (مكة المكرمة)",
                supplier_type="hotel",
                phone="+966125432100",
                currency="ريال",
                total_transactions=38000.0,
                balance_due=4500.0
            ),
            Supplier(
                name="شركة ترافيل وان للسياحة (دبي)",
                supplier_type="visa",
                phone="+97142345678",
                currency="دولار",
                total_transactions=6800.0,
                balance_due=950.0
            ),
            Supplier(
                name="مجموعة فنادق ومنتجعات ريكسوس",
                supplier_type="hotel",
                phone="0693666666",
                currency="ج.م",
                total_transactions=65000.0,
                balance_due=7200.0
            )
        ]
        db.add_all(suppliers)

        # 4. Bookings
        bookings = [
            Booking(
                file_pnr="MS-9014",
                client_name="شركة النور للتجارة والتوريدات",
                client_id=1,
                service_type="تذكرة طيران (القاهرة - دبي ذهاب وعودة)",
                service_category="flights",
                supplier_name="مصر للطيران (EgyptAir GDS)",
                sell_price=18500.0,
                cost_price=16000.0,
                currency="ج.م",
                profit=2500.0,
                payment_status="paid",
                paid_amount=18500.0,
                remaining_amount=0.0,
                eta_invoice_id="#8812",
                eta_status="certified",
                created_by="ريهام إبراهيم"
            ),
            Booking(
                file_pnr="UMR-2026",
                client_name="الحاج عبد الله السعيد",
                client_id=3,
                service_type="برنامج عمرة VIP - 14 يوم (المولد النبوي)",
                service_category="umrah",
                supplier_name="شركة دار الإيمان للفنادق (مكة المكرمة)",
                sell_price=4200.0,
                cost_price=3550.0,
                currency="ريال",
                profit=650.0,
                payment_status="partial",
                paid_amount=3000.0,
                remaining_amount=1200.0,
                eta_invoice_id="#9842",
                eta_status="certified",
                created_by="محمود الجوهري"
            ),
            Booking(
                file_pnr="HTL-4421",
                client_name="د. سارة المنشاوي",
                client_id=5,
                service_type="حجز فندق ريكسوس شرم الشيخ (4 ليالي All-Inclusive)",
                service_category="hotels",
                supplier_name="مجموعة فنادق ومنتجعات ريكسوس",
                sell_price=24000.0,
                cost_price=20800.0,
                currency="ج.م",
                profit=3200.0,
                payment_status="paid",
                paid_amount=24000.0,
                remaining_amount=0.0,
                eta_invoice_id="#7723",
                eta_status="certified",
                created_by="أحمد شريف"
            ),
            Booking(
                file_pnr="DXB-5510",
                client_name="شركة الفارس للاستيراد",
                client_id=4,
                service_type="بكج سياحة دبي (تأشيرة سريعة + فندق 4 نجوم + انتقالات)",
                service_category="packages",
                supplier_name="شركة ترافيل وان للسياحة (دبي)",
                sell_price=35000.0,
                cost_price=30000.0,
                currency="ج.م",
                profit=5000.0,
                payment_status="partial",
                paid_amount=26800.0,
                remaining_amount=8200.0,
                eta_invoice_id=None,
                eta_status="unsubmitted",
                created_by="ريهام إبراهيم"
            )
        ]
        db.add_all(bookings)

        # 5. Installments
        installments = [
            Installment(
                client_id=2,
                client_name="مجموعة الأهرام تورز",
                booking_id=1,
                amount=15000.0,
                currency="ج.م",
                due_date="2026-11-25",
                status="pending"
            ),
            Installment(
                client_id=3,
                client_name="الحاج عبد الله السعيد",
                booking_id=2,
                amount=8000.0,
                currency="ج.م",
                due_date="2026-12-01",
                status="pending"
            ),
            Installment(
                client_id=4,
                client_name="شركة الفارس للاستيراد",
                booking_id=4,
                amount=8200.0,
                currency="ج.م",
                due_date="2026-12-10",
                status="pending"
            )
        ]
        db.add_all(installments)

        # 6. Operating Expenses
        expenses = [
            OperatingExpense(
                title="إيجار المقر والفرع الرئيسي",
                category="rent",
                amount=8000.0,
                currency="ج.م",
                notes="سداد إيجار شهر نوفمبر 2026"
            ),
            OperatingExpense(
                title="حملات إعلانات فيسبوك ورسائل الواتساب للعمرة",
                category="marketing",
                amount=4500.0,
                currency="ج.م",
                notes="حملة عمرة المولد النبوي"
            ),
            OperatingExpense(
                title="فواتير اتصالات وإنترنت ومطبوعات",
                category="utilities",
                amount=5700.0,
                currency="ج.م",
                notes="فواتير فودافون وإنترنت وي WE"
            )
        ]
        db.add_all(expenses)

        # 7. Audit Log entries
        logs = [
            AuditLog(
                user_name="ريهام إبراهيم",
                action="تسجيل حجز طيران",
                details="تم تسجيل تذكرة القاهرة - دبي ملف PNR: MS-9014 بمبلغ 18,500 ج.م"
            ),
            AuditLog(
                user_name="أ. طارق ممدوح",
                action="إصدار فاتورة ETA",
                details="تم اعتماد الفاتورة الإلكترونية برقم #8812 والربط بمصلحة الضرائب"
            ),
            AuditLog(
                user_name="محمود الجوهري",
                action="تحصيل دفعة مقدمة",
                details="استلام دفعة مقدمة 3,000 ريال لحساب برنامج عمرة الحاج عبد الله السعيد"
            )
        ]
        db.add_all(logs)

        db.commit()
        print("✓ All initial seed data inserted successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
