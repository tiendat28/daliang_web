"""Khoi tao du lieu mau cho module ke toan khop voi ban thiet ke."""
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.modules.accounting import models


def seed_accounting_data(db: Session) -> None:
    # 1. Tai khoan ngan hang & quy tien mat (tong ton quy: 254 tr)
    accounts = [
        {"account_type": "cash", "name": "Quỹ tiền mặt công ty", "account_number": "TM-01", "bank_name": "Tiền mặt tại két", "current_balance": Decimal("74000000")},
        {"account_type": "bank", "name": "Vietcombank - CN Tân Bình", "account_number": "0071001234567", "bank_name": "Vietcombank", "current_balance": Decimal("180000000")},
    ]
    for acc in accounts:
        existing = db.query(models.BankAccount).filter_by(name=acc["name"]).first()
        if not existing:
            db.add(models.BankAccount(**acc))
    db.commit()

    # 2. Cac hoa don ban (khop danh sach gan day & cong no qua han)
    invoices = [
        {
            "invoice_code": "HĐ-000421",
            "invoice_type": "sales",
            "customer_name": "Xi mạ Tân Phú",
            "invoice_date": date(2026, 9, 23),
            "due_date": date(2026, 10, 23),
            "subtotal": Decimal("44181818"),
            "tax_rate": Decimal("10"),
            "tax_amount": Decimal("4418182"),
            "total_amount": Decimal("48600000"),
            "paid_amount": Decimal("0"),
            "payment_status": "pending",
            "einvoice_status": "issued",
            "einvoice_number": "1/001-C26TDL-000421",
            "items": [
                {"product_name": "Hóa chất mạ kẽm kiềm NCZ-48A", "unit": "Can", "quantity": 10, "unit_price": Decimal("2500000"), "amount": Decimal("25000000")},
                {"product_name": "Chất định hình bề mặt", "unit": "Kg", "quantity": 100, "unit_price": Decimal("191818"), "amount": Decimal("19181818")},
            ],
        },
        {
            "invoice_code": "HĐ-000420",
            "invoice_type": "sales",
            "customer_name": "Công ty Mạ Kẽm Bình Dương",
            "invoice_date": date(2026, 9, 22),
            "due_date": date(2026, 10, 22),
            "subtotal": Decimal("114545455"),
            "tax_rate": Decimal("10"),
            "tax_amount": Decimal("11454545"),
            "total_amount": Decimal("126000000"),
            "paid_amount": Decimal("126000000"),
            "payment_status": "paid",
            "einvoice_status": "issued",
            "einvoice_number": "1/001-C26TDL-000420",
            "items": [
                {"product_name": "Phụ gia thụ động Cr3+ xanh trắng", "unit": "Phuy", "quantity": 4, "unit_price": Decimal("28636364"), "amount": Decimal("114545455")},
            ],
        },
        {
            "invoice_code": "HĐ-000419",
            "invoice_type": "sales",
            "customer_name": "Cơ khí Minh Tâm",
            "invoice_date": date(2026, 9, 22),
            "due_date": date(2026, 10, 22),
            "subtotal": Decimal("20318182"),
            "tax_rate": Decimal("10"),
            "tax_amount": Decimal("2031818"),
            "total_amount": Decimal("22350000"),
            "paid_amount": Decimal("10000000"),
            "payment_status": "partial",
            "einvoice_status": "issued",
            "einvoice_number": "1/001-C26TDL-000419",
            "items": [
                {"product_name": "Chất tẩy dầu siêu âm", "unit": "Can", "quantity": 15, "unit_price": Decimal("1354545"), "amount": Decimal("20318182")},
            ],
        },
        {
            "invoice_code": "HĐ-000418",
            "invoice_type": "sales",
            "customer_name": "Phụ tùng Hưng Thịnh",
            "invoice_date": date(2026, 9, 21),
            "due_date": date(2026, 10, 21),
            "subtotal": Decimal("58909091"),
            "tax_rate": Decimal("10"),
            "tax_amount": Decimal("5890909"),
            "total_amount": Decimal("64800000"),
            "paid_amount": Decimal("0"),
            "payment_status": "pending",
            "einvoice_status": "pending_signature",
            "einvoice_number": None,
            "items": [
                {"product_name": "Muối Kẽm Clorua tinh khiết", "unit": "Bao", "quantity": 40, "unit_price": Decimal("1472727"), "amount": Decimal("58909091")},
            ],
        },
        {
            "invoice_code": "HĐ-000417",
            "invoice_type": "sales",
            "customer_name": "Kim khí Đông Á",
            "invoice_date": date(2026, 9, 20),
            "due_date": date(2026, 10, 20),
            "subtotal": Decimal("14000000"),
            "tax_rate": Decimal("10"),
            "tax_amount": Decimal("1400000"),
            "total_amount": Decimal("15400000"),
            "paid_amount": Decimal("15400000"),
            "payment_status": "paid",
            "einvoice_status": "issued",
            "einvoice_number": "1/001-C26TDL-000417",
            "items": [
                {"product_name": "Axit Sunfuric H2SO4 98%", "unit": "Can", "quantity": 20, "unit_price": Decimal("700000"), "amount": Decimal("14000000")},
            ],
        },
        # 3 hoa don qua han
        {
            "invoice_code": "HĐ-000377",
            "invoice_type": "sales",
            "customer_name": "Công ty Mạ Kẽm Bình Dương",
            "invoice_date": date(2026, 8, 1),
            "due_date": date(2026, 8, 17),  # qua 42 ngay so voi 28/09
            "subtotal": Decimal("169454545"),
            "tax_rate": Decimal("10"),
            "tax_amount": Decimal("16945455"),
            "total_amount": Decimal("186400000"),
            "paid_amount": Decimal("0"),
            "payment_status": "pending",
            "einvoice_status": "issued",
            "einvoice_number": "1/001-C26TDL-000377",
            "items": [
                {"product_name": "Lô phụ gia xi mạ Niken bóng", "unit": "Bộ", "quantity": 2, "unit_price": Decimal("84727273"), "amount": Decimal("169454545")},
            ],
        },
        {
            "invoice_code": "HĐ-000391",
            "invoice_type": "sales",
            "customer_name": "Xi mạ Tân Phú",
            "invoice_date": date(2026, 8, 22),
            "due_date": date(2026, 9, 10),  # qua 18 ngay so voi 28/09
            "subtotal": Decimal("67500000"),
            "tax_rate": Decimal("10"),
            "tax_amount": Decimal("6750000"),
            "total_amount": Decimal("74250000"),
            "paid_amount": Decimal("0"),
            "payment_status": "pending",
            "einvoice_status": "issued",
            "einvoice_number": "1/001-C26TDL-000391",
            "items": [
                {"product_name": "Hóa chất thụ động 7 màu", "unit": "Phuy", "quantity": 3, "unit_price": Decimal("22500000"), "amount": Decimal("67500000")},
            ],
        },
        {
            "invoice_code": "HĐ-000402",
            "invoice_type": "sales",
            "customer_name": "Cơ khí Minh Tâm",
            "invoice_date": date(2026, 9, 5),
            "due_date": date(2026, 9, 21),  # qua 7 ngay so voi 28/09
            "subtotal": Decimal("35363636"),
            "tax_rate": Decimal("10"),
            "tax_amount": Decimal("3536364"),
            "total_amount": Decimal("38900000"),
            "paid_amount": Decimal("0"),
            "payment_status": "pending",
            "einvoice_status": "issued",
            "einvoice_number": "1/001-C26TDL-000402",
            "items": [
                {"product_name": "Chất bảo vệ chống rỉ bề mặt", "unit": "Can", "quantity": 25, "unit_price": Decimal("1414545"), "amount": Decimal("35363636")},
            ],
        },
    ]

    for inv_data in invoices:
        items = inv_data.pop("items", [])
        existing = db.query(models.Invoice).filter_by(invoice_code=inv_data["invoice_code"]).first()
        if not existing:
            inv = models.Invoice(**inv_data)
            db.add(inv)
            db.flush()
            for it in items:
                db.add(models.InvoiceItem(invoice_id=inv.id, **it))
    db.commit()

    # 3. Phieu thu mau
    vouchers = [
        {
            "voucher_code": "PT-2026-0001",
            "voucher_type": "receipt",
            "category": "sales_receipt",
            "payment_method": "bank",
            "bank_account": "Vietcombank - CN Tân Bình",
            "amount": Decimal("126000000"),
            "partner_name": "Công ty Mạ Kẽm Bình Dương",
            "voucher_date": date(2026, 9, 22),
            "description": "Thanh toán hoá đơn HĐ-000420",
        },
        {
            "voucher_code": "PT-2026-0002",
            "voucher_type": "receipt",
            "category": "sales_receipt",
            "payment_method": "bank",
            "bank_account": "Vietcombank - CN Tân Bình",
            "amount": Decimal("15400000"),
            "partner_name": "Kim khí Đông Á",
            "voucher_date": date(2026, 9, 20),
            "description": "Thanh toán hoá đơn HĐ-000417",
        },
        {
            "voucher_code": "PC-2026-0001",
            "voucher_type": "payment",
            "category": "supplier_payment",
            "payment_method": "bank",
            "bank_account": "Vietcombank - CN Tân Bình",
            "amount": Decimal("85000000"),
            "partner_name": "Công ty TNHH Hóa Chất Đức Giang",
            "voucher_date": date(2026, 9, 21),
            "description": "Thanh toán tiền nhập xút vảy NaOH",
        },
    ]
    for v in vouchers:
        existing = db.query(models.Voucher).filter_by(voucher_code=v["voucher_code"]).first()
        if not existing:
            db.add(models.Voucher(**v))
    db.commit()
