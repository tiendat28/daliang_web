import type { DocumentStatus, Role } from "../enums";

export interface DocumentSummary {
  id: string;
  code: string;
  titleVi: string;
  titleEn: string | null;
  version: string;
  status: DocumentStatus;
  createdAt: Date;
  owner: UserSummary;
}

export interface UserSummary {
  id: string;
  email: string;
  fullName: string;
  role: Role;
}
