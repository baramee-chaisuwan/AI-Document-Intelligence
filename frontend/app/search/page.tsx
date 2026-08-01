import AppLayout from "@/components/layout/AppLayout";

export default function SearchPage() {
    return (
        <AppLayout
            title="Search"
            description="Search candidates using AI"
        >
            <div className="mt-6 rounded-lg bg-white p-6 shadow">
                <h2 className="text-xl font-bold">
                    AI Search
                </h2>

                <p className="mt-2 text-gray-500">
                    Search candidates using semantic search and AI ranking.
                </p>
            </div>
        </AppLayout>
    );
}