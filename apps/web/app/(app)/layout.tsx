import AppHeader from "@/components/mock/AppHeader";

export default function AppGroupLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen flex-col">
      <AppHeader />
      <div className="flex min-h-0 flex-1">{children}</div>
    </div>
  );
}
