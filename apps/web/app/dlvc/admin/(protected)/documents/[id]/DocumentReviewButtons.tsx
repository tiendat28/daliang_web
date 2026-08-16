"use client";

import { useActionState } from "react";
import { approveDocumentAction, rejectDocumentAction, type DocumentFormState } from "../actions";

export default function DocumentReviewButtons({ documentId }: { documentId: number }) {
  const [approveState, approveAction, approvePending] = useActionState<DocumentFormState, FormData>(
    approveDocumentAction.bind(null, documentId),
    undefined,
  );
  const [rejectState, rejectAction, rejectPending] = useActionState<DocumentFormState, FormData>(
    rejectDocumentAction.bind(null, documentId),
    undefined,
  );

  const error = approveState?.error ?? rejectState?.error;

  return (
    <div className="flex flex-col gap-2.5">
      <div className="flex gap-2.5">
        <form action={approveAction}>
          <button
            type="submit"
            disabled={approvePending || rejectPending}
            className="flex h-10 items-center gap-1.5 rounded-[9px] bg-dlvc-ok px-4 text-[13.5px] font-semibold text-white transition-[filter,box-shadow,transform] duration-150 hover:not-disabled:-translate-y-px hover:not-disabled:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {approvePending ? "Đang duyệt…" : "✓ Duyệt"}
          </button>
        </form>
        <form action={rejectAction}>
          <button
            type="submit"
            disabled={approvePending || rejectPending}
            className="flex h-10 items-center gap-1.5 rounded-[9px] border border-dlvc-danger px-4 text-[13.5px] font-semibold text-dlvc-danger transition-[filter,box-shadow,transform] duration-150 hover:not-disabled:-translate-y-px hover:not-disabled:bg-dlvc-danger/10 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {rejectPending ? "Đang xử lý…" : "✕ Từ chối"}
          </button>
        </form>
      </div>
      {error ? <p className="text-[12.5px] font-medium text-dlvc-danger">{error}</p> : null}
    </div>
  );
}
