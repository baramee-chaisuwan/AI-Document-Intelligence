type ScoreBreakdownProps = {
    breakdown: Record<string, number>;
};

export default function ScoreBreakdown({
    breakdown,
}: ScoreBreakdownProps) {
    return (
        <div className="mt-6 rounded-lg bg-white p-6 shadow">
            <h3 className="text-xl font-bold">
                AI Evaluation Breakdown
            </h3>

            <div className="mt-4 space-y-4">
                {Object.entries(breakdown).map(
                    ([key, value]) => (
                        <div key={key}>
                            <div className="mb-1 flex justify-between">
                                <span className="capitalize">
                                    {key.replaceAll("_", " ")}
                                </span>

                                <span className="font-semibold">
                                    {value}
                                </span>
                            </div>

                            <div className="h-3 rounded-full bg-gray-200">
                                <div
                                    className="h-3 rounded-full bg-blue-600"
                                    style={{
                                        width: `${Math.min(
                                            value * 5,
                                            100
                                        )}%`,
                                    }}
                                />
                            </div>
                        </div>
                    )
                )}
            </div>
        </div>
    );
}