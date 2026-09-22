# Daliang VN — Quản lý phòng thí nghiệm hóa chất

Ứng dụng quản lý nội bộ cho: khách hàng, sản phẩm công ty, tồn kho hóa chất
phòng thí nghiệm, chất chỉ thị, thiết bị, đơn pha chế hóa chất thử nghiệm,
lấy mẫu, báo cáo phân tích, nhật ký công tác, tài liệu và lưu trình test mẫu
(phiếu A4 in cho khách — xem mục 6).

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

Chạy test của backend: `docker compose exec backend python -m pytest`.

## 2. Cấu trúc dự án

```
chemical-manager/
├── docker-compose.yml
├── .env.example
├── docs/
│   └── luu-trinh-test-mau/         # ảnh tờ giấy gốc + script đối chiếu bản in
├── backend/
│   ├── Dockerfile                  # libreoffice (xem trước Word) + weasyprint, font CJK (in PDF)
│   ├── pytest.ini / tests/         # test cho formatter và tờ in
│   ├── requirements.txt
│   └── app/
│       ├── main.py                 # khởi tạo FastAPI, tạo bảng, gắn router, mount /api/static
│       ├── models.py               # toàn bộ model SQLAlchemy (schema DB)
│       ├── schemas.py              # Pydantic schema (validate/response)
│       ├── core/
│       │   ├── config.py           # đọc biến môi trường
│       │   ├── database.py         # engine, session, Base
│       │   ├── migrations.py       # thêm cột mới cho bảng đã tồn tại
│       │   ├── product_catalog.py  # nạp danh mục SP công ty từ data/company_products.json
│       │   └── seed.py             # dữ liệu mẫu + letterhead mặc định
│       ├── data/                   # company_products.json (214 mã) + script đổi từ Excel
│       ├── templates/              # mẫu Jinja2 của tờ A4 (dùng chung cho web và PDF)
│       ├── static/                 # font của tờ in (Tinos, Noto Serif TC) + logo
│       ├── services/
│       │   ├── inventory.py        # trừ/hoàn tồn kho "Lẻ"
│       │   ├── test_process_format.py   # quy tắc chữ in (khoảng, đơn vị, chỉ số _ ^)
│       │   ├── test_process_sheet.py    # dựng dữ liệu cho tờ phiếu + xuất PDF
│       │   └── test_process_code.py     # cấp mã LT-YYYY-NNN
│       └── api/                    # 1 file router / 1 nhóm chức năng
│           ├── common.py           # get_or_404 + apply_payload dùng chung
│           ├── customers.py, company_products.py, lab_chemicals.py,
│           ├── indicators.py, equipment.py, chemical_orders.py,
│           ├── chemical_sampling.py, analysis_reports.py, work_logs.py, documents.py
│           └── test_processes.py, process_templates.py, company_profile.py
└── frontend/
    ├── Dockerfile
    ├── public/fonts/               # Be Vietnam Pro (giao diện Lưu trình test mẫu)
    ├── tailwind.config.js / vite.config.js
    └── src/
        ├── main.js / App.vue / router/index.js
        ├── api/                    # client axios + khai báo endpoint
        ├── composables/
        │   ├── useCrudResource.js  # rows + modal + form + load/save/remove
        │   ├── useSearchedRows.js  # lọc theo ô tìm kiếm trên Topbar
        │   └── useStepEditorLookups.js  # 3 danh mục mà trình soạn bước cần
        ├── constants/              # giá trị dùng chung (công đoạn mạ, trạng thái lưu trình...)
        ├── components/
        │   ├── TableCard.vue       # khung card chung của mọi bảng
        │   ├── DataTable.vue       # bảng dữ liệu + lọc/sắp xếp/phân trang
        │   ├── TablePagination.vue, Modal.vue, DynamicForm.vue,
        │   ├── FormActions.vue, MonthPicker.vue, ToolbarButton.vue
        │   ├── layout/             # Sidebar, Topbar, AppLayout, SettingsPanel, MenuButton
        │   ├── analysis-reports/, documents/
        │   └── test-processes/     # thẻ danh sách, khung tờ in, trình soạn bước, hộp thoại
        ├── utils/                  # format, chemFormula, excelReport, reportSheets, pdfReport...
        └── views/                  # 1 view / 1 trang nghiệp vụ
```

## 3. Schema database (PostgreSQL)

