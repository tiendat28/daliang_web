export const Role = {
  STAFF: "staff",
  MANAGER: "manager",
  ADMIN: "admin",
} as const;
export type Role = (typeof Role)[keyof typeof Role];

export const DocumentStatus = {
  DRAFT: "draft",
  REVIEW: "review",
  PUBLISHED: "published",
  ARCHIVED: "archived",
} as const;
export type DocumentStatus = (typeof DocumentStatus)[keyof typeof DocumentStatus];
