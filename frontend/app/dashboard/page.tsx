import AppLayout from "@/components/layout/AppLayout";
import Card from "@/components/ui/Card";
import RecentCandidates from "@/components/dashboard/RecentCandidates";

export default function DashboardPage() {
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
        <AppLayout
            title="Dashboard"
            description="Welcome to AI Document Intelligence ATS"
        >
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
        </AppLayout>
    );
}