# Daliang VN — hệ thống quản lý + website

Một repo gồm ba phần, dùng chung một backend và một database:

| Phần | Thư mục | Tên miền | Dùng cho |
|---|---|---|---|
| Website công khai | `apps/landing/` | `daliang.com` | khách hàng: sản phẩm, giấy tờ, tra MSDS, form liên hệ |
| Cổng nội bộ | `apps/portal/` | `[tên-riêng].daliang.com` | nhân viên, mỗi bộ phận một module (hiện có: kỹ thuật, nhân sự, kế toán, hệ thống) |
| Backend | `backend/` | `/api/v1` trên cả hai tên miền | FastAPI, mỗi bộ phận một module |

Stack: **Vue 3 + Vite** (portal thêm Tailwind) · **FastAPI + SQLAlchemy + Alembic**
· **PostgreSQL** · **Docker Compose + nginx**.

## 1. Cách chạy

```bash
cp infra/.env.example infra/.env        # lần đầu, rồi sửa mật khẩu / tên miền
docker compose -f infra/docker-compose.yml up -d --build
```

| Thành phần | Qua nginx (như khi chạy thật) | Mở thẳng cổng |
|---|---|---|
| Website | http://daliang.localhost | http://localhost:5174 |
| Cổng nội bộ | http://noibo.daliang.localhost | http://localhost:5173 |
| API (Swagger) | `/api/v1/...` trên cả hai tên miền | http://localhost:8001/docs |
| Postgres | — | localhost:5433 — `labuser` / `labpass`, db `labdb` |

`*.localhost` tự trỏ về máy mình, không cần sửa file hosts. Hai app gọi API
bằng đường dẫn tương đối `/api/v1` (nginx, hoặc proxy của Vite khi mở thẳng
cổng) nên không có chuyện lệch cổng hay CORS.

- **Lần đầu: tạo tài khoản Admin cao nhất** (hỏi email, họ tên, mật khẩu; lần đăng
  nhập đầu bắt buộc cài 2FA):
  `docker compose -f infra/docker-compose.yml exec backend python -m app.modules.auth.create_admin`
- Dừng (giữ dữ liệu): `docker compose -f infra/docker-compose.yml stop`. Dữ liệu
  nằm trong volume `chemical-manager_db_data` — file compose ghim
  `name: chemical-manager` để luôn dùng lại đúng volume này.
- Test backend: `docker compose -f infra/docker-compose.yml exec backend python -m pytest`
  (chạy trên DB riêng `labdb_test` dựng bằng chính các migration Alembic).
- Sao lưu DB: `sh infra/backup/backup-db.sh` (giữ 30 ngày, cách đặt lịch và
  khôi phục ghi ở đầu file).

## 2. Cấu trúc dự án

