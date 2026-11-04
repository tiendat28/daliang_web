"""Dang nhap, 2FA, phien, quyen, mat khau, quan ly tai khoan."""
import pyotp
import pytest

from app.core.config import settings

PASSWORD = "matkhau-dung-123"
LOGIN = "/api/v1/auth/login"


def login(client, identifier, password=PASSWORD, remember=False):
    return client.post(LOGIN, json={"identifier": identifier, "password": password, "remember": remember})


# ---------- Dang nhap / khoa tam ----------

def test_chua_dang_nhap_bi_401_con_website_thi_mo(anon_client):
    assert anon_client.get("/api/v1/common/customers").status_code == 401
    assert anon_client.get("/api/v1/lab/chemicals").status_code == 401
    assert anon_client.get("/api/v1/website/public/site").status_code == 200


def test_sai_mat_khau_cung_thong_bao_voi_sai_email(anon_client, make_user):
    make_user("a@test.local", PASSWORD, [])
    wrong_password = login(anon_client, "a@test.local", "sai-roi-123")
    no_user = login(anon_client, "khongco@test.local", "sai-roi-123")
    assert wrong_password.status_code == no_user.status_code == 401
    assert wrong_password.json() == no_user.json()


def test_sai_5_lan_thi_khoa_tam(anon_client, make_user):
    make_user("b@test.local", PASSWORD, [])
    for _ in range(settings.login_max_attempts):
        assert login(anon_client, "b@test.local", "sai-roi-123").status_code == 401
    # Da khoa: dung mat khau cung khong vao duoc
    locked = login(anon_client, "b@test.local")
    assert locked.status_code == 423 and "khoá" in locked.json()["detail"]


def test_email_khong_phan_biet_hoa_thuong(anon_client, make_user):
    make_user("c@test.local", PASSWORD, [])
    assert login(anon_client, "  C@Test.Local ").json()["step"] == "done"


def test_dang_nhap_bang_ma_nhan_vien(anon_client, make_user):
    make_user("nv@test.local", PASSWORD, [], employee_code="DL0123")
    result = login(anon_client, "dl0123").json()
    assert result["step"] == "done" and result["user"]["employee_code"] == "DL0123"


def test_ghi_nho_thiet_bi_thi_cookie_song_30_ngay(anon_client, make_user):
    make_user("nho@test.local", PASSWORD, [])
    remembered = login(anon_client, "nho@test.local", remember=True)
    refresh_cookie = next(h for h in remembered.headers.get_list("set-cookie") if h.startswith("dl_refresh="))
    assert f"Max-Age={30 * 86400}" in refresh_cookie
    anon_client.post("/api/v1/auth/logout")
    session = login(anon_client, "nho@test.local")
    refresh_cookie = next(h for h in session.headers.get_list("set-cookie") if h.startswith("dl_refresh="))
    assert "Max-Age" not in refresh_cookie   # cookie phien: mat khi tat trinh duyet


# ---------- Quyen ----------

def test_quyen_xem_khong_cho_them(anon_client, make_user):
    make_user("xem@test.local", PASSWORD, ["common.customers.view"])
    login(anon_client, "xem@test.local")
    assert anon_client.get("/api/v1/common/customers").status_code == 200
    denied = anon_client.post("/api/v1/common/customers", json={"name": "X"})
    assert denied.status_code == 403 and "common.customers.create" in denied.json()["detail"]
    assert anon_client.get("/api/v1/lab/chemicals").status_code == 403


def test_cho_them_nhung_khong_cho_xoa(anon_client, make_user):
    make_user("them@test.local", PASSWORD, ["common.customers.view", "common.customers.create"])
    login(anon_client, "them@test.local")
    created = anon_client.post("/api/v1/common/customers", json={"name": "KH thêm được"})
    assert created.status_code == 200
    denied = anon_client.delete(f"/api/v1/common/customers/{created.json()['id']}")
    assert denied.status_code == 403 and "common.customers.delete" in denied.json()["detail"]


def test_post_xem_truoc_chi_can_quyen_xem(anon_client, make_user):
    make_user("xemlt@test.local", PASSWORD, ["lab.test_processes.view"])
    login(anon_client, "xemlt@test.local")
    preview = anon_client.post("/api/v1/lab/test-processes/letterhead-preview", json={})
    assert preview.status_code == 200


def test_me_tra_ve_quyen(client):
    me = client.get("/api/v1/auth/me").json()
    assert me["email"] == "admin@test.local" and "*" in me["permissions"]


