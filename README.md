# Daliang VN — Quản lý phòng thí nghiệm hóa chất

Ứng dụng quản lý nội bộ cho: khách hàng, sản phẩm công ty, tồn kho hóa chất
phòng thí nghiệm, thiết bị, đơn pha chế hóa chất thử nghiệm và lấy mẫu.

Stack: **Vue 3 + Tailwind CSS** (frontend) · **FastAPI + SQLAlchemy** (backend)
· **PostgreSQL** (database) · **Docker Compose**.

## 1. Cấu trúc dự án

```
lab-chemical-manager/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # khởi tạo FastAPI, tạo bảng, gắn router
│       ├── models.py          # toàn bộ model SQLAlchemy (schema DB)
│       ├── schemas.py         # Pydantic schema (validate/response)
│       ├── core/
│       │   ├── config.py      # đọc biến môi trường
│       │   └── database.py    # engine, session, Base
│       ├── services/
│       │   └── inventory.py   # logic tự động trừ/hoàn tồn kho "Lẻ"
│       └── api/                # 1 file router / 1 nhóm chức năng
│           ├── customers.py
│           ├── company_products.py
│           ├── lab_chemicals.py
│           ├── equipment.py
│           ├── chemical_orders.py
│           └── chemical_sampling.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── tailwind.config.js
    ├── vite.config.js
    └── src/
        ├── main.js / App.vue
        ├── router/index.js
        ├── api/                    # gọi API backend (axios)
        ├── components/
        │   ├── layout/              # Sidebar, Topbar, AppLayout (theo style tham khảo)
        │   ├── DataTable.vue         # bảng dữ liệu dùng chung cho mọi màn hình
        │   ├── Modal.vue
        │   └── DynamicForm.vue       # form nhập liệu sinh tự động theo cấu hình field
        └── views/                    # 1 view / 1 bảng nghiệp vụ
            ├── CustomersView.vue
            ├── CompanyProductsView.vue
            ├── LabChemicalsView.vue
            ├── EquipmentView.vue
            ├── ChemicalOrdersView.vue
            └── ChemicalSamplingView.vue
```

## 2. Schema database (PostgreSQL)

| Bảng | Tương ứng ghi chú tay | Ghi chú |
|---|---|---|
| `customers` | Bảng 1 – KH | |
| `customer_fields` | (lĩnh vực của KH) | 1 KH – n lĩnh vực |
| `customer_field_products` | (SP dùng theo lĩnh vực) | n SP dùng / lĩnh vực, tự map sang `company_products` nếu trùng mã |
| `company_products` | Bảng 2 – SP Cty | `process_stage`: pre_treatment / plating / post_plating |
| `lab_chemicals` | Bảng 3 – HC PTN | `box_count` (số hộp còn nguyên) × `volume_per_box` = `total_volume`; `remaining_volume` là phần "Lẻ" đang dùng |
| `equipment` / `equipment_variants` | Bảng 4 – Thiết bị | equipment có thể có nhiều `variants` (VD: pH có 3 dòng phân loại 5/10/20 cái) |
| `chemical_orders` | Bảng 5 – Đơn hàng HCTN | FK tới `lab_chemicals` (Mã HC) và `customers` (KH) |
| `chemical_sampling` | Bảng 6 – Lấy mẫu HC | FK tới `company_products` (Mã HC ở bảng này thực chất là mã SP công ty) |

Bảng được tạo tự động khi backend khởi động (`Base.metadata.create_all`),
không cần chạy migration thủ công cho bản MVP này.

### Logic tồn kho tự động
- Khi tạo/sửa/xoá một **đơn hàng HCTN**, `used_amount` sẽ tự động trừ/hoàn vào
  `lab_chemicals.remaining_volume` ("Lẻ") — **không cảnh báo**, có thể âm nếu vượt tồn (theo yêu cầu).
- Khi hộp đang dùng gần hết, dùng nút **"Mở hộp mới"** ở bảng Hóa chất PTN
  (icon hộp bên cạnh Sửa/Xoá): trừ 1 hộp trong kho, reset `remaining_volume`
  về đúng dung tích 1 hộp.

## 3. Cách chạy

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend (Swagger docs): http://localhost:8000/docs
- Postgres: localhost:5432 (user/pass: `labuser` / `labpass`, db: `labdb`)

## 4. Thiết kế giao diện

Sidebar + dashboard theo phong cách tham khảo (nền gradient mint/lavender nhẹ,
card bo tròn lớn, sidebar trắng mờ với mục đang chọn tô nền gradient xanh ngọc).
Mỗi bảng nghiệp vụ có 1 trang riêng gồm: bảng dữ liệu (`DataTable`) + nút
"Thêm mới" mở modal chứa form nhập liệu. Component `DynamicForm` dùng chung
cho các form đơn giản (sinh input theo cấu hình field); Khách hàng và Thiết bị
dùng form riêng vì có dữ liệu lồng nhau (lĩnh vực/SP dùng, phân loại thiết bị).

## 5. Giả định thiết kế đã áp dụng (theo xác nhận)

1. Đã xác nhận đúng cách hiểu 5 điểm về schema (hộp/dung tích, tên trường,
   phân loại thiết bị pH, v.v).
2. Trừ tồn kho "Lẻ" tự động, **không** có cơ chế cảnh báo hết hàng.
3. **Chưa** có đăng nhập/phân quyền — ứng dụng dùng nội bộ, mở tự do.
4. Với Khách hàng: nhập lĩnh vực + danh sách mã SP dùng dạng text (cách nhau
   bởi dấu phẩy); hệ thống tự dò và liên kết (FK) tới `company_products` nếu
   mã trùng khớp, nếu không sẽ lưu dạng text tự do — tránh việc phải chọn
   từng SP thủ công cho mỗi lĩnh vực.

## 6. Hướng mở rộng (chưa làm trong bản này)

- Trang Dashboard tổng quan (số liệu tồn kho thấp, đơn hàng gần đây…).
- Phân quyền người dùng khi cần.
- Cảnh báo tồn kho thấp nếu sau này đổi ý.
- Export Excel/PDF cho từng bảng.

Có gì cần chỉnh (tên trường, thêm bảng, đổi giao diện...) cứ báo để cập nhật lại.
