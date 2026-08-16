"use server";

import { prisma } from "@daliang/db";

export type LeadFormState = { success?: boolean; error?: string } | undefined;

export async function submitLead(_prevState: LeadFormState, formData: FormData): Promise<LeadFormState> {
  const fullName = String(formData.get("fullName") ?? "").trim();
  const companyName = String(formData.get("companyName") ?? "").trim();
  const phone = String(formData.get("phone") ?? "").trim();
  const email = String(formData.get("email") ?? "").trim();
  const message = String(formData.get("message") ?? "").trim();

  if (!fullName) return { error: "Vui lòng nhập họ và tên." };
  if (!phone && !email) return { error: "Vui lòng để lại số điện thoại hoặc email để chúng tôi liên hệ lại." };

  await prisma.lead.create({
    data: {
      fullName,
      companyName: companyName || null,
      phone: phone || null,
      email: email || null,
      message: message || null,
    },
  });

  // TODO: tích hợp gửi email thông báo lead mới (chưa cần cho bản đầu).

  return { success: true };
}
