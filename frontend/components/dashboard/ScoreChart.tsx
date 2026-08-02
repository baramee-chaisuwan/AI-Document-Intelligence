"use client";

import {
    ResponsiveContainer,
    BarChart,
    Bar,
    CartesianGrid,
    Tooltip,
    XAxis,
    YAxis,
    Cell,
} from "recharts";

type Props = {
    data: {
        score_range: string;
        count: number;
    }[];
};

const COLORS = [
    "#EF4444", // 0-20
    "#F97316", // 21-40
    "#FACC15", // 41-60
    "#3B82F6", // 61-80
    "#10B981", // 81-100
];

export default function ScoreChart({
    data,
}: Props) {

    return (

        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

            <h3 className="text-lg font-semibold text-gray-800">
                AI Score Distribution
            </h3>

            <p className="mb-4 text-sm text-gray-500">
                Number of candidates grouped by AI score
            </p>

            <ResponsiveContainer
                width="100%"
                height={320}
            >

                <BarChart
                    data={data}
                    margin={{
                        top: 10,
                        right: 20,
                        left: -10,
                        bottom: 0,
                    }}
                >

                    <CartesianGrid
                        strokeDasharray="3 3"
                        vertical={false}
                    />

                    <XAxis
                        dataKey="score_range"
                        tick={{
                            fontSize: 12,
                        }}
                    />

                    <YAxis
                        allowDecimals={false}
                        tick={{
                            fontSize: 12,
                        }}
                    />

                    <Tooltip
                        formatter={(value) => [
                            `${value} Candidates`,
                            "Count",
                        ]}
                    />

                    <Bar
                        dataKey="count"
                        radius={[8, 8, 0, 0]}
                        animationDuration={800}
                    >

                        {data.map((_, index) => (

                            <Cell
                                key={index}
                                fill={COLORS[index % COLORS.length]}
                            />

                        ))}

                    </Bar>

                </BarChart>

            </ResponsiveContainer>

        </div>

    );
}