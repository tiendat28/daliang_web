import { NextResponse } from "next/server";
import { auth } from "@/auth";

export default auth((req) => {
  const { pathname } = req.nextUrl;
  const isLoginPage = pathname === "/dlvc/admin/login";

  if (!req.auth && !isLoginPage) {
    const loginUrl = new URL("/dlvc/admin/login", req.nextUrl);
    loginUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (req.auth && isLoginPage) {
    return NextResponse.redirect(new URL("/dlvc/admin", req.nextUrl));
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/dlvc/admin/:path*"],
};
