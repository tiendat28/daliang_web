"""Pydantic schemas cho module ke toan."""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.schemas import ORM_CONFIG


class InvoiceItemBase(BaseModel):
    product_id: Optional[int] = None
    product_code: Optional[str] = None
    product_name: str = Field(min_length=1, max_length=200)
    unit: str = Field(default="Kg", max_length=30)
    quantity: float = Field(gt=0, default=1)
    unit_price: float = Field(ge=0, default=0)
    tax_rate: float = Field(default=10)
    amount: float = Field(ge=0, default=0)


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemOut(InvoiceItemBase):
    id: int
    invoice_id: int
    model_config = ORM_CONFIG


class InvoiceBase(BaseModel):
    invoice_code: Optional[str] = None
    invoice_type: str = Field(default="sales", pattern="^(sales|purchase)$")
    customer_id: Optional[int] = None
    customer_name: str = Field(min_length=1, max_length=200)
    supplier_name: Optional[str] = None
    invoice_date: date = Field(default_factory=date.today)
    due_date: Optional[date] = None
    subtotal: float = Field(ge=0, default=0)
    tax_rate: float = Field(default=10)
    tax_amount: float = Field(ge=0, default=0)
    total_amount: float = Field(ge=0, default=0)
    paid_amount: float = Field(ge=0, default=0)
    payment_status: str = Field(default="pending", pattern="^(pending|partial|paid)$")
    einvoice_status: str = Field(default="issued", pattern="^(draft|pending_signature|issued|cancelled)$")
    einvoice_number: Optional[str] = None
    note: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate] = []


class InvoiceUpdate(BaseModel):
    customer_name: Optional[str] = None
    supplier_name: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    subtotal: Optional[float] = None
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    paid_amount: Optional[float] = None
    payment_status: Optional[str] = None
    einvoice_status: Optional[str] = None
    note: Optional[str] = None


class InvoiceOut(InvoiceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemOut] = []
    model_config = ORM_CONFIG


class VoucherBase(BaseModel):
    voucher_code: Optional[str] = None
    voucher_type: str = Field(pattern="^(receipt|payment)$")
    category: str = Field(default="sales_receipt")
    payment_method: str = Field(default="bank", pattern="^(cash|bank)$")
    bank_account: Optional[str] = None
    amount: float = Field(gt=0)
    partner_name: str = Field(min_length=1, max_length=200)
    customer_id: Optional[int] = None
    invoice_id: Optional[int] = None
    voucher_date: date = Field(default_factory=date.today)
    description: Optional[str] = None


class VoucherCreate(VoucherBase):
    pass


class VoucherOut(VoucherBase):
    id: int
    created_at: datetime
    model_config = ORM_CONFIG


class BankAccountBase(BaseModel):
    account_type: str = Field(default="bank", pattern="^(cash|bank)$")
    name: str = Field(min_length=1, max_length=100)
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    current_balance: float = Field(default=0)
    is_active: bool = True


class BankAccountCreate(BankAccountBase):
    pass


class BankAccountOut(BankAccountBase):
    id: int
    model_config = ORM_CONFIG


class RemindDebtIn(BaseModel):
    channel: str = Field(default="email", pattern="^(email|sms|zalo|manual)$")
    note: Optional[str] = None


class MonthChartPoint(BaseModel):
    month: str
    revenue: float
    expense: float


class OverdueDebtOut(BaseModel):
    id: Optional[int] = None
    customer_name: str
    invoice_code: str
    days_overdue: int
    amount: float


class AccountingDashboardOut(BaseModel):
    revenue_this_month: float
    revenue_month_label: str
    revenue_growth_pct: float
    total_receivables: float
    receivables_count: int
    total_payables: float
    payables_suppliers_count: int
    total_funds: float
    funds_note: str
    chart_6m: List[MonthChartPoint]
    overdue_debts: List[OverdueDebtOut]
    recent_invoices: List[InvoiceOut]
