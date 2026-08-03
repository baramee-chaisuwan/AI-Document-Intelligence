"use client";

import {
    Cell,
    Legend,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
} from "recharts";

import type {
    LevelDistribution,
} from "@/services/dashboard";


type Props = {
    data: LevelDistribution[];
};


const LEVEL_COLORS: Record<string, string> = {
    "Entry-Level": "#6366F1",
    Junior: "#3B82F6",
    "Mid-Level": "#F59E0B",
    Senior: "#10B981",
};


const FALLBACK_COLOR = "#94A3B8";


export default function LevelChart({
    data,
}: Props) {

    const validData = data.filter(
        (item) =>
            item.count > 0
            && item.level.trim()
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
                        Candidate Level Distribution
                    </h3>

                    <p
                        className="
                            mt-1
                            text-sm
                            text-gray-500
                        "
                    >
                        Distribution of candidates by experience level
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
                    No candidate level data available.
                </div>

            ) : (

                <ResponsiveContainer
                    width="100%"
                    height={320}
                >

                    <PieChart>

                        <Pie
                            data={validData}
                            dataKey="count"
                            nameKey="level"
                            cx="50%"
                            cy="47%"
                            innerRadius={58}
                            outerRadius={108}
                            paddingAngle={3}
                            animationDuration={700}
                            labelLine={false}
                            label={({
                                percent = 0,
                            }) => (
                                `${Math.round(
                                    percent * 100
                                )}%`
                            )}
                        >

                            {validData.map((item) => (

                                <Cell
                                    key={item.level}
                                    fill={
                                        LEVEL_COLORS[
                                        item.level
                                        ]
                                        ?? FALLBACK_COLOR
                                    }
                                />

                            ))}

                        </Pie>


                        <Tooltip
                            formatter={(
                                value,
                                name
                            ) => [
                                    `${Number(value)} candidates`,
                                    String(name),
                                ]}
                            contentStyle={{
                                borderRadius: "12px",
                                borderColor: "#E5E7EB",
                            }}
                        />


                        <Legend
                            verticalAlign="bottom"
                            height={36}
                            iconType="circle"
                        />

                    </PieChart>

                </ResponsiveContainer>

            )}

        </section>

    );

}