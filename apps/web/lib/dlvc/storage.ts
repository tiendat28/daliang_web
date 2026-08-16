import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { randomUUID } from "node:crypto";

const UPLOAD_DIR = path.join(process.cwd(), "public", "uploads", "dlvc-documents");
const PUBLIC_PREFIX = "/uploads/dlvc-documents";

/**
 * Saves an uploaded file to /public/uploads (dev-local storage). Swap this
 * function's body for an S3-compatible client later; callers only depend on
 * the returned { filePath, fileFormat, fileSizeKb } shape.
 */
export async function saveUploadedFile(file: File): Promise<{
  filePath: string;
  fileFormat: string;
  fileSizeKb: number;
}> {
  await mkdir(UPLOAD_DIR, { recursive: true });

  const originalName = file.name || "tai-lieu";
  const ext = path.extname(originalName).replace(".", "").toUpperCase() || "FILE";
  const safeBase = path
    .basename(originalName, path.extname(originalName))
    .replace(/[^a-zA-Z0-9-_]+/g, "-")
    .slice(0, 60);
  const storedName = `${randomUUID()}-${safeBase || "tai-lieu"}.${ext.toLowerCase()}`;

  const buffer = Buffer.from(await file.arrayBuffer());
  await writeFile(path.join(UPLOAD_DIR, storedName), buffer);

  return {
    filePath: `${PUBLIC_PREFIX}/${storedName}`,
    fileFormat: ext,
    fileSizeKb: Math.max(1, Math.round(file.size / 1024)),
  };
}
