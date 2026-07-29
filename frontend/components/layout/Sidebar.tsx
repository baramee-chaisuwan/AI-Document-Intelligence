export default function Sidebar() {
    return (
        <aside className="w-64 border-r bg-white p-6">
            <p className="font-semibold mb-4">Navigation</p>

            <nav className="space-y-3">
                <p>Dashboard</p>
                <p>Candidates</p>
                <p>Upload Resume</p>
                <p>Search</p>
            </nav>
        </aside>
    );
}