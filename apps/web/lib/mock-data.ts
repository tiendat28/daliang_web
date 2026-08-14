// Du lieu gia (mock) cho giao dien - chua noi database.

export type FileKind = "pdf" | "doc" | "xls";
export type DocStatus = "draft" | "pending" | "approved";
export type Visibility = "internal" | "public";

export type Doc = {
  id: string;
  code: string;
  title: string;
  kind: FileKind;
  version: number;
  updatedAt: string;
  uploadedBy: string;
  status: DocStatus;
  visibility: Visibility;
  folder: string;
  sizeLabel: string;
  pageCount: number;
  snippet?: string;
};

export const docs: Doc[] = [
  {
    id: "1",
    code: "QT-KT-014",
    title: "Quy trình kiểm tra chất lượng đầu vào",
    kind: "pdf",
    version: 3,
    updatedAt: "04/08/2026",
    uploadedBy: "Nguyễn Văn A",
    status: "approved",
    visibility: "public",
    folder: "Kỹ thuật / Quy trình",
    sizeLabel: "4,2 MB",
    pageCount: 12,
    snippet: "...toàn bộ nguyên vật liệu phải được <mark>kiểm tra chất lượng đầu vào</mark> trước khi nhập kho...",
  },
  {
    id: "2",
    code: "BC-VT-0726",
    title: "Bảng theo dõi vật tư tháng 07",
    kind: "xls",
    version: 1,
    updatedAt: "31/07/2026",
    uploadedBy: "Trần Thị B",
    status: "approved",
    visibility: "internal",
    folder: "Kế toán",
    sizeLabel: "1,1 MB",
    pageCount: 3,
  },
  {
    id: "3",
    code: "HĐ-2026-118",
    title: "Hợp đồng nguyên tắc — Công ty Minh Long",
    kind: "doc",
    version: 2,
    updatedAt: "28/07/2026",
    uploadedBy: "Lê Văn C",
    status: "pending",
    visibility: "internal",
    folder: "Kinh doanh / Hợp đồng",
    sizeLabel: "860 KB",
    pageCount: 6,
  },
  {
    id: "4",
    code: "CN-HC-009",
    title: "Chứng nhận hiệu chuẩn thiết bị đo",
    kind: "pdf",
    version: 1,
    updatedAt: "22/07/2026",
    uploadedBy: "Nguyễn Văn A",
    status: "approved",
    visibility: "internal",
    folder: "Kỹ thuật / Báo cáo thử nghiệm",
    sizeLabel: "2,4 MB",
    pageCount: 4,
  },
  {
    id: "5",
    code: "DM-NCC-03",
    title: "Danh mục nhà cung cấp đã đánh giá",
    kind: "xls",
    version: 6,
    updatedAt: "15/07/2026",
    uploadedBy: "Phạm Thị D",
    status: "approved",
    visibility: "internal",
    folder: "Kinh doanh",
    sizeLabel: "3,0 MB",
    pageCount: 2,
    snippet: "...danh sách nhà cung cấp đạt yêu cầu sau vòng <mark>đánh giá</mark> quý II năm 2026...",
  },
  {
    id: "6",
    code: "CS-BH-2026",
    title: "Chính sách bảo hành sản phẩm 2026",
    kind: "doc",
    version: 1,
    updatedAt: "21/07/2026",
    uploadedBy: "Lê Văn C",
    status: "approved",
    visibility: "public",
    folder: "Kinh doanh",
    sizeLabel: "540 KB",
    pageCount: 5,
  },
  {
    id: "7",
    code: "BM-NCC-02",
    title: "Biểu mẫu đăng ký nhà cung cấp",
    kind: "xls",
    version: 4,
    updatedAt: "15/07/2026",
    uploadedBy: "Phạm Thị D",
    status: "approved",
    visibility: "public",
    folder: "Kinh doanh",
    sizeLabel: "220 KB",
    pageCount: 1,
  },
  {
    id: "8",
    code: "BV-KT-021",
    title: "Bản vẽ kỹ thuật khuôn ép nhựa số 021",
    kind: "pdf",
    version: 2,
    updatedAt: "18/07/2026",
    uploadedBy: "Nguyễn Văn A",
    status: "approved",
    visibility: "internal",
    folder: "Kỹ thuật / Bản vẽ",
    sizeLabel: "6,8 MB",
    pageCount: 3,
  },
  {
    id: "9",
    code: "TN-KT-005",
    title: "Báo cáo thử nghiệm độ bền vật liệu",
    kind: "pdf",
    version: 1,
    updatedAt: "12/07/2026",
    uploadedBy: "Đặng Thị E",
    status: "approved",
    visibility: "internal",
    folder: "Kỹ thuật / Báo cáo thử nghiệm",
    sizeLabel: "5,1 MB",
    pageCount: 9,
    snippet: "...kết quả cho thấy vật liệu đạt <mark>độ bền kéo</mark> tối thiểu theo tiêu chuẩn TCVN...",
  },
  {
    id: "10",
    code: "BG-KD-0714",
    title: "Báo giá cung cấp thiết bị quý III",
    kind: "doc",
    version: 1,
    updatedAt: "14/07/2026",
    uploadedBy: "Trần Thị B",
    status: "pending",
    visibility: "internal",
    folder: "Kinh doanh / Báo giá",
    sizeLabel: "410 KB",
    pageCount: 2,
  },
  {
    id: "11",
    code: "QĐ-NS-045",
    title: "Quyết định bổ nhiệm nhân sự phòng Kỹ thuật",
    kind: "doc",
    version: 1,
    updatedAt: "08/07/2026",
    uploadedBy: "Phạm Thị D",
    status: "approved",
    visibility: "internal",
    folder: "Nhân sự",
    sizeLabel: "180 KB",
    pageCount: 1,
  },
  {
    id: "12",
    code: "BCTC-Q2-2026",
    title: "Báo cáo tài chính quý II năm 2026",
    kind: "xls",
    version: 1,
    updatedAt: "05/07/2026",
    uploadedBy: "Lê Văn C",
    status: "draft",
    visibility: "internal",
    folder: "Kế toán",
    sizeLabel: "2,9 MB",
    pageCount: 7,
  },
];

