import { PrismaClient } from "./generated/prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";
import bcrypt from "bcryptjs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { mkdir, writeFile } from "node:fs/promises";

const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL! });
const prisma = new PrismaClient({ adapter });

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// Seeded documents' filePath ("/uploads/seed/...") must resolve to a real file
// under apps/web/public so the "Tải xuống" link in the DLVC admin UI works.
const SEED_UPLOAD_DIR = path.join(__dirname, "..", "..", "apps", "web", "public", "uploads", "seed");

async function writeSeedPlaceholderFile(fileName: string, title: string) {
  await mkdir(SEED_UPLOAD_DIR, { recursive: true });
  await writeFile(
    path.join(SEED_UPLOAD_DIR, fileName),
    `Đây là tệp mẫu (seed data) cho tài liệu "${title}".\nNội dung thật sẽ được tải lên qua chức năng "Tải tài liệu lên" trong hệ thống.\n`,
  );
}

// ============================================================
// DLVC INTERNAL ADMIN SYSTEM — seed data taken from docs/admin-mockup.html
// ============================================================
async function seedDlvc() {
  const DEFAULT_PASSWORD = "password123";
  const passwordHash = await bcrypt.hash(DEFAULT_PASSWORD, 10);

  // --- Departments ---
  const deptDefs = [
    { code: "DEPT-ENG", name: "Kỹ thuật", color: "#2E6E6A" },
    { code: "DEPT-HR", name: "Hành chính - Nhân sự", color: "#6B4FA0" },
    { code: "DEPT-FIN", name: "Kế toán", color: "#C99A3D" },
  ] as const;

  const depts: Record<string, Awaited<ReturnType<typeof prisma.adminDepartment.upsert>>> = {};
  for (const d of deptDefs) {
    depts[d.code] = await prisma.adminDepartment.upsert({
      where: { departmentCode: d.code },
      update: {},
      create: { departmentCode: d.code, departmentName: d.name, color: d.color },
    });
  }

  // --- Positions ---
  const positionNames = [
    "Kế toán trưởng",
    "Trưởng phòng HCNS",
    "Kỹ sư vận hành",
    "Kế toán thanh toán",
    "Trưởng phòng Kỹ thuật",
    "Chuyên viên tuyển dụng",
    "Nhân viên hành chính",
    "Kế toán công nợ",
    "Quản trị viên",
  ];
  const positions: Record<string, Awaited<ReturnType<typeof prisma.position.create>>> = {};
  for (const name of positionNames) {
    const existing = await prisma.position.findFirst({ where: { positionName: name } });
    positions[name] = existing ?? (await prisma.position.create({ data: { positionName: name } }));
  }

  // --- Employees ---
  const employeeDefs = [
    { code: "NV-0231", name: "Nguyễn Văn An", dept: "DEPT-FIN", position: "Kế toán trưởng", hire: "2019-03-12", status: "active" as const, email: "an.nguyen@daliangvn.com" },
    { code: "NV-0198", name: "Trần Thị Bích", dept: "DEPT-HR", position: "Trưởng phòng HCNS", hire: "2018-11-05", status: "active" as const, email: "bich.tran@daliangvn.com" },
    { code: "NV-0304", name: "Lê Hoàng Nam", dept: "DEPT-ENG", position: "Kỹ sư vận hành", hire: "2021-07-21", status: "on_leave" as const, email: "nam.le@daliangvn.com" },
    { code: "NV-0276", name: "Phạm Thu Hà", dept: "DEPT-FIN", position: "Kế toán thanh toán", hire: "2020-02-14", status: "active" as const, email: "ha.pham@daliangvn.com" },
    { code: "NV-0312", name: "Đỗ Minh Tuấn", dept: "DEPT-ENG", position: "Trưởng phòng Kỹ thuật", hire: "2017-09-09", status: "active" as const, email: "tuan.do@daliangvn.com" },
    { code: "NV-0155", name: "Vũ Thị Lan", dept: "DEPT-HR", position: "Chuyên viên tuyển dụng", hire: "2022-06-03", status: "active" as const, email: "lan.vu@daliangvn.com" },
    { code: "NV-0341", name: "Ngô Thanh Trúc", dept: "DEPT-HR", position: "Nhân viên hành chính", hire: "2026-08-02", status: "probation" as const, email: "truc.ngo@daliangvn.com" },
    { code: "NV-0089", name: "Hoàng Đức Thịnh", dept: "DEPT-FIN", position: "Kế toán công nợ", hire: "2016-01-17", status: "terminated" as const, email: "thinh.hoang@daliangvn.com", termination: "2026-07-31" },
    { code: "NV-0001", name: "Trần Thu Loan", dept: "DEPT-HR", position: "Quản trị viên", hire: "2015-01-01", status: "active" as const, email: "loan.tran@daliangvn.com" },
  ];

  const employees: Record<string, Awaited<ReturnType<typeof prisma.employee.upsert>>> = {};
  for (const e of employeeDefs) {
    employees[e.code] = await prisma.employee.upsert({
      where: { employeeCode: e.code },
      update: {},
      create: {
        employeeCode: e.code,
        fullName: e.name,
        email: e.email,
        departmentId: depts[e.dept].id,
        positionId: positions[e.position].id,
        hireDate: new Date(e.hire),
        terminationDate: e.termination ? new Date(e.termination) : null,
        status: e.status,
      },
    });
  }

  // Department heads
  await prisma.adminDepartment.update({
    where: { departmentCode: "DEPT-ENG" },
    data: { headEmployeeId: employees["NV-0312"].id },
  });
  await prisma.adminDepartment.update({
    where: { departmentCode: "DEPT-HR" },
    data: { headEmployeeId: employees["NV-0198"].id },
  });
  await prisma.adminDepartment.update({
    where: { departmentCode: "DEPT-FIN" },
    data: { headEmployeeId: employees["NV-0231"].id },
  });

  // --- Roles ---
  const roleDefs = [
    { name: "Admin", permissions: { "*": true } },
    { name: "Trưởng phòng", permissions: { "documents.approve": true, "employees.view": true, "employees.edit": true, "invoices.view": true } },
    { name: "Nhân viên", permissions: { "documents.upload": true, "profile.view": true } },
  ];
  const roles: Record<string, Awaited<ReturnType<typeof prisma.role.upsert>>> = {};
  for (const r of roleDefs) {
    roles[r.name] = await prisma.role.upsert({
      where: { roleName: r.name },
      update: {},
      create: { roleName: r.name, permissions: r.permissions },
    });
  }

  // --- Login accounts ---
  const userDefs = [
    { username: "loan.tran", employee: "NV-0001", role: "Admin" },
    { username: "tuan.do", employee: "NV-0312", role: "Trưởng phòng" },
    { username: "bich.tran", employee: "NV-0198", role: "Trưởng phòng" },
    { username: "an.nguyen", employee: "NV-0231", role: "Trưởng phòng" },
    { username: "ha.pham", employee: "NV-0276", role: "Nhân viên" },
  ];
  for (const u of userDefs) {
    await prisma.adminUser.upsert({
      where: { username: u.username },
      update: {},
      create: {
        username: u.username,
        passwordHash,
        employeeId: employees[u.employee].id,
        roleId: roles[u.role].id,
      },
    });
  }

  // --- Document types ---
  const docTypeDefs = [
    { name: "Quy trình vận hành", dept: "DEPT-ENG" },
    { name: "Bản vẽ kỹ thuật", dept: "DEPT-ENG" },
    { name: "Tiêu chuẩn an toàn", dept: "DEPT-ENG" },
    { name: "Hợp đồng lao động", dept: "DEPT-HR" },
    { name: "Báo cáo tài chính", dept: "DEPT-FIN" },
    { name: "Sổ sách kế toán", dept: "DEPT-FIN" },
  ];
  const docTypes: Record<string, Awaited<ReturnType<typeof prisma.documentType.create>>> = {};
  for (const dt of docTypeDefs) {
    const existing = await prisma.documentType.findFirst({ where: { typeName: dt.name, departmentId: depts[dt.dept].id } });
    docTypes[dt.name] = existing ?? (await prisma.documentType.create({ data: { typeName: dt.name, departmentId: depts[dt.dept].id } }));
  }

  // --- Documents ---
  const docDefs = [
    { title: "Quy trình vận hành máy CNC-04", dept: "DEPT-ENG", type: "Quy trình vận hành", format: "PDF", sizeKb: 4300, uploader: "NV-0312", status: "approved" as const, approver: "NV-0001" },
    { title: "Bản vẽ kỹ thuật – Dây chuyền A", dept: "DEPT-ENG", type: "Bản vẽ kỹ thuật", format: "DWG", sizeKb: 1840, uploader: "NV-0304", status: "pending" as const },
    { title: "Tiêu chuẩn an toàn lao động xưởng 2", dept: "DEPT-ENG", type: "Tiêu chuẩn an toàn", format: "PDF", sizeKb: 2150, uploader: "NV-0312", status: "expired" as const, expiry: "2026-07-01" },
    { title: "Hợp đồng lao động – Ngô Thanh Trúc", dept: "DEPT-HR", type: "Hợp đồng lao động", format: "DOCX", sizeKb: 320, uploader: "NV-0155", status: "pending" as const },
    { title: "Báo cáo tài chính Q2/2026", dept: "DEPT-FIN", type: "Báo cáo tài chính", format: "XLSX", sizeKb: 890, uploader: "NV-0231", status: "approved" as const, approver: "NV-0001" },
    { title: "Sổ sách kế toán tháng 7/2026", dept: "DEPT-FIN", type: "Sổ sách kế toán", format: "PDF", sizeKb: 1100, uploader: "NV-0276", status: "approved" as const, approver: "NV-0001" },
  ];

  for (const d of docDefs) {
    const fileName = `${d.title.replace(/[^a-zA-Z0-9]+/g, "-").toLowerCase()}.${d.format.toLowerCase()}`;
    await writeSeedPlaceholderFile(fileName, d.title);

    const existing = await prisma.adminDocument.findFirst({ where: { title: d.title } });
    const doc =
      existing ??
      (await prisma.adminDocument.create({
        data: {
          title: d.title,
          departmentId: depts[d.dept].id,
          documentTypeId: docTypes[d.type].id,
          filePath: `/uploads/seed/${fileName}`,
          fileFormat: d.format,
          fileSizeKb: d.sizeKb,
          uploadedBy: employees[d.uploader].id,
          approvedBy: d.approver ? employees[d.approver].id : null,
          approvedAt: d.approver ? new Date() : null,
          status: d.status,
          expiryDate: d.expiry ? new Date(d.expiry) : null,
        },
      }));

    const historyCount = await prisma.documentHistory.count({ where: { documentId: doc.id } });
    if (historyCount === 0) {
      await prisma.documentHistory.create({
        data: { documentId: doc.id, action: "uploaded", performedBy: employees[d.uploader].id },
      });
      if (d.approver) {
        await prisma.documentHistory.create({
          data: { documentId: doc.id, action: "approved", performedBy: employees[d.approver].id },
        });
      }
    }
  }

  // --- Partners ---
  const partnerDefs = [
    { code: "PTN-001", name: "Công ty CP Xây dựng Đại Phát", type: "customer" as const },
    { code: "PTN-002", name: "Công ty TNHH Vật tư Miền Nam", type: "supplier" as const },
    { code: "PTN-003", name: "Siêu thị Bình Minh", type: "customer" as const },
    { code: "PTN-004", name: "Nhà máy thép Hoà Phát", type: "supplier" as const },
    { code: "PTN-005", name: "Công ty CP Thương mại Việt Tín", type: "customer" as const },
    { code: "PTN-006", name: "Công ty TNHH Bao bì An Khang", type: "supplier" as const },
  ];
  const partners: Record<string, Awaited<ReturnType<typeof prisma.partner.upsert>>> = {};
  for (const p of partnerDefs) {
    partners[p.code] = await prisma.partner.upsert({
      where: { partnerCode: p.code },
      update: {},
      create: { partnerCode: p.code, partnerName: p.name, type: p.type },
    });
  }

  // --- Invoices (+ items, + payments) ---
  const invoiceDefs = [
    { number: "HD-2026-0847", type: "sale" as const, partner: "PTN-001", issue: "2026-08-16", due: "2026-09-15", total: 86_400_000, status: "unpaid" as const, creator: "NV-0276", item: "Hoá chất tiền xử lý EB-C" },
    { number: "HD-2026-0846", type: "purchase" as const, partner: "PTN-002", issue: "2026-08-15", due: "2026-08-30", total: 42_150_000, status: "paid" as const, creator: "NV-0276", item: "Vật tư đóng gói" },
    { number: "HD-2026-0839", type: "sale" as const, partner: "PTN-003", issue: "2026-08-13", due: "2026-08-28", total: 128_900_000, status: "paid" as const, creator: "NV-0276", item: "Phụ gia mạ niken NI-534C" },
    { number: "HD-2026-0812", type: "purchase" as const, partner: "PTN-004", issue: "2026-08-08", due: "2026-08-15", total: 310_000_000, status: "overdue" as const, creator: "NV-0231", item: "Thép nguyên liệu" },
    { number: "HD-2026-0801", type: "sale" as const, partner: "PTN-005", issue: "2026-08-04", due: "2026-08-19", total: 57_600_000, status: "paid" as const, creator: "NV-0276", item: "Dung dịch thụ động CRT-650" },
    { number: "HD-2026-0788", type: "purchase" as const, partner: "PTN-006", issue: "2026-08-01", due: "2026-08-16", total: 19_850_000, status: "paid" as const, creator: "NV-0231", item: "Bao bì đóng gói" },
  ];

  for (const inv of invoiceDefs) {
    const existing = await prisma.invoice.findUnique({ where: { invoiceNumber: inv.number } });
    const invoice =
      existing ??
      (await prisma.invoice.create({
        data: {
          invoiceNumber: inv.number,
          type: inv.type,
          partnerId: partners[inv.partner].id,
          createdBy: employees[inv.creator].id,
          issueDate: new Date(inv.issue),
          dueDate: new Date(inv.due),
          totalAmount: inv.total,
          status: inv.status,
        },
      }));

    const itemCount = await prisma.invoiceItem.count({ where: { invoiceId: invoice.id } });
    if (itemCount === 0) {
      await prisma.invoiceItem.create({
        data: {
          invoiceId: invoice.id,
          itemName: inv.item,
          unit: "kg",
          quantity: 1,
          unitPrice: inv.total,
        },
      });
    }

    if (inv.status === "paid") {
      const paymentCount = await prisma.payment.count({ where: { invoiceId: invoice.id } });
      if (paymentCount === 0) {
        await prisma.payment.create({
          data: {
            invoiceId: invoice.id,
            amount: inv.total,
            paymentDate: new Date(inv.issue),
            method: "bank_transfer",
            confirmedBy: employees[inv.creator].id,
          },
        });
      }
    }
  }

  // --- Sample leads (contact form) ---
  const leadDefs = [
    { name: "Nguyễn Văn Bình", company: "Nhà máy Cơ khí Bình Dương", phone: "0908123456", email: "binh.nguyen@example.com", message: "Cần báo giá hoá chất mạ kẽm cho dây chuyền mới.", status: "newLead" as const },
    { name: "Trần Thị Hồng", company: "Công ty TNHH Xi mạ Phương Nam", phone: "0913456789", email: "hong.tran@example.com", message: "Muốn tư vấn về dung dịch thụ động cho lớp mạ crom.", status: "contacted" as const },
  ];
  for (const l of leadDefs) {
    const existing = await prisma.lead.findFirst({ where: { email: l.email } });
    if (!existing) {
      await prisma.lead.create({
        data: { fullName: l.name, companyName: l.company, phone: l.phone, email: l.email, message: l.message, status: l.status },
      });
    }
  }

  console.log("Seeded (DLVC admin system):", {
    departments: deptDefs.length,
    employees: employeeDefs.length,
    roles: roleDefs.length,
    users: userDefs.length,
    documents: docDefs.length,
    partners: partnerDefs.length,
    invoices: invoiceDefs.length,
    leads: leadDefs.length,
  });
  console.log(`Default login password for all seeded DLVC users: "${DEFAULT_PASSWORD}"`);
}

seedDlvc()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (e) => {
    console.error(e);
    await prisma.$disconnect();
    process.exit(1);
  });
