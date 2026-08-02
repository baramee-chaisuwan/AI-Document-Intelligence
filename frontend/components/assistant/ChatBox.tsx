"use client";


import {
    useState
} from "react";

import {
    askAssistant
} from "@/services/assistant";

import Message from "./Message";


type Chat = {
    role: "user" | "assistant";
    content: string;
};


export default function ChatBox() {


    const [messages, setMessages] =
        useState<Chat[]>([]);


    const [question, setQuestion] =
        useState("");


    const [loading, setLoading] =
        useState(false);



    async function sendMessage() {


        if (!question.trim())
            return;


        const userMessage = {
            role: "user" as const,
            content: question
        };


        setMessages(prev => [
            ...prev,
            userMessage
        ]);


        setQuestion("");

        setLoading(true);



        try {


            const data =
                await askAssistant(
                    userMessage.content
                );


            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: data.answer
                }
            ]);


        }
        catch (error) {

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: "AI error occurred"
                }
            ]);

        }
        finally {

            setLoading(false);

        }


    }



    return (

        <div
            className="
            rounded-xl
            border
            bg-white
            p-6
            shadow-sm
            "
        >


            <div
                className="
                space-y-4
                min-h-[400px]
                "
            >

                {
                    messages.map(
                        (msg, index) => (

                            <Message
                                key={index}
                                {...msg}
                            />

                        )
                    )
                }


                {
                    loading &&
                    <p className="text-sm text-gray-400">
                        AI is thinking...
                    </p>
                }


            </div>


            <div
                className="
                mt-6
                flex
                gap-3
                "
            >

                <input

                    value={question}

                    onChange={
                        e => setQuestion(
                            e.target.value
                        )
                    }

                    onKeyDown={
                        e => {
                            if (e.key === "Enter")
                                sendMessage();
                        }
                    }

                    placeholder="
                    Ask AI about candidates...
                    "

                    className="
                    flex-1
                    rounded-lg
                    border
                    px-4
                    py-2
                    "

                />


                <button

                    onClick={sendMessage}

                    className="
                    rounded-lg
                    bg-blue-600
                    px-5
                    text-white
                    "

                >

                    Ask

                </button>


            </div>


        </div>

    );

}