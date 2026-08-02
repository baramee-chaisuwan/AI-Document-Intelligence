"use client";

import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    ResponsiveContainer,
    Legend,
} from "recharts";


type Props = {
    data: {
        level: string;
        count: number;
    }[];
};


const COLORS = [
    "#3B82F6",
    "#10B981",
    "#F59E0B",
    "#EF4444",
];


export default function LevelChart({
    data,
}: Props) {


    return (

        <div
            className="
                rounded-xl
                border
                border-gray-200
                bg-white
                p-6
                shadow-sm
            "
        >

            <h3 className="text-lg font-semibold text-gray-800">
                Candidate Level Distribution
            </h3>


            <p className="mb-4 text-sm text-gray-500">
                Distribution of candidates by experience level
            </p>



            <ResponsiveContainer
                width="100%"
                height={320}
            >

                <PieChart>


                    <Pie

                        data={data}

                        dataKey="count"

                        nameKey="level"

                        cx="50%"

                        cy="50%"

                        outerRadius={110}

                        innerRadius={45}

                        paddingAngle={3}


                        label={({ percent = 0 }) =>
                            `${(percent * 100).toFixed(0)}%`
                        }


                        animationDuration={800}

                    >

                        {
                            data.map((_, index) => (

                                <Cell
                                    key={index}
                                    fill={
                                        COLORS[
                                        index % COLORS.length
                                        ]
                                    }
                                />

                            ))
                        }


                    </Pie>



                    <Tooltip

                        formatter={(value) => [

                            `${value} Candidates`,

                            "Count",

                        ]}

                    />



                    <Legend

                        verticalAlign="bottom"

                        height={36}

                    />


                </PieChart>


            </ResponsiveContainer>


        </div>

    );

}