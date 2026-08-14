# Daliang Web

Hệ thống quản lý tài liệu nội bộ (kho tài liệu, tra cứu, xử lý OCR/preview) — monorepo gồm frontend Next.js, worker xử lý tài liệu bằng Python/Celery, và các package dùng chung.

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
- Phần UI hiện tại trong `apps/web/components/mock` và `apps/web/lib/mock-data.ts` là dữ liệu/màn hình mock, chưa nối vào `packages/db`.
