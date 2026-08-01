import AppLayout from "@/components/layout/AppLayout";
import CandidateTable from "@/components/candidates/CandidateTable";
import { getCandidates } from "@/services/candidate";

export default async function CandidatesPage() {
    const candidates = await getCandidates();

    return (
        <AppLayout
            title="Candidates"
            description="Manage all candidates in the ATS system"
        >
            <CandidateTable candidates={candidates} />
        </AppLayout>
    );
}