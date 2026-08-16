import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import bcrypt from "bcryptjs";
import { prisma } from "@daliang/db";

export const {
  handlers: { GET, POST },
  auth,
  signIn,
  signOut,
} = NextAuth({
  session: { strategy: "jwt" },
  pages: { signIn: "/dlvc/admin/login" },
  trustHost: true,
  providers: [
    Credentials({
      credentials: {
        username: { label: "Tên đăng nhập" },
        password: { label: "Mật khẩu", type: "password" },
      },
      async authorize(credentials) {
        const username = credentials?.username;
        const password = credentials?.password;
        if (typeof username !== "string" || typeof password !== "string" || !username || !password) {
          return null;
        }

        const account = await prisma.adminUser.findUnique({
          where: { username },
          include: { role: true, employee: true },
        });

        if (!account || account.status !== "active") {
          return null;
        }

        const passwordValid = await bcrypt.compare(password, account.passwordHash);
        if (!passwordValid) {
          return null;
        }

        await prisma.adminUser.update({
          where: { id: account.id },
          data: { lastLoginAt: new Date() },
        });

        return {
          id: String(account.id),
          name: account.employee?.fullName ?? account.username,
          roleName: account.role.roleName,
          employeeId: account.employeeId,
          employeeCode: account.employee?.employeeCode ?? null,
          departmentId: account.employee?.departmentId ?? null,
          permissions: (account.role.permissions as Record<string, boolean> | null) ?? null,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.roleName = user.roleName;
        token.employeeId = user.employeeId;
        token.employeeCode = user.employeeCode;
        token.departmentId = user.departmentId;
        token.permissions = user.permissions;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.id = token.sub!;
      session.user.roleName = token.roleName ?? "Nhân viên";
      session.user.employeeId = token.employeeId ?? null;
      session.user.employeeCode = token.employeeCode ?? null;
      session.user.departmentId = token.departmentId ?? null;
      session.user.permissions = token.permissions ?? null;
      return session;
    },
  },
});
