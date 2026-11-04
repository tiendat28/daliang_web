/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eefcfa',
          100: '#d3f7f1',
          200: '#a8efe4',
          300: '#71e0d2',
          400: '#3fc8bc',
          500: '#22ada3',
          600: '#178b85',
          700: '#166f6c',
          800: '#165957',
          900: '#154a49',
        },
        // Bộ token riêng của module "Lưu trình test mẫu", lấy thẳng từ docs/mockup.
        // Chỉ dùng trong module này — 9 trang cũ vẫn dùng brand.* như trước.
        lt: {
          ink: '#0D2A2D',        // chữ chính
          body: '#3E5A5C',       // chữ trên nút phụ
          label: '#47605F',      // nhãn ô nhập
          muted: '#64797D',      // chữ phụ
          faint: '#7C9196',      // chữ mờ (dòng meta)
          hint: '#9AACAE',       // dấu gạch nối giữa 2 ô số

          line: '#E4EEEB',       // viền ô nhập, nút
          divider: '#EEF4F3',    // vạch ngăn trong thẻ
          rule: '#F1F6F5',       // vạch ngăn giữa các dòng danh sách
          edge: '#E9F0EE',       // vạch dọc trên thanh công cụ
          soft: '#EBF2F0',       // viền dòng bước đang thu gọn

          teal: '#17BFA8',       // đầu gradient
          teal2: '#0D8FA0',      // cuối gradient
          tealink: '#0B7C8C',    // chữ/nút chữ màu teal
          tealdark: '#0A7382',   // trạng thái hover của link

          wash: '#ECF9F6',       // nền nút phụ màu teal
          sel: '#F4FBF9',        // nền dòng danh sách đang chọn
          selline: '#A6DDD4',    // viền thẻ đang chọn trong hộp thoại
          focus: '#CFE9E4',      // viền bước đang mở

          paper: '#F2F6F6',      // nền sau tờ A4
          card: '#FBFDFC',       // nền dòng bước thu gọn
          tint: '#F6F9F8',       // nền chip tên bước

          chip: '#F1F7F5',       // nền chip hóa chất
          chipline: '#E1EDE9',
          chipink: '#2C5B55',
          step: '#EEF4F3',       // nền số thứ tự bước

          done: '#DFF3E7', doneink: '#10693C',       // Hoàn thành
          run: '#E4EEFE', runink: '#1D4ED8',         // Đang test
          draft: '#EEF1F4', draftink: '#47565E',     // Nháp
          void: '#FDE9E9', voidink: '#B42318',       // Đã hủy
        },
        // Khung chung cua cong noi bo (sidebar, thanh tren, dang nhap, quan tri) - lay tu
        // ban thiet ke Admin.dc.html / Login.dc.html, cung bo mau voi website cong khai.
        dl: {
          dark: '#0b3336',       // nen khoi toi (trang dang nhap)
          ink: '#0f172a',        // chu chinh
          body: '#334155',       // chu thuong
          muted: '#5b6b7f',      // chu phu
          faint: '#8795a8',      // nhan nhom tren sidebar
          line: '#e2e8f0',       // vien o nhap, nut vien
          rule: '#eef2f6',       // vach giua cac dong bang
          field: '#cfdcdc',      // vien o nhap trang dang nhap
          teal: '#0b7d72',
          tealdark: '#085e56',
          mint: '#5eead4',
          soft: '#d3f4ee',       // nen avatar / icon nhat
          softink: '#0f5f56',
          wash: '#e9f6f3',       // nen muc con dang chon
          note: '#eef7f5',       // nen hop ghi chu
          panel: '#f4f8f8',      // nen the nguoi dung
          chip: '#f1f5f9',
          check: '#c3cfd9',      // vien o tick chua chon
          // the so lieu / nhan trang thai
          ok: '#e3f5ea', okink: '#166534',
          warn: '#fdf0cf', warnink: '#8a4b08',
          bad: '#fde4e4', badink: '#9b1c1c', badline: '#f5c2c2',
          info: '#e0f0fb', infoink: '#0b5a85',
          violet: '#ece8fb', violetink: '#5b3fb0',
          grey: '#eef2f6', greyink: '#475569',
        },
      },
      fontFamily: {
        lt: ['Be Vietnam Pro', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      // Tên bóng đổ không được trùng tên màu trong lt.* ở trên: gặp
      // shadow-lt-card, Tailwind hiểu luôn là "đổ bóng màu lt.card" và ghi đè
      // màu của bóng, nên thẻ hóa ra viền sáng trắng khi xem ở nền tối.
      boxShadow: {
        'dl-card': '0 1px 2px rgba(15,23,42,.04), 0 8px 24px rgba(15,23,42,.05)',
        'dl-nav': '0 8px 24px rgba(15,23,42,.05)',
        'dl-active': '0 6px 16px rgba(11,125,114,.25)',
        'lt-panel': '0 1px 2px rgba(13,42,45,.04), 0 14px 34px -18px rgba(13,42,45,.18)',
        'lt-raise': '0 1px 2px rgba(13,42,45,.04), 0 10px 26px -16px rgba(13,42,45,.22)',
        'lt-sheet': '0 2px 6px rgba(13,42,45,.10), 0 20px 44px -18px rgba(13,42,45,.32)',
        'lt-accent': '0 8px 18px -8px rgba(13,143,160,.8)',
        'lt-fab': '0 12px 26px -10px rgba(13,143,160,.85)',
        'lt-dialog': '0 24px 60px -20px rgba(13,42,45,.42)',
      },
      backgroundImage: {
        'dl-grad': 'linear-gradient(135deg, #0b7d72, #0e6f8a)',
        'dl-page': 'linear-gradient(135deg, #e4f5ef 0%, #eef1fb 55%, #f2ecfb 100%)',
        'app-gradient': 'linear-gradient(135deg, #eafaf6 0%, #eef3fb 50%, #f1eefb 100%)',
        'brand-gradient': 'linear-gradient(135deg, #166f6c 0%, #22ada3 100%)',
        'lt-gradient': 'linear-gradient(135deg, #17BFA8 0%, #0D8FA0 100%)',
      },
    },
  },
  plugins: [],
}
