import { z } from "zod";
import { DocumentStatus, Role } from "../enums";

export const createDocumentSchema = z.object({
  code: z.string().min(1),
  titleVi: z.string().min(1),
  titleEn: z.string().optional(),
  version: z.string().default("1.0"),
  status: z.enum(Object.values(DocumentStatus) as [string, ...string[]]).default(DocumentStatus.DRAFT),
  ownerId: z.string().uuid(),
});
export type CreateDocumentInput = z.infer<typeof createDocumentSchema>;

export const createUserSchema = z.object({
  email: z.string().email(),
  fullName: z.string().min(1),
  role: z.enum(Object.values(Role) as [string, ...string[]]).default(Role.STAFF),
  departmentId: z.string().uuid().optional(),
});
export type CreateUserInput = z.infer<typeof createUserSchema>;
