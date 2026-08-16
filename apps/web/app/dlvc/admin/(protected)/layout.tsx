import { prisma } from "@daliang/db";
import { auth } from "@/auth";
import { SidebarProvider } from "@/components/dlvc/admin/SidebarContext";
import Sidebar from "@/components/dlvc/admin/Sidebar";
import Topbar from "@/components/dlvc/admin/Topbar";

async function getNavCounts() {
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 1);

  const [employees, documents, invoices] = await Promise.all([
    prisma.employee.count({ where: { status: "active" } }),
    prisma.adminDocument.count({ where: { status: "pending" } }),
    prisma.invoice.count({ where: { issueDate: { gte: monthStart, lt: monthEnd } } }),
  ]);

  return { employees, documents, invoices };
}

export default async function AdminProtectedLayout({ children }: { children: React.ReactNode }) {
  const [session, counts] = await Promise.all([auth(), getNavCounts()]);

  const userName = session?.user?.name ?? session?.user?.employeeCode ?? "Người dùng";
  const userRole = session?.user?.roleName ?? "Nhân viên";

  return (
    <SidebarProvider>
      <div className="flex min-h-screen bg-dlvc-bg">
        <Sidebar counts={counts} userName={userName} userRole={userRole} />
        <div className="flex min-w-0 flex-1 flex-col">
          <Topbar userName={userName} notificationCount={counts.documents} />
          <main className="flex-1 px-4.5 py-6 min-[1001px]:px-7.5 min-[1001px]:py-6.5">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  );
}
