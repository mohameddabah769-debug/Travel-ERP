from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, Numeric
)
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="ticketing") # admin, ticketing, umrah, accountant
    role_label = Column(String(100), default="موظف حجز طيران")
    is_active = Column(Boolean, default=True)
    avatar = Column(String(10), default="👤")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "role_label": self.role_label,
            "is_active": self.is_active,
            "avatar": self.avatar,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    company = Column(String(120), nullable=True)
    total_sales = Column(Float, default=0.0)
    total_paid = Column(Float, default=0.0)
    balance_due = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="client")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "company": self.company,
            "total_sales": self.total_sales,
            "total_paid": self.total_paid,
            "balance_due": self.balance_due,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, index=True)
    supplier_type = Column(String(50), default="airline") # airline, hotel, umrah_agent, visa, transport
    phone = Column(String(50), nullable=True)
    currency = Column(String(10), default="ج.م") # ج.م, ريال, دولار
    total_transactions = Column(Float, default=0.0)
    balance_due = Column(Float, default=0.0) # مستحقات المورد علينا
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "supplier_type": self.supplier_type,
            "phone": self.phone,
            "currency": self.currency,
            "total_transactions": self.total_transactions,
            "balance_due": self.balance_due,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    file_pnr = Column(String(50), index=True, nullable=False) # e.g. MS-9014, UMR-2026
    client_name = Column(String(120), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    service_type = Column(String(200), nullable=False)
    service_category = Column(String(50), default="flights") # flights, umrah, hotels, packages
    supplier_name = Column(String(120), nullable=True)
    sell_price = Column(Float, nullable=False, default=0.0)
    cost_price = Column(Float, nullable=False, default=0.0)
    currency = Column(String(10), default="ج.م")
    profit = Column(Float, nullable=False, default=0.0)
    payment_status = Column(String(30), default="paid") # paid, partial, unpaid
    paid_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, default=0.0)
    eta_invoice_id = Column(String(100), nullable=True)
    eta_status = Column(String(30), default="unsubmitted") # unsubmitted, certified, pending
    created_by = Column(String(100), default="admin")
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="bookings")

    def to_dict(self):
        return {
            "id": self.id,
            "file_pnr": self.file_pnr,
            "client_name": self.client_name,
            "client_id": self.client_id,
            "service_type": self.service_type,
            "service_category": self.service_category,
            "supplier_name": self.supplier_name,
            "sell_price": self.sell_price,
            "cost_price": self.cost_price,
            "currency": self.currency,
            "profit": self.profit,
            "payment_status": self.payment_status,
            "paid_amount": self.paid_amount,
            "remaining_amount": self.remaining_amount,
            "eta_invoice_id": self.eta_invoice_id,
            "eta_status": self.eta_status,
            "created_by": self.created_by,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None
        }

class Installment(Base):
    __tablename__ = "installments"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    client_name = Column(String(120), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="ج.م")
    due_date = Column(String(50), nullable=False)
    status = Column(String(30), default="pending") # pending, paid, overdue
    paid_date = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "client_name": self.client_name,
            "booking_id": self.booking_id,
            "amount": self.amount,
            "currency": self.currency,
            "due_date": self.due_date,
            "status": self.status,
            "paid_date": self.paid_date.isoformat() if self.paid_date else None
        }

class TreasuryTransaction(Base):
    __tablename__ = "treasury_transactions"

    id = Column(Integer, primary_key=True, index=True)
    voucher_type = Column(String(20), nullable=False) # receipt (قبض), payment (صرف)
    voucher_number = Column(String(50), unique=True, nullable=False)
    party_name = Column(String(120), nullable=False) # client or supplier name
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="ج.م")
    treasury_account = Column(String(100), default="الخزينة الرئيسية كاش") # خزينة كاش, بنك أهلي, بنك مصر
    description = Column(String(255), nullable=True)
    created_by = Column(String(100), default="admin")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "voucher_type": self.voucher_type,
            "voucher_number": self.voucher_number,
            "party_name": self.party_name,
            "amount": self.amount,
            "currency": self.currency,
            "treasury_account": self.treasury_account,
            "description": self.description,
            "created_by": self.created_by,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None
        }

class OperatingExpense(Base):
    __tablename__ = "operating_expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    category = Column(String(50), default="utilities") # rent, marketing, salaries, utilities, misc
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="ج.م")
    expense_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "amount": self.amount,
            "currency": self.currency,
            "expense_date": self.expense_date.strftime("%Y-%m-%d") if self.expense_date else None,
            "notes": self.notes
        }

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "action": self.action,
            "details": self.details,
            "timestamp": self.timestamp.strftime("%I:%M %p - %Y-%m-%d") if self.timestamp else None
        }
