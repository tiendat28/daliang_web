import type { Session } from "next-auth";

export function isAdmin(session: Session | null): boolean {
  return session?.user?.roleName === "Admin";
}

export function isDepartmentHead(session: Session | null): boolean {
  return session?.user?.roleName === "Trưởng phòng";
}

/**
 * Reads `roles.permissions` (seeded per role, e.g. `{"documents.approve": true}`)
 * off the session — set in `auth.ts`'s `authorize()`/jwt/session callbacks from
 * the `Role` the signed-in `AdminUser` belongs to. `"*"` is a wildcard granting
 * every permission (used for Admin).
 */
export function hasPermission(session: Session | null, key: string): boolean {
  const permissions = session?.user?.permissions;
  if (!permissions) return false;
  return permissions["*"] === true || permissions[key] === true;
}

/** Admin/Trưởng phòng can see and manage the employee roster; Nhân viên can only see their own profile. */
export function canManageEmployees(session: Session | null): boolean {
  return hasPermission(session, "employees.view") || hasPermission(session, "employees.edit");
}

/** Returns the departmentId a "Trưởng phòng" is scoped to, or null when unrestricted (Admin). */
export function employeeScopeDepartmentId(session: Session | null): number | null {
  if (isAdmin(session)) return null;
  return session?.user?.departmentId ?? null;
}

/** Requires the "documents.approve" permission, and — for non-admins — ownership of the document's department. */
export function canApproveDocumentsForDepartment(session: Session | null, departmentId: number): boolean {
  if (!hasPermission(session, "documents.approve")) return false;
  return isAdmin(session) || session?.user?.departmentId === departmentId;
}

/** Admin manages invoices/payments; Trưởng phòng can view only; Nhân viên has no access. */
export function canViewInvoices(session: Session | null): boolean {
  return hasPermission(session, "invoices.view") || hasPermission(session, "invoices.manage");
}

export function canManageInvoices(session: Session | null): boolean {
  return hasPermission(session, "invoices.manage");
}
