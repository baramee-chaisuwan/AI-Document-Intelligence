"use client";

import Link from "next/link";
import {
    AlertCircle,
    BriefcaseBusiness,
    CheckCircle2,
    ExternalLink,
    Loader2,
    Plus,
    RefreshCw,
    Search,
} from "lucide-react";
import {
    useCallback,
    useEffect,
    useState,
} from "react";

import AppLayout from "@/components/layout/AppLayout";
import {
    createJob,
    getJobs,
    matchJobCandidates,
} from "@/services/jobs";
import type {
    Job,
    JobMatchResult,
} from "@/types/job";


const MAX_TITLE_LENGTH = 255;


const dateFormatter = new Intl.DateTimeFormat(
    "en",
    {
        dateStyle: "medium",
        timeStyle: "short",
    }
);


function formatDate(value: string): string {

    const date = new Date(value);

    return Number.isNaN(date.getTime())
        ? "Unknown date"
        : dateFormatter.format(date);
}


function scoreStyle(score: number): string {

    if (score >= 80) {
        return "bg-green-100 text-green-700";
    }

    if (score >= 60) {
        return "bg-blue-100 text-blue-700";
    }

    if (score >= 40) {
        return "bg-amber-100 text-amber-700";
    }

    return "bg-red-100 text-red-700";
}


