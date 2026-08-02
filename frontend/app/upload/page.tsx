import AppLayout from "@/components/layout/AppLayout";
import UploadForm from "@/components/upload/UploadForm";

export default function UploadPage() {
    return (
        <AppLayout
            title="Upload Resume"
            description="Upload candidate resumes into the ATS"
        >
            <UploadForm />
        </AppLayout>
    );
}