| Bảng | Tương ứng ghi chú tay | Ghi chú |
|---|---|---|
| `customers` | Bảng 1 – KH | |
| `customer_fields` | (lĩnh vực của KH) | 1 KH – n lĩnh vực |
| `customer_field_products` | (SP dùng theo lĩnh vực) | tự map sang `company_products` nếu trùng mã |
| `company_products` / `company_product_modes` | Bảng 2 – SP Cty | mã, tên Việt/Anh, nhóm phân loại, giai đoạn, vật liệu, công dụng; mỗi mã có n chế độ sử dụng, mỗi chế độ một danh sách thông số (jsonb, mỗi phần tử một dòng "Nhiệt độ: 50-75°C"). Danh mục gốc: `app/data/company_products.json` |
| `lab_chemicals` | Bảng 3 – HC PTN | `box_count` × `volume_per_box` = `total_volume`; `remaining_volume` là phần "Lẻ" đang dùng |
| `indicators` | Chất chỉ thị | |
| `equipment` / `equipment_variants` | Bảng 4 – Thiết bị | 1 thiết bị có nhiều phân loại |
| `chemical_orders` | Bảng 5 – Đơn hàng HCTN | FK tới `lab_chemicals` và `customers` |
| `chemical_sampling` | Bảng 6 – Lấy mẫu HC | FK tới `company_products` |
| `analysis_reports` / `analysis_samples` / `analysis_components` | Báo cáo phân tích | 1 báo cáo – n mẫu – n chỉ tiêu |
| `work_logs` | Nhật ký công tác | `log_date`, `content`, `ot_hours` (số giờ tăng ca) |
| `documents` | Tài liệu | file lưu thẳng trong DB (cột `content`) |
| `test_processes` | Lưu trình test mẫu | mã `LT-YYYY-NNN`; `test_month` luôn là ngày 01; xóa mềm bằng `deleted_at` |
| `test_process_steps` | (các bước của 1 lưu trình) | 1 bước = 1 hàng của bảng trên phiếu; `position` cũng là số thứ tự in ra |
| `test_process_step_concentrations` | (ô NỒNG ĐỘ) | 0..n dòng mỗi bước, độc lập với danh sách hóa chất |
| `test_process_step_chemicals` | (ô HÓA CHẤT) | trỏ tới `company_products` **hoặc** `lab_chemicals`, hoặc chỉ là chữ tự do |
| `process_templates` | Quy trình chuẩn | bộ bước dùng lại, lưu thẳng dạng `jsonb` |
| `company_profile` | Thông tin công ty | đúng 1 dòng — letterhead in trên mọi phiếu |

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

Thanh bên chia 2 nhóm: **Dữ liệu** (danh mục tra cứu) và **Nghiệp vụ** (việc làm
hằng ngày). Trang nào có nhiều màn con thì khai báo `meta.nav` / `meta.navChild`
trong router, thanh bên tự tô sáng theo đó — không giữ thêm danh sách tên route.

Riêng Lưu trình test mẫu có bộ áo riêng, xem mục 6.

## 5. Xuất dữ liệu

- Trang **Hóa chất** và **Thiết bị**: nút "Xuất Excel" theo tháng đang chọn.
- Trang **Nhật ký công tác**: nút "Xuất PDF".
- **Cài đặt → Xuất dữ liệu**: chọn nhiều bảng, xuất 1 file Excel nhiều sheet
  hoặc 1 file PDF; kèm chức năng sao lưu / khôi phục JSON.

Mẫu sheet Excel (logo, tên công ty, header xanh, viền, Times New Roman) nằm ở
`utils/excelReport.js`; từng sheet nghiệp vụ ở `utils/reportSheets.js` và được
dùng chung cho cả nút xuất ở trang lẫn phần xuất trong Cài đặt.

## 6. Lưu trình test mẫu

Ghi lại một lần test mẫu cho khách — thông tin chung + danh sách bước (hạng mục,
thời gian, nhiệt độ, pH, nồng độ, hóa chất) — rồi in ra đúng tờ A4 mà phòng thí
nghiệm vẫn viết tay.

**Chỉ có một mẫu in.** `app/templates/test_process_sheet.html` dựng cả HTML cho
khung xem trước trên web lẫn bản PDF (WeasyPrint đọc chính file đó), nên xem thế
nào in ra thế ấy. Font của tờ in — Tinos cho chữ Việt, bản rút gọn Noto Serif TC
cho phần chữ Hán ở đầu trang — nằm trong `app/static/fonts/` vì khi xuất PDF
WeasyPrint đọc thẳng từ đĩa; thư mục đó cũng được mount ở `/api/static` để khung
xem trước tải được cùng bộ font.

