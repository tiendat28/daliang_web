"use client";

import { useActionState } from "react";
import { loginAction, type LoginState } from "./actions";

export default function LoginForm({ callbackUrl }: { callbackUrl?: string }) {
  const [state, action, pending] = useActionState<LoginState, FormData>(loginAction, undefined);

  return (
    <form action={action} className="flex flex-col gap-4">
      <input type="hidden" name="callbackUrl" value={callbackUrl ?? ""} />

      <label className="flex flex-col gap-1.5 text-[13px] font-medium text-dlvc-ink-soft">
        Tên đăng nhập
        <input
          type="text"
          name="username"
          autoComplete="username"
          placeholder="ten.dangnhap"
          required
          className="h-11 rounded-[9px] border border-dlvc-border bg-dlvc-bg px-3.5 font-dlvc-mono text-[14px] text-dlvc-ink placeholder:text-dlvc-ink-soft/60 transition-[border-color,box-shadow] duration-150 focus:border-dlvc-accent focus:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] focus:outline-none"
        />
      </label>

      <label className="flex flex-col gap-1.5 text-[13px] font-medium text-dlvc-ink-soft">
        Mật khẩu
        <input
          type="password"
          name="password"
          autoComplete="current-password"
          placeholder="••••••••"
          required
          className="h-11 rounded-[9px] border border-dlvc-border bg-dlvc-bg px-3.5 text-[14px] text-dlvc-ink transition-[border-color,box-shadow] duration-150 focus:border-dlvc-accent focus:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] focus:outline-none"
        />
      </label>

      {state?.error ? (
        <p className="rounded-lg border border-dlvc-danger/30 bg-dlvc-danger/10 px-3.5 py-2.5 text-[13px] font-medium text-dlvc-danger">
          {state.error}
        </p>
      ) : null}

      <button
        type="submit"
        disabled={pending}
        className="mt-1 flex h-11 items-center justify-center gap-2 rounded-[9px] bg-dlvc-sidebar text-[14px] font-semibold text-white transition-[filter,box-shadow,transform] duration-150 hover:not-disabled:-translate-y-px hover:not-disabled:shadow-[0_0_0_3px_rgba(34,211,238,0.45)] hover:not-disabled:brightness-125 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {pending ? "Đang đăng nhập…" : "Đăng nhập"}
      </button>
    </form>
  );
}
