import {
    LayoutDashboard,
    Users,
    Upload,
    Search,
    BarChart3,
    Settings,
} from "lucide-react";

const menuItems = [
    {
        title: "Dashboard",
        icon: LayoutDashboard,
        active: true,
    },
    {
        title: "Candidates",
        icon: Users,
    },
    {
        title: "Upload Resume",
        icon: Upload,
    },
    {
        title: "Search",
        icon: Search,
    },
    {
        title: "Analytics",
        icon: BarChart3,
    },
    {
        title: "Settings",
        icon: Settings,
    },
];

export default function Sidebar() {
    return (
        <aside className="w-64 border-r bg-white p-6">
            <p className="mb-6 text-lg font-semibold">
                Navigation
            </p>

            <nav className="space-y-2">
                {menuItems.map((item) => {
                    const Icon = item.icon;

                    return (
                        <button
                            key={item.title}
                            className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left transition ${item.active
                                    ? "bg-blue-600 text-white"
                                    : "text-gray-700 hover:bg-gray-100"
                                }`}
                        >
                            <Icon size={20} />
                            <span>{item.title}</span>
                        </button>
                    );
                })}
            </nav>
        </aside>
    );
}