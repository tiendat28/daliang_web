"""Du lieu ke toan: hoa don ban/mua, phieu thu/chi, so quy, ngan hang."""
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base

SCHEMA = "accounting"


class _InSchema:
    __table_args__ = {"schema": SCHEMA}


class BankAccount(_InSchema, Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True)
    account_type = Column(String(20), nullable=False, default="bank")  # cash / bank
    name = Column(String(100), nullable=False)
    account_number = Column(String(50))
    bank_name = Column(String(100))
    current_balance = Column(Numeric(15, 2), nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Invoice(_InSchema, Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    invoice_code = Column(String(30), unique=True, nullable=False)  # HD-000421
    invoice_type = Column(String(20), nullable=False, default="sales")  # sales / purchase
    customer_id = Column(Integer, ForeignKey("common.customers.id", ondelete="SET NULL"))
    customer_name = Column(String(200), nullable=False)
    supplier_name = Column(String(200))
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date)
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=10)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    paid_amount = Column(Numeric(15, 2), nullable=False, default=0)
    payment_status = Column(String(30), nullable=False, default="pending")  # pending / partial / paid
    einvoice_status = Column(String(30), nullable=False, default="issued")  # draft / pending_signature / issued / cancelled
    einvoice_number = Column(String(50))
    note = Column(Text)
    created_by = Column(Integer, ForeignKey("auth.users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(_InSchema, Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("accounting.invoices.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("common.company_products.id", ondelete="SET NULL"))
    product_code = Column(String(50))
    product_name = Column(String(200), nullable=False)
    unit = Column(String(30), nullable=False, default="Kg")
    quantity = Column(Numeric(12, 3), nullable=False, default=1)
    unit_price = Column(Numeric(15, 2), nullable=False, default=0)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=10)
    amount = Column(Numeric(15, 2), nullable=False, default=0)

    invoice = relationship("Invoice", back_populates="items")


class Voucher(_InSchema, Base):
    __tablename__ = "vouchers"

    id = Column(Integer, primary_key=True)
    voucher_code = Column(String(30), unique=True, nullable=False)  # PT-2026-001 / PC-2026-001
    voucher_type = Column(String(10), nullable=False)  # receipt / payment
    category = Column(String(50), nullable=False, default="sales_receipt")
    payment_method = Column(String(20), nullable=False, default="bank")  # cash / bank
    bank_account = Column(String(50))
    amount = Column(Numeric(15, 2), nullable=False, default=0)
    partner_name = Column(String(200), nullable=False)
    customer_id = Column(Integer, ForeignKey("common.customers.id", ondelete="SET NULL"))
    invoice_id = Column(Integer, ForeignKey("accounting.invoices.id", ondelete="SET NULL"))
    voucher_date = Column(Date, nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("auth.users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
