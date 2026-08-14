import { PrismaClient } from "./generated/prisma/client";
import { PrismaPg } from "@prisma/adapter-pg";

const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL! });
const prisma = new PrismaClient({ adapter });

async function main() {
  const department = await prisma.department.upsert({
    where: { code: "IT" },
    update: {},
    create: { name: "Phòng Công nghệ thông tin", code: "IT" },
  });

  const user = await prisma.user.upsert({
    where: { email: "an.nguyen@daliang.vn" },
    update: {},
    create: {
      email: "an.nguyen@daliang.vn",
      fullName: "Nguyễn Văn An",
      passwordHash: "seed-placeholder",
      role: "staff",
      departmentId: department.id,
    },
  });

  const documents = [
    {
      code: "QT-001",
      titleVi: "Quy trình tiếp nhận hồ sơ",
      version: "1.0",
    },
    {
      code: "QT-002",
      titleVi: "Quy trình phê duyệt tài liệu",
      version: "2.1",
    },
    {
      code: "HD-003",
      titleVi: "Hướng dẫn sử dụng hệ thống lưu trữ",
      version: "1.3",
    },
  ];

  for (const doc of documents) {
    await prisma.document.upsert({
      where: { code: doc.code },
      update: {},
      create: {
        code: doc.code,
        titleVi: doc.titleVi,
        version: doc.version,
        status: "published",
        ownerId: user.id,
      },
    });
  }

  console.log("Seeded:", { department: department.name, user: user.fullName, documents: documents.length });
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (e) => {
    console.error(e);
    await prisma.$disconnect();
    process.exit(1);
  });
