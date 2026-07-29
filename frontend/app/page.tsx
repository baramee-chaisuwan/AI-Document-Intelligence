import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-100">
      <Navbar />

      <div className="flex">
        <Sidebar />

        <main className="flex-1 p-8">
          <h2 className="text-3xl font-bold">
            Dashboard
          </h2>

          <p className="mt-2 text-gray-500">
            Welcome to AI Document Intelligence ATS
          </p>
        </main>
      </div>
    </div>
  );
}