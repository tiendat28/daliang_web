export default function Container({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-zinc-50 p-8 font-sans dark:bg-black">
      <main className="mx-auto max-w-5xl">{children}</main>
    </div>
  );
}
