import { Bell } from "lucide-react";

export default function Navbar() {

    return (

        <header
            className="
                sticky
                top-0
                z-50
                flex
                h-16
                items-center
                justify-between
                border-b
                bg-white
                px-8
                shadow-sm
            "
        >

            <div>

                <h1 className="text-2xl font-bold text-slate-900">
                    AI Document Intelligence
                </h1>

                <p className="text-sm text-gray-500">
                    Applicant Tracking System
                </p>

            </div>

            <div className="flex items-center gap-6">

                <button
                    className="
                        rounded-full
                        p-2
                        transition
                        hover:bg-slate-100
                    "
                >

                    <Bell
                        size={22}
                        className="text-gray-600"
                    />

                </button>

                <div className="h-8 w-px bg-gray-200" />

                <div className="flex items-center gap-3">

                    <div
                        className="
                            flex
                            h-10
                            w-10
                            items-center
                            justify-center
                            rounded-full
                            bg-blue-600
                            text-lg
                            font-bold
                            text-white
                        "
                    >
                        B
                    </div>

                    <div>

                        <p className="font-semibold text-slate-900">
                            Baramee
                        </p>

                        <div className="flex items-center gap-2">

                            <span className="h-2 w-2 rounded-full bg-green-500" />

                            <p className="text-xs text-gray-500">
                                Administrator
                            </p>

                        </div>

                    </div>

                </div>

            </div>

        </header>

    );

}