"""Nhat ky thao tac: ghi su kien dang nhap (goi tay) va moi request ghi (middleware)."""
from fastapi import Request
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import API_PREFIX
from app.core.database import SessionLocal
from app.modules.system import models

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Ten de doc cua tung nhom API (<module>/<nhom>) - dung de dung cau tom tat nhat ky
RESOURCE_LABELS = {
    "common/customers": "khách hàng", "common/products": "sản phẩm", "common/documents": "tài liệu",
    "common/company-profile": "thông tin công ty",
    "lab/chemicals": "hoá chất PTN", "lab/indicators": "chất chỉ thị", "lab/equipment": "thiết bị",
    "lab/formulations": "đơn hàng HCTN", "lab/samples": "phiếu lấy mẫu", "lab/analysis-reports": "báo cáo phân tích",
    "lab/work-logs": "nhật ký công tác", "lab/test-processes": "lưu trình", "lab/process-templates": "quy trình chuẩn",
    "website/contact-leads": "đơn khách gửi",
    "system/users": "tài khoản", "system/roles": "vai trò",
    "hr/employees": "hồ sơ nhân viên", "hr/departments": "phòng ban", "hr/attendance": "chấm công",
    "hr/leave-requests": "đơn nghỉ phép", "hr/contracts": "hợp đồng", "hr/certificates": "chứng chỉ",
    "accounting/invoices": "hoá đơn", "accounting/vouchers": "chứng từ thu chi",
    "accounting/bank-accounts": "tài khoản ngân hàng",
    "warehouse/stock": "tồn kho theo lô", "warehouse/receipts": "phiếu nhập kho",
    "warehouse/dispatches": "phiếu xuất kho", "warehouse/locations": "vị trí kho",
    "warehouse/audits": "phiếu kiểm kê",
    "dispatch/trips": "chuyến giao hàng", "dispatch/vehicles": "xe giao hàng",
    "dispatch/drivers": "tài xế",
}
METHOD_VERBS = {"POST": "Thêm", "PUT": "Sửa", "PATCH": "Sửa", "DELETE": "Xoá"}
# Duoi duong dan dac biet -> dong tu rieng
SUFFIX_VERBS = {
    "open-box": "Mở hộp mới", "duplicate": "Nhân bản", "save-as-template": "Lưu thành quy trình chuẩn từ",
    "status": "Đổi trạng thái", "logo": "Đổi logo", "website": "Sửa phần website của",
    "decision": "Duyệt đơn nghỉ phép", "remind-debt": "Nhắc nợ",
    "pick": "Soạn hàng phiếu xuất", "load": "Bàn giao xe phiếu xuất",
    "assign": "Phân công tài xế",
    "preview-sheet": None, "letterhead-preview": None,   # chi la xem truoc - khong ghi nhat ky
}


def describe_request(method: str, path: str) -> str | None:
    """"PUT /api/v1/lab/formulations/5" -> "Sửa đơn hàng HCTN #5". None = khong can ghi."""
    parts = path[len(API_PREFIX):].strip("/").split("/")
    if len(parts) < 2:
        return None
    label = RESOURCE_LABELS.get(f"{parts[0]}/{parts[1]}", parts[1])
    record_id = next((p for p in parts[2:] if p.isdigit()), None)
    last = parts[-1]
    if last in SUFFIX_VERBS:
        verb = SUFFIX_VERBS[last]
        if verb is None:
            return None
    else:
        verb = METHOD_VERBS.get(method, method)
    return f"{verb} {label}" + (f" #{record_id}" if record_id else "")
# Da ghi bang su kien rieng (login.success, 2fa.enable...) hoac la khach vang lai tren website
SKIP_PREFIXES = (f"{API_PREFIX}/auth/", f"{API_PREFIX}/website/public/")


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    return (forwarded.split(",")[0].strip() or (request.client.host if request.client else ""))[:64]


def _module_of(path: str) -> str | None:
    rest = path[len(API_PREFIX):].strip("/").split("/")
    return rest[0] if rest and rest[0] else None


def mark_request(request: Request, summary: str, action: str | None = None) -> None:
    """Route tu dat cau nhat ky cho request dang chay (vd "Khoá tài khoản Nguyễn Văn An"),
    thay cho cau middleware tu dung tu duong dan. action: loai rieng (vd "user.lock")."""
    request.state.audit_summary = summary
    if action:
        request.state.audit_action = action


def record_event(db, action: str, request: Request | None = None, *, user=None, email: str | None = None,
                 status: int | None = None, detail: dict | None = None, summary: str | None = None) -> None:
    """Ghi mot dong nhat ky trong session dang mo (khong commit)."""
    db.add(models.AuditLog(
        user_id=user.id if user else None,
        user_email=(user.email if user else email),
        action=action,
        module=_module_of(request.url.path) if request else None,
        path=request.url.path[:255] if request else None,
        status=status,
        ip=client_ip(request) if request else None,
        summary=summary,
        detail=detail,
    ))


# Test thay bang session cua DB test (tests/conftest.py) de khong ghi vao DB that
audit_session_factory = SessionLocal


def _write_request_log(user_id, user_email, action, path, status, ip, summary) -> None:
    with audit_session_factory() as db:
        db.add(models.AuditLog(
            user_id=user_id, user_email=user_email, action=action,
            module=_module_of(path), path=path[:255], status=status, ip=ip, summary=summary,
        ))
        db.commit()


class AuditMiddleware(BaseHTTPMiddleware):
    """Moi request ghi (them/sua/xoa) da dang nhap -> mot dong nhat ky. Khong luu body."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        audit_user = getattr(request.state, "audit_user", None)   # (id, email) - auth.deps gan vao
        if (request.method in WRITE_METHODS and audit_user is not None and path.startswith(API_PREFIX)
                and not path.startswith(SKIP_PREFIXES) and response.status_code < 500):
            summary = getattr(request.state, "audit_summary", None) or describe_request(request.method, path)
            if summary:
                action = getattr(request.state, "audit_action", None) or request.method
                await run_in_threadpool(
                    _write_request_log, *audit_user, action, path,
                    response.status_code, client_ip(request), summary[:255],
                )
        return response
