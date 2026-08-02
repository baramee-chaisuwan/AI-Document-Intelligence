import AppLayout from "@/components/layout/AppLayout";

import ChatBox from "@/components/assistant/ChatBox";


export default function AssistantPage() {


    return (

        <AppLayout

            title="AI Assistant"

            description="
            Ask AI about candidates and resumes
            "

        >

            <div className="mt-8">

                <ChatBox />

            </div>


        </AppLayout>

    );

}