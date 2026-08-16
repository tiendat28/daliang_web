"use server";

import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { prisma } from "@daliang/db";
import { auth } from "@/auth";
import { canApproveDocumentsForDepartment } from "@/lib/dlvc/permissions";
import { saveUploadedFile } from "@/lib/dlvc/storage";

export type DocumentFormState = { error?: string } | undefined;

export async function uploadDocument(_prevState: DocumentFormState, formData: FormData): Promise<DocumentFormState> {
  const session = await auth();
  const employeeId = session?.user?.employeeId;
  if (!employeeId) {
    return { error: "Tài khoản của bạn chưa gắn với hồ sơ nhân viên nên không thể tải tài liệu." };
  }

  const title = String(formData.get("title") ?? "").trim();
  const departmentIdRaw = String(formData.get("departmentId") ?? "");
  const documentTypeIdRaw = String(formData.get("documentTypeId") ?? "");
  const expiryDateRaw = String(formData.get("expiryDate") ?? "");
  const notes = String(formData.get("notes") ?? "").trim();
  const file = formData.get("file");

  if (!title) return { error: "Vui lòng nhập tên tài liệu." };
  if (!departmentIdRaw) return { error: "Vui lòng chọn phòng ban." };
  if (!(file instanceof File) || file.size === 0) return { error: "Vui lòng chọn tệp cần tải lên." };

  const { filePath, fileFormat, fileSizeKb } = await saveUploadedFile(file);

  const document = await prisma.adminDocument.create({
    data: {
      title,
      departmentId: Number(departmentIdRaw),
      documentTypeId: documentTypeIdRaw ? Number(documentTypeIdRaw) : null,
      filePath,
      fileFormat,
      fileSizeKb,
      uploadedBy: employeeId,
      status: "pending",
      expiryDate: expiryDateRaw ? new Date(expiryDateRaw) : null,
      notes: notes || null,
    },
  });

  await prisma.documentHistory.create({
    data: { documentId: document.id, action: "uploaded", performedBy: employeeId },
  });

  revalidatePath("/dlvc/admin/documents");
  redirect(`/dlvc/admin/documents?dept=${document.departmentId}`);
}

async function reviewDocument(documentId: number, decision: "approved" | "rejected"): Promise<DocumentFormState> {
  const session = await auth();
  const employeeId = session?.user?.employeeId;
  if (!employeeId) return { error: "Tài khoản của bạn chưa gắn với hồ sơ nhân viên." };

  const document = await prisma.adminDocument.findUnique({ where: { id: documentId } });
  if (!document) return { error: "Không tìm thấy tài liệu." };

  if (!canApproveDocumentsForDepartment(session, document.departmentId)) {
    return { error: "Bạn không có quyền duyệt tài liệu của phòng ban này." };
  }

  await prisma.adminDocument.update({
    where: { id: documentId },
    data: { status: decision, approvedBy: employeeId, approvedAt: new Date() },
  });

  await prisma.documentHistory.create({
    data: { documentId, action: decision, performedBy: employeeId },
  });

  revalidatePath(`/dlvc/admin/documents/${documentId}`);
  revalidatePath("/dlvc/admin/documents");
}

export async function approveDocumentAction(
  documentId: number,
  _prevState: DocumentFormState,
  _formData: FormData,
): Promise<DocumentFormState> {
  return reviewDocument(documentId, "approved");
}

export async function rejectDocumentAction(
  documentId: number,
  _prevState: DocumentFormState,
  _formData: FormData,
): Promise<DocumentFormState> {
  return reviewDocument(documentId, "rejected");
}
