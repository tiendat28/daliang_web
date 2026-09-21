# Font cho tờ in

`Tinos` (Apache 2.0 / OFL, Google Fonts — https://fonts.google.com/specimen/Tinos)
cùng số đo với Times New Roman nhưng có đủ dấu tiếng Việt, nên tờ in dùng font
này thay vì Times để chữ không bị nhảy dòng so với mẫu giấy.

Font để thẳng trong repo (không dùng CDN) vì WeasyPrint chạy trong container
backend, không ra được internet khi build ở máy khách.

Chữ Trung phồn thể dùng `Noto Serif CJK TC`, cài bằng gói `fonts-noto-cjk`
trong `backend/Dockerfile` — không cần chép file vào đây.
