# Daliang VN — Quản lý phòng thí nghiệm hóa chất

Ứng dụng quản lý nội bộ cho: khách hàng, sản phẩm công ty, tồn kho hóa chất
phòng thí nghiệm, chất chỉ thị, thiết bị, đơn pha chế hóa chất thử nghiệm,
lấy mẫu, báo cáo phân tích, nhật ký công tác và tài liệu.

Stack: **Vue 3 + Tailwind CSS** (frontend) · **FastAPI + SQLAlchemy** (backend)
· **PostgreSQL** (database) · **Docker Compose**.

## 1. Cách chạy

```bash
docker compose up -d --build
```

| Thành phần | Địa chỉ |
|---|---|
| Frontend | http://localhost:5173 |
| Backend (Swagger) | http://localhost:8001/docs |
| Postgres | localhost:5433 — user/pass `labuser` / `labpass`, db `labdb` |

Dừng (giữ nguyên dữ liệu): `docker compose stop`. Dữ liệu nằm trong volume
`db_data`, không mất khi build lại image.

## 2. Cấu trúc dự án

```
chemical-manager/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile                  # kèm libreoffice để xem trước file Word
│   ├── requirements.txt
│   └── app/
│       ├── main.py                 # khởi tạo FastAPI, tạo bảng, gắn router
│       ├── models.py               # toàn bộ model SQLAlchemy (schema DB)
│       ├── schemas.py              # Pydantic schema (validate/response)
│       ├── core/
│       │   ├── config.py           # đọc biến môi trường
│       │   ├── database.py         # engine, session, Base
│       │   └── migrations.py       # thêm cột mới cho bảng đã tồn tại
│       ├── services/
│       │   └── inventory.py        # trừ/hoàn tồn kho "Lẻ"
│       └── api/                    # 1 file router / 1 nhóm chức năng
│           ├── common.py           # get_or_404 + apply_payload dùng chung
│           ├── customers.py, company_products.py, lab_chemicals.py,
│           ├── indicators.py, equipment.py, chemical_orders.py,
│           └── chemical_sampling.py, analysis_reports.py, work_logs.py, documents.py
└── frontend/
    ├── Dockerfile
    ├── tailwind.config.js / vite.config.js
    └── src/
        ├── main.js / App.vue / router/index.js
        ├── api/                    # client axios + khai báo endpoint
        ├── composables/
        │   ├── useCrudResource.js  # rows + modal + form + load/save/remove
        │   └── useSearchedRows.js  # lọc theo ô tìm kiếm trên Topbar
        ├── constants/              # giá trị dùng chung (công đoạn mạ...)
        ├── components/
        │   ├── TableCard.vue       # khung card chung của mọi bảng
        │   ├── DataTable.vue       # bảng dữ liệu + lọc/sắp xếp/phân trang
        │   ├── TablePagination.vue, Modal.vue, DynamicForm.vue,
        │   ├── FormActions.vue, MonthPicker.vue, ToolbarButton.vue
        │   ├── layout/             # Sidebar, Topbar, AppLayout, SettingsPanel
        │   ├── analysis-reports/, documents/
        ├── utils/                  # format, chemFormula, excelReport, reportSheets, pdfReport...
        └── views/                  # 1 view / 1 trang nghiệp vụ
```

## 3. Schema database (PostgreSQL)

| Bảng | Tương ứng ghi chú tay | Ghi chú |
|---|---|---|
| `customers` | Bảng 1 – KH | |
| `customer_fields` | (lĩnh vực của KH) | 1 KH – n lĩnh vực |
| `customer_field_products` | (SP dùng theo lĩnh vực) | tự map sang `company_products` nếu trùng mã |
| `company_products` | Bảng 2 – SP Cty | `process_stage`: pre_treatment / plating / post_plating |
| `lab_chemicals` | Bảng 3 – HC PTN | `box_count` × `volume_per_box` = `total_volume`; `remaining_volume` là phần "Lẻ" đang dùng |
| `indicators` | Chất chỉ thị | |
| `equipment` / `equipment_variants` | Bảng 4 – Thiết bị | 1 thiết bị có nhiều phân loại |
| `chemical_orders` | Bảng 5 – Đơn hàng HCTN | FK tới `lab_chemicals` và `customers` |
| `chemical_sampling` | Bảng 6 – Lấy mẫu HC | FK tới `company_products` |
| `analysis_reports` / `analysis_samples` / `analysis_components` | Báo cáo phân tích | 1 báo cáo – n mẫu – n chỉ tiêu |
| `work_logs` | Nhật ký công tác | `log_date`, `content`, `ot_hours` (số giờ tăng ca) |
| `documents` | Tài liệu | file lưu thẳng trong DB (cột `content`) |

Bảng được tạo tự động khi backend khởi động (`Base.metadata.create_all`).
`create_all` **không** thêm cột vào bảng đã có, nên mỗi cột bổ sung về sau được
khai báo trong `app/core/migrations.py` (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS`).

### Logic tồn kho tự động
- Tạo/sửa/xoá một **đơn hàng HCTN** sẽ tự động trừ/hoàn `used_amount` vào
  `lab_chemicals.remaining_volume` ("Lẻ") — **không cảnh báo**, cho phép âm nếu vượt tồn.
- Hộp đang dùng gần hết thì bấm **"Mở hộp mới"** ở bảng Hóa chất PTN: trừ 1 hộp
  trong kho, reset `remaining_volume` về đúng dung tích 1 hộp.

## 4. Giao diện

Sidebar + card bo tròn trên nền gradient mint/lavender, có chế độ tối (Cài đặt).
Mỗi trang nghiệp vụ = 1 `TableCard`: tiêu đề + nút thao tác ở trên, bảng cuộn ở
giữa, phân trang ở chân — card tự co theo chiều cao màn hình nên chân bảng luôn
nhìn thấy. Màn hình nhỏ (`sm`) đổi sang danh sách thẻ.

Form đơn giản dùng `DynamicForm` (sinh input theo cấu hình field); Khách hàng,
Thiết bị, Đơn hàng HCTN và Báo cáo phân tích có form riêng vì dữ liệu lồng nhau.

## 5. Xuất dữ liệu

- Trang **Hóa chất** và **Thiết bị**: nút "Xuất Excel" theo tháng đang chọn.
- Trang **Nhật ký công tác**: nút "Xuất PDF".
- **Cài đặt → Xuất dữ liệu**: chọn nhiều bảng, xuất 1 file Excel nhiều sheet
  hoặc 1 file PDF; kèm chức năng sao lưu / khôi phục JSON.

Mẫu sheet Excel (logo, tên công ty, header xanh, viền, Times New Roman) nằm ở
`utils/excelReport.js`; từng sheet nghiệp vụ ở `utils/reportSheets.js` và được
dùng chung cho cả nút xuất ở trang lẫn phần xuất trong Cài đặt.

## 6. Giả định thiết kế đã áp dụng

1. Trừ tồn kho "Lẻ" tự động, **không** có cơ chế cảnh báo hết hàng.
2. **Chưa** có đăng nhập/phân quyền — ứng dụng dùng nội bộ, mở tự do.
3. Khách hàng: nhập lĩnh vực + danh sách mã SP dùng dạng text (cách nhau bởi
   dấu phẩy); hệ thống tự dò và liên kết (FK) tới `company_products` nếu mã
   trùng khớp, không trùng thì lưu dạng text tự do.

## 7. Hướng mở rộng (chưa làm)

- Trang Dashboard tổng quan (tồn kho thấp, đơn hàng gần đây…).
- Phân quyền người dùng, cảnh báo tồn kho thấp.
