import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";

type AppLayoutProps = {
    title: string;
    description?: string;
    children: React.ReactNode;
};

export default function AppLayout({
    title,
    description,
    children,
}: AppLayoutProps) {
    return (
        <div className="min-h-screen bg-slate-100">
            <Navbar />

            <div className="flex">
                <Sidebar />

                <main className="flex-1 p-8">
                    <h2 className="text-3xl font-bold">
                        {title}
                    </h2>

                    {description && (
                        <p className="mt-2 text-gray-500">
                            {description}
                        </p>
                    )}

                    {children}
                </main>
            </div>
        </div>
    );
}