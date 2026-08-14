import { docs } from "@/lib/mock-data";
import DocumentsView from "@/components/mock/DocumentsView";

export default function DocumentsPage() {
  return <DocumentsView docs={docs.slice(0, 5)} />;
}
