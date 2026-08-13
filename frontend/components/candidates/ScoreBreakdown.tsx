import type {
    ScoreBreakdown as ScoreBreakdownType,
} from "@/services/candidate";
import {
    scoreLabels,
    scoreVersion,
} from "@/lib/score-labels";


type ScoreBreakdownProps = {
    breakdown: ScoreBreakdownType;
};


type ScoreCategoryConfig = {
    label: string;
    maxScore: number;
};


const SCORE_CONFIG: Record<string, ScoreCategoryConfig> = {
    python: {
        label: "Python",
        maxScore: 8,
    },
    sql: {
        label: "Database",
        maxScore: 8,
    },
    backend: {
        label: "Backend Frameworks",
        maxScore: 7,
    },
    devops: {
        label: "DevOps",
        maxScore: 7,
    },
    ai_domain: {
        label: "AI / ML Domain",
        maxScore: 8,
    },
    data_domain: {
        label: "Data Engineering",
        maxScore: 7,
    },
    backend_domain: {
        label: "Backend Engineering",
        maxScore: 5,
    },
    experience: {
        label: "Work Experience",
        maxScore: 20,
    },
    projects: {
        label: "Projects",
        maxScore: 20,
    },
    engineering_signal: {
        label: "Engineering Practices",
        maxScore: 10,
    },
};


const PROFILE_SCORE_CONFIG: Record<string, ScoreCategoryConfig> = {
    professional_experience: {
        label: "Professional Experience",
        maxScore: 25,
    },
    achievements: {
        label: "Achievements",
        maxScore: 20,
    },
    competencies: {
        label: "Competencies",
        maxScore: 20,
    },
    certifications: {
        label: "Certifications",
        maxScore: 10,
    },
    education: {
        label: "Education",
        maxScore: 10,
    },
    leadership: {
        label: "Leadership",
        maxScore: 10,
    },
    evidence_quality: {
        label: "Evidence Quality",
        maxScore: 5,
    },
};


const SCORE_ORDER = [
    "python",
    "sql",
    "backend",
    "devops",
    "ai_domain",
    "data_domain",
    "backend_domain",
    "experience",
    "projects",
    "engineering_signal",
];


function clampPercent(
    value: number
) {

    return Math.min(
        Math.max(
            value,
            0
        ),
        100
    );

}


function progressColor(
    percent: number
) {

    if (percent >= 80) {
        return "bg-green-500";
    }

    if (percent >= 60) {
        return "bg-blue-500";
    }

    if (percent >= 40) {
        return "bg-yellow-500";
    }

    return "bg-red-500";

}


function badgeColor(
    percent: number
) {

    if (percent >= 80) {
        return "bg-green-100 text-green-700";
    }

    if (percent >= 60) {
        return "bg-blue-100 text-blue-700";
    }

    if (percent >= 40) {
        return "bg-yellow-100 text-yellow-700";
    }

    return "bg-red-100 text-red-700";

}


export default function ScoreBreakdown({
    breakdown,
}: ScoreBreakdownProps) {

    const isProfileV2 = scoreVersion(
        breakdown
    ) === "profile_v2";
    const labels = scoreLabels(breakdown);
    const activeConfig = isProfileV2
        ? PROFILE_SCORE_CONFIG
        : SCORE_CONFIG;
    const scoreOrder = isProfileV2
        ? Object.keys(PROFILE_SCORE_CONFIG)
        : SCORE_ORDER;

    const entries = scoreOrder.map(
        (key) => {

            const config = activeConfig[key];

            const rawValue = Number(
                breakdown?.[key] ?? 0
            );

            const value = Number.isFinite(
                rawValue
            )
                ? Math.max(rawValue, 0)
                : 0;

            const percent = clampPercent(
                Math.round(
                    (
                        value
                        / config.maxScore
                    )
                    * 100
                )
            );

            return {
                key,
                label: config.label,
                value,
                maxScore: config.maxScore,
                percent,
            };

        }
    );


    const totalScore = entries.reduce(
        (total, item) =>
            total + item.value,
        0
    );


    const totalMaximum = entries.reduce(
        (total, item) =>
            total + item.maxScore,
        0
    );


    return (

        <section
            className="
                mt-6
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
                    flex-col
                    gap-4
                    sm:flex-row
                    sm:items-start
                    sm:justify-between
                "
            >

                <div>

                    <h3
                        className="
                            text-xl
                            font-semibold
                            text-gray-900
                        "
                    >
                        {labels.breakdown}
                    </h3>

                    <p
                        className="
                            mt-1
                            text-sm
                            text-gray-500
                        "
                    >
                        Explainable scoring based on resume evidence
                    </p>

                </div>


                <div
                    className="
                        rounded-xl
                        bg-gray-50
                        px-4
                        py-3
                        text-left
                        sm:text-right
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
                        {labels.rule}
                    </p>

                    <p
                        className="
                            mt-1
                            text-2xl
                            font-bold
                            text-gray-900
                        "
                    >
                        {totalScore}/{totalMaximum}
                    </p>

                </div>

            </div>


            <div className="mt-8 space-y-6">

                {entries.map((item) => (

                    <div key={item.key}>

                        <div
                            className="
                                mb-2
                                flex
                                flex-col
                                gap-2
                                sm:flex-row
                                sm:items-center
                                sm:justify-between
                            "
                        >

                            <span
                                className="
                                    font-medium
                                    text-gray-700
                                "
                            >
                                {item.label}
                            </span>


                            <div
                                className="
                                    flex
                                    items-center
                                    gap-2
                                "
                            >

                                <span
                                    className="
                                        text-sm
                                        text-gray-500
                                    "
                                >
                                    {item.value}/{item.maxScore}
                                </span>

                                <span
                                    className={`
                                        min-w-16
                                        rounded-full
                                        px-3
                                        py-1
                                        text-center
                                        text-sm
                                        font-bold
                                        ${badgeColor(
                                        item.percent
                                    )}
                                    `}
                                >
                                    {item.percent}%
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
                            role="progressbar"
                            aria-label={item.label}
                            aria-valuenow={item.percent}
                            aria-valuemin={0}
                            aria-valuemax={100}
                        >

                            <div
                                className={`
                                    h-full
                                    rounded-full
                                    transition-all
                                    duration-500
                                    ${progressColor(
                                    item.percent
                                )}
                                `}
                                style={{
                                    width: `${item.percent}%`,
                                }}
                            />

                        </div>

                    </div>

                ))}

            </div>

        </section>

    );

}
