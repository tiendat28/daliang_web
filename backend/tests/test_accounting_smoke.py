"""Smoke & unit tests for accounting module."""
from datetime import date
import pytest
from pydantic import ValidationError

from app.modules.accounting.schemas import (
    InvoiceCreate,
    InvoiceItemCreate,
    VoucherCreate,
    BankAccountCreate,
    RemindDebtIn,
    AccountingDashboardOut,
)


def test_invoice_schema_validation():
    inv = InvoiceCreate(
        customer_name="Công ty Xi Mạ ABC",
        invoice_type="sales",
        subtotal=10000000,
        tax_rate=10,
        tax_amount=1000000,
        total_amount=11000000,
        items=[
            InvoiceItemCreate(
                product_name="Hóa chất tẩy gỉ",
                unit="Can",
                quantity=4,
                unit_price=2500000,
                amount=10000000,
            )
        ],
    )
    assert inv.customer_name == "Công ty Xi Mạ ABC"
    assert len(inv.items) == 1
    assert inv.items[0].quantity == 4

    # Empty customer_name should fail
    with pytest.raises(ValidationError):
        InvoiceCreate(customer_name="")


def test_voucher_schema_validation():
    voucher = VoucherCreate(
        voucher_type="receipt",
        category="sales_receipt",
        payment_method="bank",
        amount=50000000,
        partner_name="Công ty Mạ Kẽm Bình Dương",
        voucher_date=date.today(),
        description="Thu tiền hoá đơn bán hàng",
    )
    assert voucher.voucher_type == "receipt"
    assert voucher.amount == 50000000

    # Invalid voucher_type
    with pytest.raises(ValidationError):
        VoucherCreate(
            voucher_type="invalid_type",
            amount=1000,
            partner_name="Test",
        )

    # Negative amount
    with pytest.raises(ValidationError):
        VoucherCreate(
            voucher_type="receipt",
            amount=-100,
            partner_name="Test",
        )


def test_bank_account_and_remind_debt():
    acc = BankAccountCreate(
        account_type="bank",
        name="Vietcombank Tân Bình",
        account_number="0071000",
        current_balance=250000000,
    )
    assert acc.account_type == "bank"
    assert acc.current_balance == 250000000

    remind = RemindDebtIn(channel="email", note="Gửi đối chiếu nợ tháng 9")
    assert remind.channel == "email"

    with pytest.raises(ValidationError):
        RemindDebtIn(channel="carrier_pigeon")


def test_accounting_workflow_with_db(client):
    """CRUD workflow for accounting module."""
    # 1. Check dashboard
    res = client.get("/api/v1/accounting/dashboard")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["revenue_this_month"] > 0
    assert len(data["chart_6m"]) == 6

    # 2. Create an invoice
    inv_res = client.post("/api/v1/accounting/invoices", json={
        "customer_name": "Công ty Test ABC",
        "invoice_type": "sales",
        "subtotal": 10000000,
        "tax_rate": 10,
        "tax_amount": 1000000,
        "total_amount": 11000000,
        "items": [
            {
                "product_name": "Axit Sunfuric",
                "unit": "Can",
                "quantity": 5,
                "unit_price": 2000000,
                "amount": 10000000,
            }
        ]
    })
    assert inv_res.status_code == 200, inv_res.text
    inv_id = inv_res.json()["id"]

    # 3. Create a receipt voucher for this invoice
    v_res = client.post("/api/v1/accounting/vouchers", json={
        "voucher_type": "receipt",
        "category": "sales_receipt",
        "payment_method": "bank",
        "amount": 5000000,
        "partner_name": "Công ty Test ABC",
        "invoice_id": inv_id,
        "description": "Thu trước 5 triệu",
    })
    assert v_res.status_code == 200, v_res.text
    v_id = v_res.json()["id"]

    # 4. Check invoice payment_status is partial
    updated_inv = client.get(f"/api/v1/accounting/invoices/{inv_id}").json()
    assert updated_inv["payment_status"] == "partial"
    assert updated_inv["paid_amount"] == 5000000

    # 5. Remind debt
    remind_res = client.post(f"/api/v1/accounting/invoices/{inv_id}/remind-debt", json={"channel": "email"})
    assert remind_res.status_code == 200
    assert remind_res.json()["ok"] is True

    # Cleanup
    client.delete(f"/api/v1/accounting/vouchers/{v_id}")
    client.delete(f"/api/v1/accounting/invoices/{inv_id}")