```
chemical-manager/
├── apps/
│   ├── landing/                    # Website công khai — Vue + Vite, KHÔNG Tailwind
│   │   ├── index.html
│   │   ├── assets/                 # logo, ảnh, font (Vite phục vụ thẳng: /fonts, /images)
│   │   ├── i18n/                   # vi.json en.json zh.json — chữ giao diện 3 thứ tiếng
│   │   └── src/
│   │       ├── main.js · App.vue · routes.js (sơ đồ URL 3 ngôn ngữ) · api.js · useSite.js
│   │       ├── styles/site.css     # CSS của bản thiết kế gốc (mục 8.3)
│   │       ├── components/         # header, footer, lưới sản phẩm, khối liên hệ…
│   │       └── pages/              # 8 trang theo sơ đồ URL
│   │
│   └── portal/                     # Cổng nội bộ — Vue + Vite + Tailwind
│       └── src/
│           ├── main.js · App.vue
│           ├── router/             # gom route của mọi module
│           ├── core/               # dùng chung mọi bộ phận
│           │   ├── api/            # client axios (tự xin lại phiên khi hết 15'), crud(), common.js, errors.js
│           │   ├── auth/           # đăng nhập: store (user, can()), api, trang login / 2FA / quên MK
│           │   ├── pages/          # trang tổng quan (/), tài khoản của tôi (/profile)
│           │   ├── layouts/        # AdminLayout, Sidebar, Topbar, SettingsPanel, MenuButton
│           │   ├── components/     # DataTable, TableCard, Modal, DynamicForm, MonthPicker…
│           │   ├── composables/    # useCrudResource, useSearchedRows
│           │   ├── store/          # theme, sidebar, pageSearch
│           │   ├── utils/          # format, apiAsset, logo
│           │   └── style.css
│           └── modules/
│               ├── index.js        # danh sách module của cổng
│               ├── lab/            # Kỹ thuật (toàn bộ app cũ)
│               │   ├── index.js · routes.js · api.js
│               │   ├── pages/ components/ composables/ constants/ utils/
│               ├── hr/             # Nhân sự: hồ sơ, chấm công, nghỉ phép, hợp đồng, chứng chỉ, phòng ban
│               │   ├── index.js · routes.js · api.js
│               │   └── pages/      # HrPage.vue
│               ├── accounting/     # Kế toán: hoá đơn bán/mua, công nợ, sổ quỹ, báo cáo
│               │   ├── index.js · routes.js · api.js
│               │   └── pages/      # AccountingPage.vue
│               └── system/         # Hệ thống: tài khoản, vai trò & quyền, website, nhật ký, thông tin công ty
│
├── backend/
│   ├── alembic.ini · migrations/   # thay đổi DB có version (mục 5)
│   ├── tests/
│   └── app/
│       ├── main.py                 # gắn router các module dưới /api/v1, seed mặc định
│       ├── core/                   # config, database, crud, schemas, security (mật khẩu, JWT, TOTP), mailer
│       ├── static/                 # font + logo của tờ in, phục vụ ở /api/v1/static
│       └── modules/
│           ├── __init__.py         # MODULES + load_all_modules() + module_routers()
│           ├── common/             # dữ liệu dùng chung — schema `common`
│           │   ├── models.py schemas.py router.py
│           │   ├── routers/        # customers, products, company_profile, documents
│           │   ├── services/       # catalog (nạp 214 mã), company_profile, documents (file)
│           │   └── data/           # company_products.json + script đổi từ Excel
│           ├── lab/                # kỹ thuật — schema `lab`
│           │   ├── models.py schemas.py router.py seed.py
│           │   ├── routers/        # chemicals, indicators, equipment, formulations, samples,
│           │   │                   # analysis_reports, work_logs, test_processes, process_templates
│           │   ├── services/       # inventory, test_process_*, product_links
│           │   └── templates/      # mẫu Jinja2 của tờ A4
│           ├── hr/                 # nhân sự — schema `hr`
│           │   ├── models.py schemas.py router.py permissions.py
│           ├── accounting/         # kế toán — schema `accounting`
│           │   ├── models.py schemas.py router.py permissions.py seed.py
│           ├── website/            # website công khai — schema `website`
│           ├── auth/               # tài khoản, vai trò, quyền, phiên — schema `auth`
│           │   ├── deps.py         # get_current_user, require(), guard() dùng ở mọi module
│           │   ├── permissions.py  # gom quyền của các module + vai trò mặc định
│           │   └── create_admin.py # lệnh tạo Admin cao nhất
│           └── system/             # quản trị + nhật ký thao tác — schema `system`
│
├── infra/
│   ├── docker-compose.yml          # db · backend · portal · landing · nginx
│   ├── nginx/templates/            # định tuyến 2 tên miền + /api
│   ├── .env.example                # mật khẩu DB, tên miền
│   └── backup/backup-db.sh
│
└── docs/
    ├── landingpage/                # bản thiết kế gốc của website + script so pixel
    └── luu-trinh-test-mau/         # ảnh tờ giấy gốc + script đối chiếu bản in
```

## 3. Quy ước để các bộ phận ghép vào nhau

