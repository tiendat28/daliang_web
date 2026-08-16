import { prisma } from "@daliang/db";
import { auth } from "@/auth";
import { formatDateVn, formatVnd } from "@/lib/dlvc/format";
import KpiCard from "@/components/dlvc/admin/KpiCard";
import RecentActivityCard, { type ActivityItem } from "@/components/dlvc/admin/RecentActivityCard";
import DepartmentDocsCard, { type DeptDocCount } from "@/components/dlvc/admin/DepartmentDocsCard";

async function getOverviewData() {
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  const sevenDaysAgo = new Date(now.getTime() - 7 * 86_400_000);
  const in30Days = new Date(now.getTime() + 30 * 86_400_000);

  const [
    activeEmployees,
    newHiresThisMonth,
    pendingDocuments,
    recentPendingDocuments,
    invoicesThisMonth,
    invoicesThisMonthValue,
    expiringDocuments,
    activityRows,
    departments,
  ] = await Promise.all([
    prisma.employee.count({ where: { status: "active" } }),
    prisma.employee.count({ where: { hireDate: { gte: monthStart, lt: monthEnd } } }),
    prisma.adminDocument.count({ where: { status: "pending" } }),
    prisma.adminDocument.count({ where: { status: "pending", createdAt: { gte: sevenDaysAgo } } }),
    prisma.invoice.count({ where: { issueDate: { gte: monthStart, lt: monthEnd } } }),
    prisma.invoice.aggregate({
      where: { issueDate: { gte: monthStart, lt: monthEnd } },
      _sum: { totalAmount: true },
    }),
    prisma.adminDocument.count({
      where: { expiryDate: { gte: now, lte: in30Days }, status: { in: ["pending", "approved"] } },
    }),
    prisma.documentHistory.findMany({
      take: 8,
      orderBy: { performedAt: "desc" },
      include: {
        document: { include: { department: true } },
        performer: true,
      },
    }),
    prisma.adminDepartment.findMany({
      include: { _count: { select: { documents: true } } },
      orderBy: { documents: { _count: "desc" } },
    }),
  ]);

  const activity: ActivityItem[] = activityRows.map((row) => ({
    id: row.id,
    action: row.action,
    performedAt: row.performedAt,
    performerName: row.performer.fullName,
    documentTitle: row.document.title,
    departmentName: row.document.department.departmentName,
    departmentColor: row.document.department.color,
  }));

  const departmentDocs: DeptDocCount[] = departments.map((d) => ({
    id: d.id,
    name: d.departmentName,
    color: d.color,
    count: d._count.documents,
  }));

  return {
    activeEmployees,
    newHiresThisMonth,
    pendingDocuments,
    recentPendingDocuments,
    invoicesThisMonth,
    invoicesThisMonthValue: invoicesThisMonthValue._sum.totalAmount ?? 0,
    expiringDocuments,
    activity,
    departmentDocs,
  };
}

export default async function AdminOverviewPage() {
  const [session, data] = await Promise.all([auth(), getOverviewData()]);
  const now = new Date();
  const weekday = now.toLocaleDateString("vi-VN", { weekday: "long" });
  const time = now.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });

  return (
    <div>
      <div className="mb-5.5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[21px] font-bold tracking-tight text-dlvc-ink">Tổng quan</h1>
          <p className="mt-0.75 text-[13px] text-dlvc-ink-soft">
            {weekday.charAt(0).toUpperCase() + weekday.slice(1)}, {formatDateVn(now)} — Cập nhật lúc {time}
            {session?.user?.name ? ` · Xin chào, ${session.user.name}` : ""}
          </p>
        </div>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-4 min-[560px]:grid-cols-2 min-[1200px]:grid-cols-4">
        <KpiCard
          label="Nhân sự đang làm việc"
          value={data.activeEmployees}
          delta={data.newHiresThisMonth > 0 ? `↑ ${data.newHiresThisMonth} người trong tháng` : undefined}
        />
        <KpiCard
          label="Tài liệu chờ duyệt"
          value={data.pendingDocuments}
          delta={data.recentPendingDocuments > 0 ? `↑ ${data.recentPendingDocuments} mới trong tuần` : undefined}
          down
          accentColor="var(--color-dlvc-dept-hcns)"
        />
        <KpiCard
          label="Hoá đơn tháng này"
          value={data.invoicesThisMonth}
          delta={`${formatVnd(data.invoicesThisMonthValue)} tổng giá trị`}
          accentColor="var(--color-dlvc-dept-hoa-don)"
        />
        <KpiCard
          label="Tài liệu sắp hết hạn"
          value={data.expiringDocuments}
          delta="Trong 30 ngày tới"
          down={data.expiringDocuments > 0}
          accentColor="var(--color-dlvc-dept-ky-thuat)"
        />
      </div>

      <div className="grid grid-cols-1 items-start gap-4.5 min-[1100px]:grid-cols-[1.5fr_1fr]">
        <RecentActivityCard items={data.activity} />
        <DepartmentDocsCard items={data.departmentDocs} />
      </div>
    </div>
  );
}
