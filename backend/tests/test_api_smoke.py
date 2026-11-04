"""Goi thu moi API cua cac module tren DB test.

Khong kiem nghiep vu chi tiet - chi bat loi kieu "route tro sai duong dan",
"SQL viet tay quen ten schema", "import trong ham tro file cu": nhung loi chi no
khi co nguoi bam dung nut do.
"""
import pytest

LIST_ENDPOINTS = [
    "/api/v1/common/customers",
    "/api/v1/common/products",
    "/api/v1/common/company-profile",
    "/api/v1/common/documents",
    "/api/v1/lab/chemicals",
    "/api/v1/lab/indicators",
    "/api/v1/lab/equipment",
    "/api/v1/lab/formulations",
    "/api/v1/lab/samples",
    "/api/v1/lab/analysis-reports",
    "/api/v1/lab/work-logs",
    "/api/v1/lab/test-processes",
    "/api/v1/lab/test-processes/operation-suggestions",
    "/api/v1/lab/process-templates",
    "/api/v1/website/public/site",
    "/api/v1/website/contact-leads",
    "/api/v1/hr/dashboard",
    "/api/v1/hr/departments",
    "/api/v1/hr/employees",
    "/api/v1/hr/attendance",
    "/api/v1/hr/leave-requests",
    "/api/v1/hr/contracts",
    "/api/v1/hr/certificates",
    "/api/v1/accounting/dashboard",
    "/api/v1/accounting/invoices",
    "/api/v1/accounting/vouchers",
    "/api/v1/accounting/bank-accounts",
    "/api/v1/health",
]


@pytest.mark.parametrize("path", LIST_ENDPOINTS)
def test_moi_danh_sach_tra_200(client, path):
    response = client.get(path)
    assert response.status_code == 200, response.text


def test_khach_hang_va_don_pha_che(client):
    customer = client.post("/api/v1/common/customers", json={
        "name": "KH kiem tra", "fields": [{"field_name": "Ma kem", "product_codes": ["NCZ-48A"]}],
    })
    assert customer.status_code == 200, customer.text
    chemical = client.post("/api/v1/lab/chemicals", json={
        "code": "TEST-HC", "name": "Hoa chat kiem tra", "box_count": 2, "volume_per_box": 500, "unit": "ml",
    })
    assert chemical.status_code == 200, chemical.text

    order = client.post("/api/v1/lab/formulations", json={
        "lab_chemical_id": chemical.json()["id"], "customer_id": customer.json()["id"],
        "used_amount": 100, "unit": "ml",
    })
    assert order.status_code == 200, order.text
    remaining = [c for c in client.get("/api/v1/lab/chemicals").json() if c["code"] == "TEST-HC"][0]
    assert remaining["remaining_volume"] is not None   # don pha che tru vao phan "Le"

    assert client.delete(f"/api/v1/lab/formulations/{order.json()['id']}").status_code == 200
    assert client.delete(f"/api/v1/lab/chemicals/{chemical.json()['id']}").status_code == 200
    assert client.delete(f"/api/v1/common/customers/{customer.json()['id']}").status_code == 200


def test_tai_lieu_noi_bo_va_file_cong_khai(client):
    upload = client.post(
        "/api/v1/common/documents",
        data={"category": "coa", "name": "COA TEST-1", "uploaded_by": "kiem tra"},
        files={"file": ("coa.txt", b"noi dung", "text/plain")},
    )
    assert upload.status_code == 200, upload.text
    doc_id = upload.json()["id"]
    assert client.get(f"/api/v1/common/documents/{doc_id}/file").content == b"noi dung"
    # COA la tai lieu noi bo: website khong duoc mo
    assert client.get(f"/api/v1/website/public/files/{doc_id}").status_code == 404
    assert client.delete(f"/api/v1/common/documents/{doc_id}").status_code == 200


def test_form_lien_he_website(client):
    lead = client.post("/api/v1/website/public/contact-leads", json={"name": "Khach", "phone": "0900", "lang": "en"})
    assert lead.status_code == 201, lead.text
    assert client.get("/api/v1/website/public/lookup/KHONG-CO-MA").json() is None