- **Một module = một thư mục cùng tên** ở `backend/app/modules/` và
  `apps/portal/src/modules/`. Làm bộ phận mới thì copy khung module có sẵn và
  thêm tên vào danh sách (`MODULES` ở backend, `modules/index.js` ở portal) —
  không phải sửa router, sidebar hay module khác.
- **Backend**: mỗi module có `models.py`, `schemas.py`, `router.py` (gắn dưới
  `/api/v1/<module>`); nghiệp vụ ở `service.py`, module lớn tách thành
  `routers/` và `services/`.
- **Portal**: mỗi module có `routes.js` (route + mục menu), `api.js`, `pages/`,
  `components/`, và `index.js` khai báo `{ name, routes, menu, settingsSections }`.
  Sidebar và bảng Cài đặt tự dựng từ đó. Route đặt tên `<module>-<trang>`
  (`lab-customers`), đường dẫn `/<module>/<trang>`. Import dùng `@/` = `src/`.
- **Database**: một PostgreSQL, **mỗi module một schema** trùng tên. Dữ liệu cả
  công ty dùng chung (khách hàng, sản phẩm, thông tin công ty, tài liệu) chỉ có
  **một bản** ở schema `common`; module khác tham chiếu tới, không chép.
  `common` chỉ import `auth` (để kiểm quyền), không bao giờ trỏ sang module
  nghiệp vụ (lab, kho…) — chỗ nào cần
  (vd nạp lại danh mục sản phẩm phải nối lại bảng của lab) thì module kia đăng
  ký hook, nối trong `load_all_modules()`.
- **Quyền**: đặt tên `module.đối_tượng.hành_động`, mỗi module khai trong
  `<module>/permissions.py` (tự đồng bộ vào DB lúc khởi động). Backend chặn ở
  `router.py` của module — `guard("lab.equipment")`: GET cần `.view`, thêm/sửa/xoá
  cần `.edit`. Portal khai `meta.permission` trên route: menu, trang, nút
  Thêm/Sửa/Xoá (TableCard, DataTable, `useCanEdit()`) tự ẩn theo đó.

## 4. Các trang của cổng nội bộ

| Đường dẫn | Trang | Trước đây |
|---|---|---|
| `/lab/customers` | Khách hàng | `/customers` |
| `/lab/products` | Sản phẩm công ty | `/company-products` |
| `/lab/chemicals` | Hóa chất PTN + chất chỉ thị | `/lab-chemicals` |
| `/lab/equipment` | Thiết bị | `/equipment` |
| `/lab/formulations` | Đơn hàng HCTN (đơn pha chế) | `/chemical-orders` |
| `/lab/samples` | Lấy mẫu HC | `/chemical-sampling` |
| `/lab/analysis-reports` | Báo cáo phân tích | `/analysis-reports` |
| `/lab/documents` | Tài liệu (MSDS, COA, kỹ thuật, phương pháp, chứng nhận) | `/documents` |
| `/lab/work-log` | Nhật ký công tác | `/work-log` |
| `/lab/test-processes[/new \| /:id \| /:id/edit]` | Lưu trình test mẫu | `/test-processes…` |
| `/lab/process-templates` | Quy trình chuẩn | `/process-templates` |
| `/hr` | Nhân sự (hồ sơ, chấm công, nghỉ phép, hợp đồng, chứng chỉ, phòng ban) | Mới (Module HR) |
| `/accounting` | Kế toán (tổng quan, hoá đơn bán/mua, công nợ phải thu/trả, sổ quỹ, báo cáo) | Mới (Module Kế toán) |
| `/warehouse/stock` | Kho (tồn kho theo lô, phiếu nhập, phiếu xuất, kiểm kê, vị trí kho) | Mới (Module Kho) |
| `/delivery/board` | Điều phối xe (bảng điều phối Kanban, chuyến giao, quản lý xe, tài xế) | Mới (Module Điều phối) |
| `/system/settings` | Thông tin công ty (letterhead + liên hệ trên website) | `/company-profile` |