# ---------- 2FA ----------

def _setup_and_enable(client):
    setup = client.post("/api/v1/auth/2fa/setup")
    assert setup.status_code == 200 and setup.json()["qr"].startswith("data:image/svg+xml")
    secret = setup.json()["secret"]
    enabled = client.post("/api/v1/auth/2fa/enable", json={"code": pyotp.TOTP(secret).now()})
    assert enabled.status_code == 200, enabled.text
    return secret, enabled.json()


def test_vai_tro_bat_buoc_2fa_phai_cai_moi_vao_duoc(anon_client, make_user, monkeypatch):
    monkeypatch.setattr(settings, "two_factor_enabled", True)
    make_user("ketoan@test.local", PASSWORD, ["common.customers.view"], require_2fa=True)
    assert login(anon_client, "ketoan@test.local").json()["step"] == "setup_2fa"
    # Chua cai xong thi chua goi duoc API
    assert anon_client.get("/api/v1/common/customers").status_code == 401

    _, result = _setup_and_enable(anon_client)
    assert len(result["backup_codes"]) == 10 and result["user"]["totp_enabled"]
    assert anon_client.get("/api/v1/common/customers").status_code == 200


def test_dang_nhap_co_2fa_va_ma_du_phong_chi_dung_mot_lan(anon_client, make_user, monkeypatch):
    monkeypatch.setattr(settings, "two_factor_enabled", True)
    make_user("d@test.local", PASSWORD, [], require_2fa=True)
    login(anon_client, "d@test.local")
    secret, result = _setup_and_enable(anon_client)
    backup = result["backup_codes"][0]
    anon_client.post("/api/v1/auth/logout")

    assert login(anon_client, "d@test.local").json()["step"] == "verify_2fa"
    assert anon_client.post("/api/v1/auth/2fa/verify", json={"code": "000000"}).status_code == 401
    ok = anon_client.post("/api/v1/auth/2fa/verify", json={"code": pyotp.TOTP(secret).now()})
    assert ok.status_code == 200 and ok.json()["step"] == "done"

    anon_client.post("/api/v1/auth/logout")
    login(anon_client, "d@test.local")
    assert anon_client.post("/api/v1/auth/2fa/verify", json={"code": backup.lower()}).status_code == 200
    anon_client.post("/api/v1/auth/logout")
    login(anon_client, "d@test.local")
    assert anon_client.post("/api/v1/auth/2fa/verify", json={"code": backup}).status_code == 401


# ---------- Phien ----------

def test_refresh_xoay_vong_va_phat_hien_dung_lai(anon_client, make_user):
    make_user("e@test.local", PASSWORD, ["common.customers.view"])
    login(anon_client, "e@test.local")
    old_refresh = anon_client.cookies.get("dl_refresh")
    assert anon_client.post("/api/v1/auth/refresh").status_code == 200
    assert anon_client.cookies.get("dl_refresh") != old_refresh

    # Ai do dung lai refresh token cu -> moi phien cua user bi thu hoi
    anon_client.cookies.set("dl_refresh", old_refresh, path="/api/v1/auth")
    assert anon_client.post("/api/v1/auth/refresh").status_code == 401


def test_dang_xuat_thi_het_refresh(client):
    assert client.post("/api/v1/auth/logout").status_code == 200
    assert client.post("/api/v1/auth/refresh").status_code == 401


# ---------- Mat khau ----------

def test_quen_mat_khau_gui_link_dat_lai_mot_lan(anon_client, make_user, monkeypatch):
    sent = []
    monkeypatch.setattr("app.modules.auth.service.send_email", lambda to, subject, html, text: sent.append(text))
    make_user("f@test.local", PASSWORD, [])

    assert anon_client.post("/api/v1/auth/forgot-password", json={"email": "khongco@test.local"}).status_code == 200
    assert anon_client.post("/api/v1/auth/forgot-password", json={"email": "f@test.local"}).status_code == 200
    assert len(sent) == 1
    token = sent[0].split("token=")[1].strip()

    weak = anon_client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": "123"})
    assert weak.status_code == 400
    ok = anon_client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": "matkhau-moi-456"})
    assert ok.status_code == 200
    again = anon_client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": "matkhau-khac-789"})
    assert again.status_code == 400
    assert login(anon_client, "f@test.local", "matkhau-moi-456").json()["step"] == "done"