export type FolderNode = {
  name: string;
  children?: FolderNode[];
};

export const folderTree: FolderNode[] = [
  {
    name: "Kỹ thuật",
    children: [
      { name: "Bản vẽ" },
      { name: "Quy trình" },
      { name: "Báo cáo thử nghiệm" },
    ],
  },
  {
    name: "Kinh doanh",
    children: [{ name: "Hợp đồng" }, { name: "Báo giá" }],
  },
  { name: "Nhân sự" },
  { name: "Kế toán" },
];

export type Shortcut = {
  label: string;
  badge?: number;
};

export const shortcuts: Shortcut[] = [
  { label: "Tất cả tài liệu" },
  { label: "Tài liệu của tôi" },
  { label: "Chờ duyệt", badge: 3 },
  { label: "Đã công khai" },
  { label: "Thùng rác" },
];

export type ActivityAction = "đã xem" | "đã tải về" | "đã duyệt" | "đã tải lên";

export type ActivityLog = {
  id: string;
  actor: string;
  action: ActivityAction;
  target: string;
  time: string;
};

export const activityLogs: ActivityLog[] = [
  {
    id: "1",
    actor: "Nguyễn Văn A",
    action: "đã duyệt",
    target: "QT-KT-014 · Quy trình kiểm tra chất lượng đầu vào",
    time: "10:24",
  },
  {
    id: "2",
    actor: "Trần Thị B",
    action: "đã tải lên",
    target: "BC-VT-0726 · Bảng theo dõi vật tư tháng 07",
    time: "09:47",
  },
  {
    id: "3",
    actor: "Khách (117.2.•.•)",
    action: "đã xem",
    target: "CS-BH-2026 · Chính sách bảo hành sản phẩm 2026",
    time: "09:12",
  },
  {
    id: "4",
    actor: "Lê Văn C",
    action: "đã tải về",
    target: "DM-NCC-03 · Danh mục nhà cung cấp đã đánh giá",
    time: "04/08",
  },
  {
    id: "5",
    actor: "Phạm Thị D",
    action: "đã tải lên",
    target: "BM-NCC-02 · Biểu mẫu đăng ký nhà cung cấp",
    time: "04/08",
  },
  {
    id: "6",
    actor: "Đặng Thị E",
    action: "đã xem",
    target: "TN-KT-005 · Báo cáo thử nghiệm độ bền vật liệu",
    time: "03/08",
  },
];

export type PermissionRow = {
  id: string;
  subject: string;
  description: string;
  canView: boolean;
  canDownload: boolean;
  canEdit: boolean;
  canManage: boolean;
};

export const permissionRows: PermissionRow[] = [
  {
    id: "1",
    subject: "Quản trị viên",
    description: "2 người",
    canView: true,
    canDownload: true,
    canEdit: true,
    canManage: true,
  },
  {
    id: "2",
    subject: "Trưởng phòng",
    description: "6 người",
    canView: true,
    canDownload: true,
    canEdit: true,
    canManage: false,
  },
  {
    id: "3",
    subject: "Nhân viên",
    description: "34 người",
    canView: true,
    canDownload: true,
    canEdit: false,
    canManage: false,
  },
  {
    id: "4",
    subject: "Khách / Đối tác",
    description: "Không giới hạn",
    canView: true,
    canDownload: false,
    canEdit: false,
    canManage: false,
  },
];