Chung: `/login`, `/verify-2fa`, `/forgot-password`, `/reset-password`, `/` (tổng
quan — lối tắt theo quyền), `/profile` (đổi mật khẩu, 2FA). Hệ thống:
`/system/users`, `/system/roles`, `/system/website` (đơn khách gửi, chọn mã lên
web), `/system/audit-log`.

API tương ứng: `/api/v1/common/{customers, products, company-profile, documents}`,
`/api/v1/lab/{chemicals, indicators, equipment, formulations, samples,
analysis-reports, work-logs, test-processes, process-templates}`,
`/api/v1/hr/{dashboard, departments, employees, attendance, leave-requests, contracts, certificates}`,
`/api/v1/accounting/{dashboard, invoices, vouchers, bank-accounts}`,
`/api/v1/warehouse/{dashboard, stock, receipts, dispatches, locations, audits}`,
`/api/v1/dispatch/{dashboard, trips, vehicles, drivers}`,
`/api/v1/website/...` (mục 8).

**Giao diện.** Sidebar + card bo tròn trên nền gradient mint/lavender, có chế
độ tối. Mỗi module là một nhóm trên thanh bên (lấy từ `menu` trong `routes.js`
của module). Mỗi trang nghiệp vụ là một `TableCard`: tiêu đề + nút ở trên, bảng
cuộn ở giữa, phân trang ở chân; màn hẹp đổi sang danh sách thẻ. Trang nào có
nhiều màn con khai báo `meta.nav` / `meta.navChild`, thanh bên tự tô sáng.

**Xuất dữ liệu.** Trang Hóa chất, Thiết bị: "Xuất Excel" theo tháng; Nhật ký
công tác: "Xuất PDF". **Cài đặt** (chân thanh bên) có phần giao diện chung và
phần của module lab (`LabDataSettings.vue`): xuất nhiều bảng ra một file Excel
hoặc PDF, sao lưu / khôi phục JSON. Mẫu sheet Excel ở
`modules/lab/utils/excelReport.js`, từng sheet ở `reportSheets.js`.

## 5. Database

| Schema | Bảng | Ghi chú |
|---|---|---|
| `common` | `customers`, `customer_fields`, `customer_field_products` | KH – lĩnh vực – mã SP dùng (tự map sang `company_products` nếu trùng mã, kể cả mã thành phần NCZ-49A → NCZ-49) |
| `common` | `company_products`, `company_product_modes` | danh mục 214 mã: tên Việt/Anh/Trung, nhóm, giai đoạn, vật liệu, công dụng; mỗi mã n chế độ sử dụng, mỗi chế độ một danh sách thông số (jsonb). `web_group` = nhóm trên website |
| `common` | `company_profile` | đúng 1 dòng — letterhead mọi phiếu in + liên hệ trên website |
| `common` | `documents` | file lưu thẳng trong DB (cột `content`); loại `certificate` hiện trên website |
| `lab` | `lab_chemicals`, `indicators` | tồn kho HC PTN (`box_count × volume_per_box`, "Lẻ" = `remaining_volume`), chất chỉ thị |
| `lab` | `equipment`, `equipment_variants` | 1 thiết bị n phân loại |
| `lab` | `chemical_orders` | đơn hàng HCTN — tự trừ/hoàn "Lẻ" của hóa chất, không cảnh báo, cho phép âm |
| `lab` | `chemical_sampling` | lấy mẫu HC → `common.company_products` |
| `lab` | `analysis_reports`, `analysis_completed_by`, `analysis_samples`, `analysis_components` | 1 báo cáo – n mẫu – n chỉ tiêu |
| `lab` | `work_logs` | nhật ký, `ot_hours` = giờ tăng ca |
| `lab` | `test_processes`, `test_process_steps`, `…_concentrations`, `…_chemicals`, `process_templates` | lưu trình test mẫu (mục 7) |
| `hr` | `departments`, `employees`, `attendance`, `leave_requests`, `contracts`, `certificates` | Quản lý nhân sự: hồ sơ nhân viên, chấm công hàng ngày, duyệt nghỉ phép, hợp đồng, chứng chỉ đào tạo, phòng ban |
| `accounting` | `bank_accounts`, `invoices`, `invoice_items`, `vouchers` | Quản lý kế toán: tài khoản ngân hàng / tiền mặt, hóa đơn bán / mua, chi tiết mặt hàng & hóa chất, phiếu thu / chi |
| `warehouse` | `locations`, `stock_items`, `receipts`, `receipt_items`, `dispatches`, `dispatch_items`, `audits` | Quản lý kho: vị trí lưu kho 3 kho 48 vị trí, tồn kho theo lô, phiếu nhập, phiếu xuất, soạn hàng FEFO, giao xe, kiểm kê |
| `dispatch` | `vehicles`, `drivers`, `delivery_trips` | Điều phối xe: quản lý đội xe tải hóa chất, tài xế, bảng điều phối Kanban 4 cột, phân công chuyến, trạng thái giao hàng |
| `website` | `contact_leads` | mỗi lượt khách gửi form "Nhận báo giá" |
| `auth` | `users`, `roles`, `permissions`, `user_roles`, `role_permissions`, `refresh_tokens`, `password_resets` | tài khoản, quyền, phiên (mục 9) |
| `system` | `audit_logs` | nhật ký thao tác |

