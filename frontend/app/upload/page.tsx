import AppLayout from "@/components/layout/AppLayout";

export default function UploadPage() {
    return (
        <AppLayout
            title="Upload Resume"
            description="Upload candidate resumes into the ATS"
        >
            <div className="mt-6 rounded-lg bg-white p-6 shadow">
                <h2 className="text-xl font-bold">
                    Upload Resume
                </h2>

                <p className="mt-2 text-gray-500">
                    Upload candidate resumes into the ATS system.
                </p>
            </div>
        </AppLayout>
    );
}