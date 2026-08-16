"use server";

import { AuthError } from "next-auth";
import { signIn } from "@/auth";

export type LoginState = { error?: string } | undefined;

export async function loginAction(_prevState: LoginState, formData: FormData): Promise<LoginState> {
  const username = formData.get("username");
  const password = formData.get("password");
  const callbackUrl = formData.get("callbackUrl");

  if (typeof username !== "string" || !username || typeof password !== "string" || !password) {
    return { error: "Vui lòng nhập tên đăng nhập và mật khẩu." };
  }

  try {
    await signIn("credentials", {
      username,
      password,
      redirectTo: typeof callbackUrl === "string" && callbackUrl ? callbackUrl : "/dlvc/admin",
    });
  } catch (error) {
    if (error instanceof AuthError) {
      return { error: "Sai tên đăng nhập hoặc mật khẩu." };
    }
    throw error;
  }
}
