import { Bell } from "lucide-react";

export default function Navbar() {
    return (
        <header className="flex h-16 items-center justify-between border-b bg-white px-8">
            <h1 className="text-xl font-bold">
                AI Document Intelligence
            </h1>

            <div className="flex items-center gap-5">
                <button className="relative rounded-full p-2 hover:bg-gray-100">
                    <Bell size={22} />

                    <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />
                </button>

                <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-600 text-white font-semibold">
                        B
                    </div>

                    <div>
                        <p className="text-sm font-semibold">
                            Baramee
                        </p>

                        <p className="text-xs text-gray-500">
                            Admin
                        </p>
                    </div>
                </div>
            </div>
        </header>
    );
}