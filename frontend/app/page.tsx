import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";
import Card from "@/components/ui/Card";
import RecentCandidates from "@/components/dashboard/RecentCandidates";

export default function Home() {
  const dashboardStats = [
    {
      title: "Total Candidates",
      value: 128,
    },
    {
      title: "Uploaded Today",
      value: 12,
    },
    {
      title: "Matched",
      value: 86,
    },
    {
      title: "Pending Review",
      value: 18,
    },
  ];

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

          <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
            {dashboardStats.map((stat) => (
              <Card
                key={stat.title}
                title={stat.title}
                value={stat.value}
              />
            ))}
          </div>

          <RecentCandidates />
        </main>
      </div>
    </div>
  );
}