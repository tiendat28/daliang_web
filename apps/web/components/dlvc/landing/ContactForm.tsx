"use client";

import { useActionState } from "react";
import { submitLead, type LeadFormState } from "@/app/actions";

const inputClass =
  "rounded-[9px] border border-dlvc-landing-border bg-dlvc-paper px-3.5 py-2.75 text-[14px] text-dlvc-landing-ink transition-[border-color,box-shadow] duration-150 focus:border-dlvc-cobalt focus:shadow-[0_0_0_3px_rgba(34,211,238,0.4)] focus:outline-none";
const labelClass = "flex flex-col gap-1.5 text-[12.5px] font-semibold text-dlvc-landing-ink-soft";

export default function ContactForm() {
  const [state, formAction, pending] = useActionState<LeadFormState, FormData>(submitLead, undefined);

  if (state?.success) {
    return (
      <div className="rounded-2xl border border-dlvc-landing-border bg-dlvc-surface p-8 text-center">
        <div className="mb-3 text-[32px]">✓</div>
        <h3 className="mb-2 text-[17px] font-bold text-dlvc-landing-ink">Đã gửi yêu cầu tư vấn</h3>
        <p className="text-[13.5px] text-dlvc-landing-ink-soft">
          Cảm ơn bạn đã liên hệ. Đội ngũ kỹ thuật của DLVC sẽ phản hồi trong thời gian sớm nhất.
        </p>
      </div>
    );
  }

  return (
    <form action={formAction} className="rounded-2xl border border-dlvc-landing-border bg-dlvc-surface p-8">
      <div className="mb-3.5 grid grid-cols-1 gap-3.5 min-[560px]:grid-cols-2">
        <label className={labelClass}>
          Họ và tên
          <input name="fullName" required placeholder="Nguyễn Văn A" className={inputClass} />
        </label>
        <label className={labelClass}>
          Công ty / Nhà máy
          <input name="companyName" placeholder="Tên công ty" className={inputClass} />
        </label>
      </div>
      <div className="mb-3.5 grid grid-cols-1 gap-3.5 min-[560px]:grid-cols-2">
        <label className={labelClass}>
          Số điện thoại
          <input name="phone" type="tel" placeholder="09xx xxx xxx" className={inputClass} />
        </label>
        <label className={labelClass}>
          Email
          <input name="email" type="email" placeholder="email@congty.com" className={inputClass} />
        </label>
      </div>
      <label className={`${labelClass} mb-3.5`}>
        Nội dung cần tư vấn
        <textarea
          name="message"
          rows={4}
          placeholder="Mô tả ngắn về quy trình mạ / hoá chất bạn đang cần..."
          className={`${inputClass} resize-vertical`}
        />
      </label>

      {state?.error ? (
        <p className="mb-3.5 rounded-lg border border-dlvc-danger/30 bg-dlvc-danger/10 px-3.5 py-2.5 text-[13px] font-medium text-dlvc-danger">
          {state.error}
        </p>
      ) : null}

      <button
        type="submit"
        disabled={pending}
        className="flex w-full items-center justify-center gap-2 rounded-lg bg-dlvc-cobalt-deep py-3.25 text-[14.5px] font-bold text-white transition-[filter,box-shadow,transform] duration-150 hover:not-disabled:-translate-y-px hover:not-disabled:shadow-[0_0_0_4px_var(--color-dlvc-cobalt-soft),0_0_26px_rgba(34,211,238,0.4)] hover:not-disabled:brightness-[1.3] disabled:cursor-not-allowed disabled:opacity-60"
      >
        {pending ? "Đang gửi…" : "Gửi yêu cầu tư vấn"}
      </button>
    </form>
  );
}