**Alembic quản lý cấu trúc DB** — backend chạy `alembic upgrade head` trước khi
mở API (xem `backend/Dockerfile`), app không tự tạo/sửa bảng nữa.

- Đổi model xong: `alembic revision --autogenerate -m "mo ta"` trong container
  backend, **đọc lại file sinh ra**, rồi khởi động lại.
- Kiểm model và DB có khớp không: `alembic check` (phải ra "No new upgrade
  operations detected").
- Bản `0001_baseline` chuyển DB cũ (mọi bảng ở `public`) sang schema theo module
  bằng `ALTER TABLE … SET SCHEMA` — giữ nguyên dữ liệu, id, khoá ngoại — hoặc
  dựng mới toàn bộ nếu DB trống. Ngày 23/09/2026 đã chạy trên DB thật: 24/24
  bảng trùng số dòng trước/sau.
- Tên index không kèm schema (`ix_<bảng>_<cột>`, đặt trong `core/database.py`)
  để khớp index có sẵn từ trước.

Danh mục sản phẩm lấy từ file Excel tổng hợp. Sửa Excel xong thì dựng lại JSON
rồi nạp lại (ghi đè mã trùng, xoá mã không còn trong file, bảng đang trỏ tới mã
bị xoá được chuyển sang mã gốc; cột website không bị đụng tới):

```bash
python backend/app/modules/common/data/build_company_products.py "San pham cong ty.xlsx"   # cần openpyxl
docker compose -f infra/docker-compose.yml exec backend python -m app.modules.common.services.catalog
```

## 6. Dữ liệu mặc định

Chạy lúc backend khởi động, **idempotent** — chỉ điền ô còn trống, không ghi đè:

- `common/services/company_profile.py`: dòng thông tin công ty (letterhead +
  liên hệ website). Mã số thuế, email để `[ngoặc vuông]` chờ điền ở `/system/settings`.
- `website/seed.py`: chọn 18 mã lên web (6 mã/nhóm) — chỉ khi chưa mã nào được
  chọn — kèm tên tiếng Trung, mô tả tiếng Anh/Trung.

Chạy tay: dữ liệu mẫu lưu trình
`docker compose -f infra/docker-compose.yml exec backend python -m app.modules.lab.seed`.

## 7. Lưu trình test mẫu

Ghi lại một lần test mẫu cho khách — thông tin chung + danh sách bước (hạng mục,
thời gian, nhiệt độ, pH, nồng độ, hóa chất) — rồi in ra đúng tờ A4 mà phòng thí
nghiệm vẫn viết tay.

**Chỉ có một mẫu in.** `modules/lab/templates/test_process_sheet.html` dựng cả
HTML cho khung xem trước lẫn bản PDF (WeasyPrint đọc chính file đó), nên xem thế
nào in ra thế ấy. Font tờ in — Tinos cho chữ Việt, bản rút gọn Noto Serif TC cho
chữ Hán ở đầu trang — nằm trong `backend/app/static/fonts/`: xuất PDF thì
WeasyPrint đọc thẳng từ đĩa, khung xem trước tải qua `/api/v1/static` (đường dẫn
tương đối — iframe `srcdoc` lấy gốc URL của trang cha, cùng tên miền với API).

**Quy tắc chữ in** gom trong `modules/lab/services/test_process_format.py`: ghép
khoảng ("2-3 phút", "20-30°C"), bỏ số 0 thừa, chỉ số `_` / `^` (`HNO_3` → HNO₃,
`Zn^2+` → Zn²⁺). `modules/lab/utils/testProcessFormat.js` là bản sao phía trình
duyệt, chỉ dùng cho dữ liệu **chưa lưu**. Hai bên lệch nhau thì bản Python đúng.

**Bộ áo riêng.** Module dùng token màu `lt.*` (`tailwind.config.js`, cạnh
`brand.*`) và các lớp `.lt-*` ở cuối `core/style.css`. Font giao diện Be Vietnam
Pro để trong `apps/portal/public/fonts/`, không lấy từ CDN vì máy ở công ty có
thể không có mạng. Tờ A4 xem trước luôn nền sáng kể cả ở chế độ tối.

**Vài điểm cần biết**

- Mã `LT-YYYY-NNN` cấp trong `services/test_process_code.py`, có advisory lock
  để hai người bấm Lưu cùng lúc không trùng số.
- Xóa lưu trình là **xóa mềm** (`deleted_at`).
- Tên khách in trên phiếu lưu riêng khỏi `customers`: đổi tên khách không làm đổi
  phiếu đã phát hành, và nhận được cả khách chưa có trong danh mục.
- Ô cần in khác thường thì điền `time_text` / `temp_text` / `ph_text` — phiếu in
  nguyên văn ô đó.
- Đổi logo ở `/system/settings` ghi file mới vào `backend/app/static/img/`; deploy
  không mount thư mục backend thì phải gắn volume cho thư mục này.
- Đối chiếu tờ in với mẫu giấy: `docs/luu-trinh-test-mau/compare_sheet.py`.

## 8. Website công khai

App riêng `apps/landing` (Vue + Vite, không Tailwind), chỉ gọi phần công khai
`/api/v1/website/public/...` của backend.

### 8.1 Sơ đồ địa chỉ

Tiếng Việt không có tiền tố, hai thứ tiếng còn lại dưới `/en` và `/zh`. Đổi ngôn
ngữ thì giữ nguyên trang đang xem (`/san-pham/thu-dong` → `/en/products/passivation`).

| Trang | Tiếng Việt | English | 中文 |
|---|---|---|---|
| Trang chủ | `/` | `/en` | `/zh` |
| Giới thiệu | `/gioi-thieu` | `/en/about` | `/zh/about` |
| Sản phẩm (tất cả) | `/san-pham` | `/en/products` | `/zh/products` |
| Sản phẩm theo nhóm | `/san-pham/:nhom` | `/en/products/:group` | `/zh/products/:group` |
| Chi tiết sản phẩm | `/san-pham/:nhom/:ma` | `/en/products/:group/:code` | `/zh/products/:group/:code` |
| Giấy tờ & chứng nhận | `/chung-nhan` | `/en/certificates` | `/zh/certificates` |
| Tra cứu MSDS/TDS | `/tai-lieu` | `/en/documents` | `/zh/documents` |
| Dịch vụ | `/dich-vu` | `/en/services` | `/zh/services` |
| Liên hệ + bản đồ | `/lien-he` | `/en/contact` | `/zh/contact` |

Slug ba nhóm: `tien-xu-ly` / `phu-gia-ma` / `thu-dong` (vi) — `pretreatment` /
`plating-additives` / `passivation` (en, zh). Bảng đường dẫn nằm gọn trong
`apps/landing/src/routes.js`.

### 8.2 Dữ liệu — không có bảng nội dung riêng

| Trên website | Lấy từ | Sửa ở đâu (cổng nội bộ) |
|---|---|---|
| Sản phẩm | `common.company_products` có `web_group`; thông số từ `company_product_modes` | Sản phẩm công ty → Sửa → khối "Website công khai" |
| Link MSDS / TDS | file loại MSDS / Kỹ thuật trong `common.documents` có mã sản phẩm trong tên (vd `MSDS NCZ-48.pdf`); nhiều file thì lấy file mới nhất | Tài liệu → tải lên, đặt tên có mã |
| Giấy tờ, chứng nhận | `common.documents` loại `certificate`; chưa có file nào thì hiện 4 thẻ chờ như bản thiết kế | Tài liệu → tab "Chứng nhận" |
| Liên hệ, chân trang | `common.company_profile` | Thông tin công ty → khối "Website công khai" |
| Đơn khách gửi | `website.contact_leads` | `/system/website` |

```
GET  /api/v1/website/public/site          # công ty + sản phẩm lên web + chứng nhận, một lần gọi
GET  /api/v1/website/public/lookup/{ma}   # tra MSDS/TDS - tìm trên cả 214 mã
GET  /api/v1/website/public/files/{id}    # mở file - CHỈ loại MSDS, kỹ thuật, chứng nhận
POST /api/v1/website/public/contact-leads # form liên hệ
GET  /api/v1/website/contact-leads        # đơn khách gửi (nội bộ)
```

Mọi trường chữ trả **cả ba thứ tiếng cùng lúc** (`name.vi` / `.en` / `.zh`) để
đổi ngôn ngữ không phải gọi lại API. Thông số vận hành và vật liệu chỉ có tiếng
Việt (catalog chỉ có một thứ tiếng).

### 8.3 Giống hệt bản thiết kế — cách kiểm

Bản thiết kế gốc giữ ở `docs/landingpage/landingpage-goc.html` (thước đo duy
nhất, như `mau-goc.png` của tờ A4). Khối `<style>` của nó chép nguyên văn sang
`apps/landing/src/styles/site.css`; chỉ khác hai chỗ, có ghi chú tại chỗ: font
Be Vietnam Pro lấy từ `assets/fonts` thay vì Google Fonts, chữ Hán lấy font sẵn
trong máy (Microsoft YaHei / PingFang SC). Các trang con không có trong bản gốc
dùng lớp ở mục "Phần thêm" cuối file.

```bash
pip install playwright pillow && playwright install chromium   # lần đầu
python docs/landingpage/compare_landing.py
```

Kết quả 23/09/2026 — **0.00% điểm ảnh lệch, 46/46 phần tử trùng toạ độ** ở cả
ba khổ 1440 / 1024 / 390px. Script đồng bộ nội dung (DB), đoạn giới thiệu và
file font cho hai bản trước khi đo — không thì lệch giả ~0.5% dù bố cục đúng.

## 9. Đăng nhập, phân quyền, nhật ký

| Việc | Cách làm |
|---|---|
| Mật khẩu | bcrypt; tối thiểu 10 ký tự, có chữ và số |
| Phiên | cookie httpOnly (JS không đọc được): access 15 phút + refresh 7 ngày. Refresh **xoay vòng** — token cũ bị dùng lại thì thu hồi mọi phiên của người đó |
| Khoá tạm | sai mật khẩu 5 lần → khoá 15 phút; thông báo sai email và sai mật khẩu giống nhau |
| 2FA | TOTP (Google/Microsoft Authenticator) + 10 mã dự phòng dùng một lần; **bắt buộc** với vai trò có cờ `require_2fa` (mặc định: Admin cao nhất, Kế toán) — lần đăng nhập đầu phải cài xong mới vào |
| Quên mật khẩu | link hết hạn 30 phút, dùng 1 lần, gửi qua Resend (HTTPS — Railway chặn SMTP). Chưa đặt `RESEND_API_KEY` thì link in ra log backend. Admin cũng cấp được mật khẩu tạm ở `/system/users` |
| Mật khẩu tạm | tài khoản mới / admin cấp lại → bắt đổi ngay, trước đó mọi API trả 403 |
| Đổi / đặt lại mật khẩu, khoá tài khoản | mọi phiên cũ mất hiệu lực ngay (`token_version`) |
| Nhật ký | mọi thao tác thêm/sửa/xoá (ai, lúc nào, đường dẫn, IP) + đăng nhập, sai mật khẩu, 2FA… — không lưu nội dung gửi lên. Xem ở `/system/audit-log` |
| Admin cuối cùng | không khoá / gỡ quyền được tài khoản Admin cao nhất cuối cùng |

Vai trò mặc định (sửa ở `/system/roles`): Admin cao nhất (`*`), Kỹ thuật, Kho,
Điều phối, Tài xế, Kế toán, Nhân sự. Hiện chỉ Kỹ thuật và Hệ thống có trang thật;
các vai trò khác sẽ có quyền khi làm module tương ứng.

## 10. Triển khai: Vercel (2 app) + Railway (backend + Postgres)

**Railway** — service backend với thư mục gốc `backend/` (có sẵn `Dockerfile` và
`railway.json`, health check `/api/v1/health`), thêm Postgres của Railway.

| Biến môi trường | Giá trị |
|---|---|
| `DATABASE_URL` | lấy từ Postgres của Railway (dạng `postgres://` cũng được) |
| `JWT_SECRET` | chuỗi ngẫu nhiên dài: `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `COOKIE_SECURE` | `true` — khi đã bật mà thiếu `JWT_SECRET` thì backend từ chối khởi động |
| `PORTAL_URL` | `https://<tên-riêng>.daliang.com` — để ghép link đặt lại mật khẩu |
| `RESEND_API_KEY`, `MAIL_FROM` | tài khoản Resend, tên miền gửi đã xác thực |

Backend tự chạy `alembic upgrade head` mỗi lần khởi động. Sau lần deploy đầu:
mở **Shell** của service → `python -m app.modules.auth.create_admin`. Logo đổi ở
trang Thông tin công ty ghi vào `app/static/img/` — gắn Volume của Railway vào
thư mục này, không thì mất khi deploy lại.

**Vercel** — 2 project, Root Directory lần lượt `apps/portal` và `apps/landing`
(Vite, `npm run build`, output `dist`). Trong `vercel.json` của **cả hai** app,
thay `BACKEND-CUA-BAN.up.railway.app` bằng tên miền Railway của backend: Vercel
chuyển `/api/*` sang Railway nên trình duyệt thấy API cùng tên miền → cookie đăng
nhập chạy được, không cần CORS. Portal có sẵn header `X-Robots-Tag: noindex`.
Gắn tên miền: landing → `daliang.com`, portal → `<tên-riêng>.daliang.com`.

## 11. Lộ trình

1. ~~Sắp xếp theo cấu trúc mới, tách schema, Alembic~~ (23/09/2026)
2. ~~Core đăng nhập, phân quyền, 2FA, nhật ký thao tác, trang /system/*~~ (23/09/2026)
3. ~~Module Nhân sự (HR): hồ sơ, chấm công, nghỉ phép, hợp đồng, chứng chỉ, phòng ban~~ (28/09/2026)
4. ~~Module Kế toán (Accounting): tổng quan KPI, biểu đồ thu/chi 6 tháng, nhắc nợ, xuất Excel, phiếu thu/chi, hóa đơn~~ (28/09/2026)
5. ~~Module Kho (Warehouse): quản lý 3 kho 48 vị trí, tồn kho theo lô, phiếu nhập/xuất, soạn hàng FEFO, giao xe, kiểm kê, xuất Excel~~ (28/09/2026)
6. ~~Module Điều phối xe (Dispatch): bảng điều phối Kanban 4 cột, phân công chuyến, quản lý xe và tài xế~~ (28/09/2026)
7. Luồng đơn hàng: bảng `orders` chung (schema `common`) nối liền mạch form website → kỹ thuật → kho → điều phối / tài xế → kế toán.