def test_doi_mat_khau_dang_xuat_phien_khac(anon_client, make_user):
    make_user("g@test.local", PASSWORD, ["common.customers.view"])
    login(anon_client, "g@test.local")
    other_access = anon_client.cookies.get("dl_access")
    changed = anon_client.post("/api/v1/auth/change-password",
                               json={"current_password": PASSWORD, "new_password": "matkhau-moi-456"})
    assert changed.status_code == 200
    assert anon_client.get("/api/v1/common/customers").status_code == 200   # phien nay duoc cap lai
    anon_client.cookies.set("dl_access", other_access, path="/api")          # phien cu
    assert anon_client.get("/api/v1/common/customers").status_code == 401


# ---------- Quan ly tai khoan ----------

def test_admin_tao_tai_khoan_mat_khau_tam_bat_doi(client, anon_client):
    roles = client.get("/api/v1/system/roles").json()
    lab = next(r for r in roles if r["code"] == "lab")
    created = client.post("/api/v1/system/users",
                          json={"email": "moi@test.local", "full_name": "NV mới", "role_ids": [lab["id"]]})
    assert created.status_code == 201
    temporary = created.json()["temporary_password"]

    client.post("/api/v1/auth/logout")
    assert login(client, "moi@test.local", temporary).json()["user"]["must_change_password"]
    blocked = client.get("/api/v1/lab/chemicals")
    assert blocked.status_code == 403 and "đổi mật khẩu" in blocked.json()["detail"]
    client.post("/api/v1/auth/change-password", json={"current_password": temporary, "new_password": "matkhau-rieng-789"})
    assert client.get("/api/v1/lab/chemicals").status_code == 200


def test_khong_the_khoa_admin_cuoi_cung(client):
    me = client.get("/api/v1/auth/me").json()
    user = next(u for u in client.get("/api/v1/system/users").json() if u["id"] == me["id"])
    response = client.put(f"/api/v1/system/users/{user['id']}",
                          json={"full_name": user["full_name"], "role_ids": user["role_ids"], "is_active": False})
    assert response.status_code == 400


def test_nhat_ky_ghi_thao_tac_va_dang_nhap(client):
    created = client.post("/api/v1/common/customers", json={"name": "KH nhật ký"}).json()
    logs = client.get("/api/v1/system/audit-logs").json()["items"]
    summaries = [item["summary"] for item in logs]
    assert f"Thêm khách hàng" in summaries or any(s and s.startswith("Thêm khách hàng") for s in summaries)
    assert "Đăng nhập" in summaries
    client.put(f"/api/v1/common/customers/{created['id']}", json={"name": "KH đổi tên", "fields": []})
    latest = client.get("/api/v1/system/audit-logs").json()["items"][0]
    assert latest["summary"] == f"Sửa khách hàng #{created['id']}" and latest["user_name"] == "Người test"


def test_xoa_mem_giai_phong_email_va_khong_dang_nhap_duoc(client, anon_client):
    created = client.post("/api/v1/system/users", json={
        "email": "xoa@test.local", "employee_code": "dl9", "department": "lab", "full_name": "Sẽ xoá",
    }).json()
    user_id, temporary = created["user"]["id"], created["temporary_password"]
    assert created["user"]["employee_code"] == "DL9"
    assert client.delete(f"/api/v1/system/users/{user_id}").status_code == 200
    assert all(u["id"] != user_id for u in client.get("/api/v1/system/users").json())
    logs = client.get("/api/v1/system/audit-logs").json()["items"]
    assert logs[0]["summary"] == "Xoá tài khoản Sẽ xoá" and logs[0]["action"] == "user.delete"
    # Email va ma NV dung lai duoc
    again = client.post("/api/v1/system/users", json={"email": "xoa@test.local", "employee_code": "DL9",
                                                       "full_name": "Người mới"})
    assert again.status_code == 201
    client.post("/api/v1/auth/logout")
    assert login(client, "xoa@test.local", temporary).status_code == 401


def test_khoa_mo_tai_khoan_va_so_lieu(client):
    created = client.post("/api/v1/system/users", json={"email": "khoa@test.local", "full_name": "Bị khoá"}).json()
    user_id = created["user"]["id"]
    locked = client.patch(f"/api/v1/system/users/{user_id}/active", json={"is_active": False})
    assert locked.status_code == 200 and not locked.json()["is_active"]
    summary = client.get("/api/v1/system/users/summary").json()
    assert summary["active_users"] == 1 and summary["roles"] >= 1
    assert client.get("/api/v1/system/departments").json()[0] == {"code": "lab", "name": "Kỹ thuật"}
