const candidates = [
    {
        id: 1,
        name: "John Doe",
        position: "AI Engineer",
        score: 92,
        status: "Matched",
    },
    {
        id: 2,
        name: "Jane Smith",
        position: "Data Engineer",
        score: 88,
        status: "Matched",
    },
    {
        id: 3,
        name: "Michael Brown",
        position: "Backend Developer",
        score: 81,
        status: "Review",
    },
];

export default function RecentCandidates() {
    return (
        <div className="mt-8 rounded-xl border bg-white p-6 shadow-sm">
            <h3 className="mb-5 text-xl font-semibold">
                Recent Candidates
            </h3>

            <div className="overflow-x-auto">
                <table className="w-full text-left">
                    <thead>
                        <tr className="border-b text-sm text-gray-500">
                            <th className="pb-3">Name</th>
                            <th className="pb-3">Position</th>
                            <th className="pb-3">Score</th>
                            <th className="pb-3">Status</th>
                        </tr>
                    </thead>

                    <tbody>
                        {candidates.map((candidate) => (
                            <tr
                                key={candidate.id}
                                className="border-b last:border-none"
                            >
                                <td className="py-4 font-medium">
                                    {candidate.name}
                                </td>

                                <td className="py-4 text-gray-600">
                                    {candidate.position}
                                </td>

                                <td className="py-4">
                                    {candidate.score}%
                                </td>

                                <td className="py-4">
                                    <span
                                        className={`rounded-full px-3 py-1 text-sm font-medium ${candidate.status === "Matched"
                                                ? "bg-green-100 text-green-700"
                                                : "bg-yellow-100 text-yellow-700"
                                            }`}
                                    >
                                        {candidate.status}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}