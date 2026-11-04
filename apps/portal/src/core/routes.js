/* Route cua phan dung chung: dang nhap (meta.public, khung AuthLayout), trang
 * tong quan va trang tai khoan cua toi. */
const auth = name => () => import(`./auth/pages/${name}.vue`)
const PUBLIC = { public: true, layout: 'auth' }

export const coreRoutes = [
  { path: '/login', name: 'login', component: auth('LoginPage'), meta: { ...PUBLIC, title: 'Đăng nhập' } },
  { path: '/verify-2fa', name: 'verify-2fa', component: auth('TwoFactorPage'), meta: { ...PUBLIC, title: 'Xác thực 2 bước' } },
  { path: '/forgot-password', name: 'forgot-password', component: auth('ForgotPasswordPage'), meta: { ...PUBLIC, title: 'Quên mật khẩu' } },
  { path: '/reset-password', name: 'reset-password', component: auth('ResetPasswordPage'), meta: { ...PUBLIC, title: 'Đặt mật khẩu mới' } },
    { path: '/', name: 'home', component: () => import('./pages/HomePage.vue'), meta: { title: 'Trang chủ' } },
  { path: '/profile', name: 'profile', component: () => import('./pages/ProfilePage.vue'), meta: { title: 'Tài khoản của tôi' } },
]
