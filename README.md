# Daliang Web

Monorepo chứa hai hệ thống độc lập:

- **DLVC** (`apps/web/app/dlvc`) — website công khai + trang quản trị nội bộ cho Công ty TNHH Hóa chất Daliang VN. Landing page tại `/dlvc`, quản trị (nhân sự/tài liệu/hoá đơn) tại `/dlvc/admin` (yêu cầu đăng nhập, xem `apps/web/auth.ts`).
- **Hạ tầng quản lý tài liệu nội bộ** (kho tài liệu, tra cứu, xử lý OCR/preview) — `apps/worker` (Python/Celery) + các model `Department/User/Document` trong `packages/db/schema.prisma`. Phần giao diện Next.js của hệ thống này đã được gỡ bỏ; hạ tầng backend vẫn còn để dùng lại sau nếu cần.

## Cấu trúc thư mục

```
apps/
  web/        Next.js 16 (App Router) — giao diện chính
  worker/     Celery worker (Python) — trích xuất văn bản, OCR, tạo preview
packages/
  db/         Prisma schema + client dùng chung (Postgres)
  shared/     Types/schema (zod) dùng chung giữa các app
docker-compose.yml   Hạ tầng local: Postgres, Redis, MinIO, worker
```

## Yêu cầu môi trường

- Node.js 20+, npm
- Python 3.11+ (cho `apps/worker`)
- Docker (để chạy Postgres/Redis/MinIO qua `docker-compose`)

## Cài đặt

```bash
npm install
cp .env.example .env
```

Chỉnh `.env` nếu cần (mặc định đã khớp với `docker-compose.yml`).

## Chạy hạ tầng local

```bash
docker compose up -d
```

Khởi động Postgres (`5432`), Redis (`6379`), MinIO (`9000`, console `9001`) và worker xử lý tài liệu.

## Database (Prisma)

```bash
npm run db:generate   # generate Prisma client
npm run db:migrate    # chạy migration (dev)
npm run db:seed       # seed dữ liệu mẫu
npm run db:studio     # mở Prisma Studio
```

## Chạy web app

```bash
npm run dev
```

Mở [http://localhost:3000](http://localhost:3000).

Các script khác: `npm run build`, `npm run start`, `npm run lint`.

## Ghi chú

- `apps/web` dùng Next.js 16 — một số API (vd. `usePathname`) có thay đổi so với bản trước, xem `apps/web/AGENTS.md`.
- `apps/web/.env` cần biến `AUTH_SECRET` riêng (NextAuth cho `/dlvc/admin`) ngoài `DATABASE_URL` — xem `apps/web/.env.example`. Next.js đọc env từ `apps/web/`, không phải từ thư mục gốc.
- `packages/shared` hiện chưa được `apps/web` hay `packages/db` sử dụng — cân nhắc xoá nếu không có kế hoạch dùng lại.
