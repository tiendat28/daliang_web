import type { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface User {
    roleName?: string;
    employeeId?: number | null;
    employeeCode?: string | null;
    departmentId?: number | null;
    permissions?: Record<string, boolean> | null;
  }

  interface Session {
    user: {
      id: string;
      roleName: string;
      employeeId: number | null;
      employeeCode: string | null;
      departmentId: number | null;
      permissions: Record<string, boolean> | null;
    } & DefaultSession["user"];
  }
}

// `next-auth/jwt` only re-exports `JWT` from `@auth/core/jwt` ("export * from
// '@auth/core/jwt'"); NextAuth's own callback signatures import `JWT` directly
// from `@auth/core/jwt`, so augmenting "next-auth/jwt" alone never reaches the
// type actually used by `callbacks.jwt`/`callbacks.session`. Augment both.
declare module "next-auth/jwt" {
  interface JWT {
    roleName?: string;
    employeeId?: number | null;
    employeeCode?: string | null;
    departmentId?: number | null;
    permissions?: Record<string, boolean> | null;
  }
}

declare module "@auth/core/jwt" {
  interface JWT {
    roleName?: string;
    employeeId?: number | null;
    employeeCode?: string | null;
    departmentId?: number | null;
    permissions?: Record<string, boolean> | null;
  }
}
