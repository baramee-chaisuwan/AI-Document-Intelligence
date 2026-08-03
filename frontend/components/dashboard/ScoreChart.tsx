"use client";

import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

import type {
    ScoreDistribution,
} from "@/services/dashboard";


type Props = {
    data: ScoreDistribution[];
};


const SCORE_COLORS: Record<string, string> = {
    "0-20": "#EF4444",
    "21-40": "#F97316",
    "41-60": "#FACC15",
    "61-80": "#3B82F6",
    "81-100": "#10B981",
};


const FALLBACK_COLOR = "#94A3B8";


export default function ScoreChart({
    data,
}: Props) {

    const validData = data.filter(
        (item) =>
            item.count >= 0
            && item.score_range.trim()
    );


    const totalCandidates = validData.reduce(
        (total, item) => total + item.count,
        0
    );


    return (

        <section
            className="
                rounded-2xl
                border
                border-gray-200
                bg-white
                p-6
                shadow-sm
            "
        >

            <div
                className="
                    flex
                    items-start
                    justify-between
                    gap-4
                "
            >

                <div>

                    <h3
                        className="
                            text-lg
                            font-semibold
                            text-gray-900
                        "
                    >
                        AI Score Distribution
                    </h3>

                    <p
                        className="
                            mt-1
                            text-sm
                            text-gray-500
                        "
                    >
                        Number of candidates grouped by AI score
                    </p>

                </div>


                <div
                    className="
                        rounded-lg
                        bg-gray-50
                        px-3
                        py-2
                        text-right
                    "
                >

                    <p
                        className="
                            text-xs
                            font-medium
                            uppercase
                            tracking-wide
                            text-gray-500
                        "
                    >
                        Total
                    </p>

                    <p
                        className="
                            text-xl
                            font-bold
                            text-gray-900
                        "
                    >
                        {totalCandidates}
                    </p>

                </div>

            </div>


            {validData.length === 0 ? (

                <div
                    className="
                        flex
                        h-80
                        items-center
                        justify-center
                        text-sm
                        text-gray-500
                    "
                >
                    No score distribution data available.
                </div>

            ) : (

                <ResponsiveContainer
                    width="100%"
                    height={320}
                >

                    <BarChart
                        data={validData}
                        margin={{
                            top: 18,
                            right: 16,
                            left: -10,
                            bottom: 0,
                        }}
                    >

                        <CartesianGrid
                            strokeDasharray="3 3"
                            vertical={false}
                            stroke="#E5E7EB"
                        />

                        <XAxis
                            dataKey="score_range"
                            tick={{
                                fontSize: 12,
                            }}
                            axisLine={false}
                            tickLine={false}
                        />

                        <YAxis
                            allowDecimals={false}
                            tick={{
                                fontSize: 12,
                            }}
                            axisLine={false}
                            tickLine={false}
                        />

                        <Tooltip
                            formatter={(value) => [
                                `${Number(value)} candidates`,
                                "Count",
                            ]}
                            labelFormatter={(label) =>
                                `Score range: ${label}`
                            }
                            contentStyle={{
                                borderRadius: "12px",
                                borderColor: "#E5E7EB",
                            }}
                        />

                        <Bar
                            dataKey="count"
                            radius={[8, 8, 0, 0]}
                            animationDuration={700}
                            maxBarSize={64}
                        >

                            {validData.map((item) => (

                                <Cell
                                    key={item.score_range}
                                    fill={
                                        SCORE_COLORS[
                                        item.score_range
                                        ]
                                        ?? FALLBACK_COLOR
                                    }
                                />

                            ))}

                        </Bar>

                    </BarChart>

                </ResponsiveContainer>

            )}

        </section>

    );

}