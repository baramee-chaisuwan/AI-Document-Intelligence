type ScoreBreakdownProps = {
    breakdown: Record<string, number>;
};


function getMaxScore(key: string) {

    const maxScores: Record<string, number> = {

        python: 15,
        sql: 15,
        etl: 15,
        ml: 15,
        internship: 10,
        projects: 10,

    };


    return maxScores[key] ?? 100;

}



function progressColor(percent: number) {

    if (percent >= 80)
        return "bg-green-500";

    if (percent >= 60)
        return "bg-blue-500";

    if (percent >= 40)
        return "bg-yellow-500";

    return "bg-red-500";

}



function badgeColor(percent: number) {

    if (percent >= 80)
        return "bg-green-100 text-green-700";

    if (percent >= 60)
        return "bg-blue-100 text-blue-700";

    if (percent >= 40)
        return "bg-yellow-100 text-yellow-700";

    return "bg-red-100 text-red-700";

}



export default function ScoreBreakdown({
    breakdown,
}: ScoreBreakdownProps) {


    const entries = Object.entries(
        breakdown ?? {}
    );


    return (

        <div
            className="
                mt-6
                rounded-xl
                border
                border-gray-200
                bg-white
                p-6
                shadow-sm
            "
        >

            <h3 className="text-xl font-semibold">
                AI Evaluation Breakdown
            </h3>


            <p className="mt-1 text-sm text-gray-500">
                Explainable AI scoring based on candidate profile
            </p>



            {
                entries.length === 0 ? (

                    <p className="mt-6 text-sm text-gray-500">
                        No evaluation breakdown available.
                    </p>

                ) : (


                    <div className="mt-6 space-y-6">


                        {
                            entries.map(
                                ([key, value]) => {


                                    const maxScore =
                                        getMaxScore(key);


                                    const percent =
                                        Math.round(
                                            (value / maxScore) * 100
                                        );


                                    return (

                                        <div
                                            key={key}
                                        >


                                            <div
                                                className="
                                                    mb-2
                                                    flex
                                                    justify-between
                                                    items-center
                                                "
                                            >

                                                <span
                                                    className="
                                                        font-medium
                                                        capitalize
                                                        text-gray-700
                                                    "
                                                >

                                                    {key.replaceAll(
                                                        "_",
                                                        " "
                                                    )}

                                                </span>



                                                <div className="flex items-center gap-2">


                                                    <span className="text-sm text-gray-500">
                                                        {value}/{maxScore}
                                                    </span>


                                                    <span
                                                        className={`
                                                            rounded-full
                                                            px-3
                                                            py-1
                                                            text-sm
                                                            font-bold
                                                            ${badgeColor(
                                                            percent
                                                        )}
                                                        `}
                                                    >

                                                        {percent}%

                                                    </span>


                                                </div>


                                            </div>



                                            <div
                                                className="
                                                    h-3
                                                    overflow-hidden
                                                    rounded-full
                                                    bg-gray-200
                                                "
                                            >

                                                <div

                                                    className={`
                                                        h-full
                                                        rounded-full
                                                        transition-all
                                                        duration-500
                                                        ${progressColor(
                                                        percent
                                                    )}
                                                    `}

                                                    style={{
                                                        width:
                                                            `${percent}%`,
                                                    }}

                                                />

                                            </div>


                                        </div>

                                    );


                                }
                            )
                        }


                    </div>

                )
            }


        </div>

    );

}