**Quy tắc chữ in** gom trong `services/test_process_format.py`: ghép khoảng
("2-3 phút", "20-30°C"), bỏ số 0 thừa, và cú pháp đánh dấu chỉ số `_` / `^`
(`HNO_3` → HNO₃, `Zn^2+` → Zn²⁺). `utils/testProcessFormat.js` là bản sao phía
trình duyệt, chỉ dùng cho dữ liệu **chưa lưu** (dòng tóm tắt của bước đang thu
gọn, gợi ý "in ra:" cạnh ô nồng độ). Hai bên lệch nhau thì bản Python là bản đúng.

**Các màn hình:**

| Trang | Việc |
|---|---|
| `/test-processes` | danh sách + tờ in của lưu trình đang chọn; lọc theo trạng thái, khách, tháng, hóa chất |
| `/test-processes/new`, `/test-processes/:id/edit` | form nhập, khung xem trước dựng lại khi ngừng gõ |
| `/process-templates` | quy trình chuẩn — bộ bước dùng lại khi tạo lưu trình mới |
| `/company-profile` | thông tin công ty in ở đầu mọi phiếu |

Trên điện thoại, trang chi tiết có thêm chế độ **Từng bước** cho dễ đọc hơn tờ A4
thu nhỏ.

**Bộ áo riêng.** Module dùng token màu `lt.*` (khai trong `tailwind.config.js`,
cạnh `brand.*`) và các lớp `.lt-*` ở cuối `style.css`; chín trang cũ giữ nguyên
`brand.*`. Font giao diện Be Vietnam Pro để trong `frontend/public/fonts/` chứ
không lấy từ CDN, vì máy ở công ty có thể không có mạng. Các trang này tự dựng
đầu trang nên `meta.hideTopbar` tắt Topbar chung, và có `MenuButton` riêng để mở
thanh bên trên màn hẹp. Tờ A4 xem trước luôn nền sáng, kể cả khi app ở chế độ tối
— vì nó là tờ giấy in.

**Vài điểm khác cần biết**

- Mã `LT-YYYY-NNN` cấp trong `services/test_process_code.py`, có advisory lock để
  hai người bấm Lưu cùng lúc không ra trùng số.
- Xóa lưu trình là **xóa mềm** (`deleted_at`), bản ghi vẫn còn trong DB.
- Tên khách in trên phiếu lưu riêng khỏi bảng `customers`: đổi tên khách trong
  danh mục không làm đổi phiếu đã phát hành, và nhận được cả khách chưa có trong
  danh mục.
- Ô nào cần in khác thường thì điền `time_text` / `temp_text` / `ph_text` —
  phiếu in nguyên văn ô đó, bỏ qua các ô số.
- Đổi logo ở trang Thông tin công ty sẽ ghi file mới vào `app/static/img/`; deploy
  kiểu không mount volume thì nhớ gắn volume cho thư mục này, không thì logo mất
  mỗi lần dựng lại image.

## 7. Giả định thiết kế đã áp dụng

1. Trừ tồn kho "Lẻ" tự động, **không** có cơ chế cảnh báo hết hàng.
2. **Chưa** có đăng nhập/phân quyền — ứng dụng dùng nội bộ, mở tự do.
3. Khách hàng: nhập lĩnh vực + danh sách mã SP dùng dạng text (cách nhau bởi
   dấu phẩy); hệ thống tự dò và liên kết (FK) tới `company_products` nếu mã
   trùng khớp — hoặc là thành phần của một mã (NCZ-49A → NCZ-49) — không
   trùng thì lưu dạng text tự do.
4. Danh mục SP công ty lấy từ file Excel tổng hợp. Sửa Excel xong thì dựng lại
   JSON rồi nạp lại (ghi đè mã trùng, xoá mã không còn trong file, các bảng
   đang trỏ tới mã bị xoá được chuyển sang mã gốc):
   ```bash
   python backend/app/data/build_company_products.py "San pham cong ty.xlsx"   # cần openpyxl
   docker compose exec backend python -m app.core.product_catalog
   ```
   Database còn kiểu SP cũ thì lần khởi động đầu tiên backend tự làm việc này.

## 8. Hướng mở rộng (chưa làm)

- Trang Dashboard tổng quan (tồn kho thấp, đơn hàng gần đây…).
- Phân quyền người dùng, cảnh báo tồn kho thấp.