export default function JobsPage() {

    const [jobs, setJobs] = useState<Job[]>([]);
    const [jobsLoading, setJobsLoading] = useState(true);
    const [loadError, setLoadError] = useState("");

    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [creating, setCreating] = useState(false);
    const [createError, setCreateError] = useState("");
    const [createSuccess, setCreateSuccess] = useState("");

    const [matchingJobId, setMatchingJobId] = (
        useState<number | null>(null)
    );
    const [matchedJob, setMatchedJob] = useState<Job | null>(null);
    const [matches, setMatches] = (
        useState<JobMatchResult[] | null>(null)
    );
    const [matchError, setMatchError] = useState("");


    const loadJobs = useCallback(async () => {

        try {
            setJobsLoading(true);
            setLoadError("");
            const data = await getJobs();
            setJobs(data);
        } catch (error) {
            setLoadError(
                error instanceof Error
                    ? error.message
                    : "Could not load jobs."
            );
        } finally {
            setJobsLoading(false);
        }
    }, []);


    useEffect(() => {
        const loadingTimer = window.setTimeout(
            () => {
                void loadJobs();
            },
            0
        );

        return () => {
            window.clearTimeout(loadingTimer);
        };
    }, [loadJobs]);


    async function handleCreateJob(
        event: React.FormEvent<HTMLFormElement>
    ) {
        event.preventDefault();

        const normalizedTitle = title.trim();
        const normalizedDescription = description.trim();

        if (!normalizedTitle || !normalizedDescription) {
            setCreateError(
                "Title and description are required."
            );
            return;
        }

        if (normalizedTitle.length > MAX_TITLE_LENGTH) {
            setCreateError(
                `Title must not exceed ${MAX_TITLE_LENGTH} characters.`
            );
            return;
        }

        try {
            setCreating(true);
            setCreateError("");
            setCreateSuccess("");

            const job = await createJob({
                title: normalizedTitle,
                description: normalizedDescription,
            });

            setTitle("");
            setDescription("");
            setCreateSuccess(
                `${job.title} was created successfully.`
            );
            await loadJobs();
        } catch (error) {
            setCreateError(
                error instanceof Error
                    ? error.message
                    : "Could not create the job."
            );
        } finally {
            setCreating(false);
        }
    }


    async function handleMatch(job: Job) {

        try {
            setMatchingJobId(job.id);
            setMatchedJob(job);
            setMatches(null);
            setMatchError("");

            const results = await matchJobCandidates(job.id);
            setMatches(results);
        } catch (error) {
            setMatchError(
                error instanceof Error
                    ? error.message
                    : "Could not match candidates."
            );
        } finally {
            setMatchingJobId(null);
        }
    }


    const canCreate = (
        title.trim().length > 0
        && title.trim().length <= MAX_TITLE_LENGTH
        && description.trim().length > 0
    );


    return (
        <AppLayout
            title="Job Management"
            description="Create job descriptions and rank indexed candidates using explainable matching scores"
        >
            <div className="grid gap-6 xl:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
                <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
                    <div className="flex items-start gap-4">
                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                            <Plus size={22} />
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold text-gray-900">
                                Create Job
                            </h2>
                            <p className="mt-1 text-sm leading-6 text-gray-500">
                                Requirements and the matching vector are prepared automatically after submission.
                            </p>
                        </div>
                    </div>

                    <form onSubmit={handleCreateJob} className="mt-7 space-y-5">
                        <div>
                            <label htmlFor="job-title" className="text-sm font-medium text-gray-700">
                                Job title
                            </label>
                            <input
                                id="job-title"
                                value={title}
                                maxLength={MAX_TITLE_LENGTH}
                                disabled={creating}
                                onChange={(event) => {
                                    setTitle(event.target.value);
                                    setCreateError("");
                                    setCreateSuccess("");
                                }}
                                placeholder="Senior Backend Engineer"
                                className="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 disabled:bg-gray-50"
                            />
                            <p className="mt-1 text-right text-xs text-gray-400">
                                {title.length}/{MAX_TITLE_LENGTH}
                            </p>
                        </div>

                        <div>
                            <label htmlFor="job-description" className="text-sm font-medium text-gray-700">
                                Description
                            </label>
                            <textarea
                                id="job-description"
                                value={description}
                                disabled={creating}
                                rows={10}
                                onChange={(event) => {
                                    setDescription(event.target.value);
                                    setCreateError("");
                                    setCreateSuccess("");
                                }}
                                placeholder="Describe required skills, preferred experience, and responsibilities."
                                className="mt-2 w-full resize-y rounded-xl border border-gray-300 p-4 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 disabled:bg-gray-50"
                            />
                        </div>

                        {createError && (
                            <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                                {createError}
                            </div>
                        )}

                        {createSuccess && (
                            <div role="status" className="rounded-xl border border-green-200 bg-green-50 p-4 text-sm text-green-700">
                                {createSuccess}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={creating || !canCreate}
                            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {creating ? (
                                <>
                                    <Loader2 size={18} className="animate-spin" />
                                    Creating Job...
                                </>
                            ) : (
                                <>
                                    <Plus size={18} />
                                    Create Job
                                </>
                            )}
                        </button>
                    </form>
                </section>

                <section>
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                            <h2 className="text-xl font-semibold text-gray-900">
                                Existing Jobs
                            </h2>
                            <p className="mt-1 text-sm text-gray-500">
                                {jobs.length} {jobs.length === 1 ? "job" : "jobs"} available
                            </p>
                        </div>
                        <button
                            type="button"
                            onClick={() => void loadJobs()}
                            disabled={jobsLoading}
                            className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50"
                        >
                            <RefreshCw size={16} className={jobsLoading ? "animate-spin" : ""} />
                            Refresh
                        </button>
                    </div>

                    {loadError && (
                        <div role="alert" className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                            {loadError}
                        </div>
                    )}

                    {jobsLoading && jobs.length === 0 ? (
                        <div role="status" className="mt-4 rounded-2xl border border-gray-200 bg-white p-8 text-center text-sm text-gray-500 shadow-sm">
                            Loading jobs...
                        </div>
                    ) : jobs.length === 0 ? (
                        <div className="mt-4 rounded-2xl border border-dashed border-gray-300 bg-white p-10 text-center shadow-sm">
                            <BriefcaseBusiness size={34} className="mx-auto text-gray-400" />
                            <h3 className="mt-4 font-semibold text-gray-900">
                                No jobs yet
                            </h3>
                            <p className="mt-2 text-sm text-gray-500">
                                Create the first job to begin candidate matching.
                            </p>
                        </div>
                    ) : (
                        <div className="mt-4 space-y-4">
                            {jobs.map((job) => (
                                <JobCard
                                    key={job.id}
                                    job={job}
                                    selected={matchedJob?.id === job.id}
                                    matching={matchingJobId === job.id}
                                    matchingDisabled={matchingJobId !== null}
                                    onMatch={() => void handleMatch(job)}
                                />
                            ))}
                        </div>
                    )}
                </section>
            </div>

            {(matchedJob || matchError) && (
                <section className="mt-8 rounded-2xl border border-gray-200 bg-white shadow-sm">
                    <div className="border-b border-gray-200 p-6 sm:p-8">
                        <div className="flex items-start gap-3">
                            <Search size={22} className="mt-0.5 shrink-0 text-blue-600" />
                            <div>
                                <h2 className="text-xl font-semibold text-gray-900">
                                    Candidate Ranking
                                </h2>
                                {matchedJob && (
                                    <p className="mt-1 text-sm text-gray-500">
                                        Results for {matchedJob.title}; scores are returned by the backend matching service.
                                    </p>
                                )}
                            </div>
                        </div>
                    </div>

                    {matchError ? (
                        <div role="alert" className="m-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 sm:m-8">
                            {matchError}
                        </div>
                    ) : matchingJobId !== null ? (
                        <div role="status" className="flex items-center justify-center gap-3 p-10 text-sm text-gray-500">
                            <Loader2 size={19} className="animate-spin" />
                            Comparing indexed resume evidence...
                        </div>
                    ) : matches?.length === 0 ? (
                        <div className="p-10 text-center">
                            <AlertCircle size={34} className="mx-auto text-gray-400" />
                            <h3 className="mt-4 font-semibold text-gray-900">
                                No rankable candidates
                            </h3>
                            <p className="mt-2 text-sm text-gray-500">
                                No candidates currently have usable indexed resume chunks for this job.
                            </p>
                        </div>
                    ) : matches ? (
                        <MatchTable matches={matches} />
                    ) : null}
                </section>
            )}
        </AppLayout>
    );
}


function JobCard({
    job,
    selected,
    matching,
    matchingDisabled,
    onMatch,
}: {
    job: Job;
    selected: boolean;
    matching: boolean;
    matchingDisabled: boolean;
    onMatch: () => void;
}) {

    const requirements = job.extracted_requirements;

    return (
        <article className={`rounded-2xl border bg-white p-5 shadow-sm transition ${selected ? "border-blue-300 ring-2 ring-blue-100" : "border-gray-200"}`}>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                    <h3 className="truncate text-lg font-semibold text-gray-900" title={job.title}>
                        {job.title}
                    </h3>
                    <p className="mt-1 text-xs text-gray-500">
                        Created {formatDate(job.created_at)} | User #{job.created_by}
                    </p>
                </div>
                <button
                    type="button"
                    onClick={onMatch}
                    disabled={matchingDisabled}
                    className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    {matching ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
                    {matching ? "Matching..." : "Match Candidates"}
                </button>
            </div>

            <p className="mt-4 line-clamp-3 whitespace-pre-line text-sm leading-6 text-gray-600">
                {job.description}
            </p>

            <div className="mt-5 grid gap-4 md:grid-cols-2">
                <RequirementGroup title="Required skills" items={requirements.required_skills} variant="required" />
                <RequirementGroup title="Preferred skills" items={requirements.preferred_skills} variant="preferred" />
                <RequirementGroup title="Experience" items={requirements.experience_requirements} />
                <RequirementGroup title="Responsibilities" items={requirements.responsibilities} />
            </div>
        </article>
    );
}


function RequirementGroup({
    title,
    items,
    variant = "neutral",
}: {
    title: string;
    items: string[];
    variant?: "required" | "preferred" | "neutral";
}) {

    const badgeClass = variant === "required"
        ? "bg-blue-50 text-blue-700"
        : variant === "preferred"
            ? "bg-purple-50 text-purple-700"
            : "bg-gray-100 text-gray-700";

    return (
        <div>
            <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                {title}
            </h4>
            {items.length === 0 ? (
                <p className="mt-2 text-sm text-gray-400">None specified</p>
            ) : (
                <div className="mt-2 flex flex-wrap gap-2">
                    {items.map((item) => (
                        <span key={item} className={`rounded-full px-2.5 py-1 text-xs font-medium ${badgeClass}`}>
                            {item}
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
}


function MatchTable({
    matches,
}: {
    matches: JobMatchResult[];
}) {

    return (
        <div className="overflow-x-auto">
            <table className="min-w-[1100px] w-full text-left">
                <thead className="bg-gray-50 text-xs uppercase tracking-wide text-gray-500">
                    <tr>
                        <th className="px-5 py-4">Rank</th>
                        <th className="px-5 py-4">Candidate</th>
                        <th className="px-5 py-4">Match</th>
                        <th className="px-5 py-4">Semantic</th>
                        <th className="px-5 py-4">Required</th>
                        <th className="px-5 py-4">Preferred</th>
                        <th className="px-5 py-4">Skill evidence</th>
                    </tr>
                </thead>
                <tbody>
                    {matches.map((match, index) => (
                        <tr key={match.candidate_id} className="border-t border-gray-100 align-top hover:bg-gray-50">
                            <td className="px-5 py-5 font-semibold text-gray-700">
                                #{index + 1}
                            </td>
                            <td className="px-5 py-5">
                                <Link href={`/candidates/${match.candidate_id}`} className="inline-flex items-center gap-1.5 font-semibold text-blue-600 hover:text-blue-700">
                                    {match.candidate_name}
                                    <ExternalLink size={14} />
                                </Link>
                                <p className="mt-1 text-xs text-gray-500">Candidate #{match.candidate_id}</p>
                            </td>
                            <ScoreCell score={match.match_score} emphasize />
                            <ScoreCell score={match.score_breakdown.semantic_score} />
                            <ScoreCell score={match.score_breakdown.required_skill_score} />
                            <ScoreCell score={match.score_breakdown.preferred_skill_score} />
                            <td className="max-w-md px-5 py-5">
                                <SkillList title="Matched" items={match.matched_skills} matched />
                                <div className="mt-3">
                                    <SkillList title="Missing required" items={match.missing_skills} matched={false} />
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}


function ScoreCell({
    score,
    emphasize = false,
}: {
    score: number;
    emphasize?: boolean;
}) {

    return (
        <td className="px-5 py-5">
            <span className={`inline-flex min-w-16 justify-center rounded-full px-3 py-1.5 font-semibold ${emphasize ? "text-base" : "text-sm"} ${scoreStyle(score)}`}>
                {score}%
            </span>
        </td>
    );
}


function SkillList({
    title,
    items,
    matched,
}: {
    title: string;
    items: string[];
    matched: boolean;
}) {

    return (
        <div>
            <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-gray-500">
                {matched ? <CheckCircle2 size={14} className="text-green-600" /> : <AlertCircle size={14} className="text-red-500" />}
                {title}
            </p>
            {items.length === 0 ? (
                <p className="mt-1.5 text-xs text-gray-400">None</p>
            ) : (
                <div className="mt-2 flex flex-wrap gap-1.5">
                    {items.map((item) => (
                        <span key={item} className={`rounded-full px-2.5 py-1 text-xs font-medium ${matched ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
                            {item}
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
}
