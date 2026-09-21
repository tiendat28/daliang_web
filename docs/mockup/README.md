# Mockup giao diện — module Lưu trình test mẫu

Đây là bản thiết kế đã chốt, xuất thành HTML tĩnh. Mở bất kỳ file `.html` nào bằng
trình duyệt là thấy đúng màn hình đó (cần mạng để tải font Google Fonts).

Dùng kèm `PROMPT-luu-trinh-test-mau.md`: file prompt nói *làm gì*, thư mục này cho thấy
*trông ra sao*. Khi hai bên lệch nhau, mã trong thư mục này là đúng.

## Các màn hình

| File | Màn hình | Kích thước dựng |
|---|---|---|
| `Main.html` | Danh sách + chi tiết (màn hình chính) | 1440 × 980 |
| `Form.html` | Form nhập / sửa, có khung xem trước | 1440 × 1060 |
| `Templates.html` | Quy trình chuẩn | 1440 × 860 |
| `Dialog.html` | Hộp thoại "Chèn từ quy trình chuẩn" | 620 × 544 |
| `Letterhead.html` | Cài đặt thông tin công ty | 1000 × 660 |
| `MobileList.html` | Điện thoại — danh sách | 390 × 844 |
| `MobileDetail.html` | Điện thoại — chi tiết, chế độ Từng bước | 390 × 844 |
| `Sheet.html` | Tờ in A4 | 794 × 1123 |

Ảnh chụp từng màn hình nằm trong `anh/`.

## Cách đọc mockup

- Mọi kiểu dáng viết inline trong thẻ, không có class. Đọc thẳng giá trị từ thuộc tính
  `style` là ra màu, cỡ chữ, khoảng cách, bo góc, đổ bóng.
- Bảng giá trị gom lại thành token nằm ở mục 6.0 của file prompt. Khi dựng code, khai báo
  token trước rồi dùng token, đừng chép mã hex vào từng component.
- Mockup dựng ở bề rộng cố định để đối chiếu. Khi code thì để layout co giãn: sidebar giữ
  232px, cột danh sách giữ 372px, phần còn lại `flex: 1`.
- Dữ liệu trong mockup là dữ liệu mẫu. Lưu trình LT-2026-012 đúng bằng tờ giấy gốc; các
  lưu trình còn lại chỉ để xem danh sách cho thật.

## Tờ in A4 (`Sheet.html`)

Dựng theo số đo lấy từ ảnh tờ giấy gốc, ở 96 dpi:

- Trang 794 × 1123 px (A4), lề trên 49, dưới 57, trái 79, phải 57.
- Bảng rộng 658 px, 7 cột: 43 / 104 / 100 / 99 / 64 / 132 / 116.
- Mép trên bảng cách đỉnh trang 363 px, mép dưới 889 px.
- Hàng tiêu đề và hàng thường cao 44 px, hàng có nhiều hóa chất tự giãn.
- Ô bảng phải đặt `box-sizing: border-box`, nếu không padding sẽ đội bề rộng bảng lên.
- Thẻ `<sub>` cần `line-height: 0`, nếu không ô rỗng vẫn làm cao hàng.
- Khối chữ ký căn giữa tại 533 px tính từ mép trái trang.

Khi dựng PDF bằng WeasyPrint, in `Sheet.html` ra rồi đặt cạnh `mau-goc.png` để so.

## Font

- Giao diện: Be Vietnam Pro (400 / 500 / 600 / 700).
- Tờ in: Tinos cho chữ Việt, Noto Serif TC cho chữ Trung.

Cả ba đều có trên Google Fonts. Nếu app cần chạy khi không có mạng thì tải file font vào
repo và khai báo `@font-face` thay vì dùng CDN.
