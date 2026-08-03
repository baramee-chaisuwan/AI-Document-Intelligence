"use client";

import {
    FormEvent,
    KeyboardEvent,
    useEffect,
    useRef,
    useState,
} from "react";

import {
    Bot,
    Loader2,
    Send,
    Sparkles,
} from "lucide-react";

import {
    askAssistant,
} from "@/services/assistant";

import Message from "./Message";


const MAX_QUESTION_LENGTH = 2000;


type Chat = {
    id: string;
    role: "user" | "assistant";
    content: string;
};


function createMessageId() {

    return (
        Date.now().toString()
        + "-"
        + Math.random()
            .toString(36)
            .slice(2)
    );

}


export default function ChatBox() {

    const [
        messages,
        setMessages,
    ] = useState<Chat[]>([]);

    const [
        question,
        setQuestion,
    ] = useState("");

    const [
        loading,
        setLoading,
    ] = useState(false);

    const [
        error,
        setError,
    ] = useState("");

    const messagesEndRef = (
        useRef<HTMLDivElement | null>(
            null
        )
    );


    const normalizedQuestion = (
        question.trim()
    );

    const canSend = (
        normalizedQuestion.length > 0
        && normalizedQuestion.length
        <= MAX_QUESTION_LENGTH
        && !loading
    );


    useEffect(() => {

        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
        });

    }, [
        messages,
        loading,
    ]);


    async function sendMessage() {

        if (!canSend) {
            return;
        }


        const userMessage: Chat = {
            id: createMessageId(),
            role: "user",
            content: normalizedQuestion,
        };


        setMessages((previousMessages) => [
            ...previousMessages,
            userMessage,
        ]);

        setQuestion("");
        setError("");
        setLoading(true);


        try {

            const data = await askAssistant(
                userMessage.content
            );


            const assistantMessage: Chat = {
                id: createMessageId(),
                role: "assistant",
                content: (
                    data.answer?.trim()
                    || (
                        "I couldn't find that information "
                        + "in the resume database."
                    )
                ),
            };


            setMessages((previousMessages) => [
                ...previousMessages,
                assistantMessage,
            ]);

        } catch (error) {

            const errorMessage = (
                error instanceof Error
                    ? error.message
                    : "The AI assistant is unavailable."
            );


            setError(
                errorMessage
            );


            setMessages((previousMessages) => [
                ...previousMessages,
                {
                    id: createMessageId(),
                    role: "assistant",
                    content: (
                        "Sorry, I couldn't process "
                        + "that question right now."
                    ),
                },
            ]);

        } finally {

            setLoading(false);

        }

    }


    function handleSubmit(
        event: FormEvent<HTMLFormElement>
    ) {

        event.preventDefault();

        sendMessage();

    }


    function handleKeyDown(
        event: KeyboardEvent<HTMLTextAreaElement>
    ) {

        if (
            event.key === "Enter"
            && !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }


    return (

        <section
            className="
                overflow-hidden
                rounded-2xl
                border
                border-gray-200
                bg-white
                shadow-sm
            "
        >

            <div
                className="
                    flex
                    items-center
                    gap-3
                    border-b
                    border-gray-100
                    px-5
                    py-4
                    sm:px-6
                "
            >

                <div
                    className="
                        flex
                        h-11
                        w-11
                        items-center
                        justify-center
                        rounded-xl
                        bg-purple-50
                    "
                >
                    <Bot
                        size={23}
                        className="text-purple-600"
                    />
                </div>


                <div>

                    <h2
                        className="
                            font-semibold
                            text-gray-900
                        "
                    >
                        AI HR Assistant
                    </h2>

                    <p
                        className="
                            mt-0.5
                            text-xs
                            text-gray-500
                        "
                    >
                        Ask questions about indexed candidates
                    </p>

                </div>

            </div>


            <div
                className="
                    min-h-[420px]
                    max-h-[620px]
                    overflow-y-auto
                    bg-gray-50
                    px-4
                    py-5
                    sm:px-6
                "
                aria-live="polite"
            >

                {messages.length === 0 ? (

                    <div
                        className="
                            flex
                            min-h-[360px]
                            flex-col
                            items-center
                            justify-center
                            text-center
                        "
                    >

                        <div
                            className="
                                flex
                                h-16
                                w-16
                                items-center
                                justify-center
                                rounded-2xl
                                bg-white
                                shadow-sm
                            "
                        >
                            <Sparkles
                                size={30}
                                className="text-purple-600"
                            />
                        </div>


                        <h3
                            className="
                                mt-5
                                text-lg
                                font-semibold
                                text-gray-900
                            "
                        >
                            Ask about your candidates
                        </h3>

                        <p
                            className="
                                mt-2
                                max-w-md
                                text-sm
                                leading-6
                                text-gray-500
                            "
                        >
                            Try asking who has Docker experience,
                            which candidate knows FastAPI, or who
                            best matches a specific technical skill.
                        </p>

                    </div>

                ) : (

                    <div className="space-y-4">

                        {messages.map((message) => (

                            <Message
                                key={message.id}
                                role={message.role}
                                content={message.content}
                            />

                        ))}


                        {loading && (

                            <div
                                className="
                                    flex
                                    items-center
                                    gap-2
                                    text-sm
                                    text-gray-500
                                "
                            >
                                <Loader2
                                    size={17}
                                    className="animate-spin"
                                />

                                AI is reviewing candidate evidence...
                            </div>

                        )}

                    </div>

                )}


                <div ref={messagesEndRef} />

            </div>


            {error && (

                <div
                    role="alert"
                    className="
                        border-t
                        border-red-100
                        bg-red-50
                        px-5
                        py-3
                        text-sm
                        text-red-700
                        sm:px-6
                    "
                >
                    {error}
                </div>

            )}


            <form
                onSubmit={handleSubmit}
                className="
                    border-t
                    border-gray-100
                    bg-white
                    p-4
                    sm:p-5
                "
            >

                <div
                    className="
                        flex
                        items-end
                        gap-3
                    "
                >

                    <div className="min-w-0 flex-1">

                        <label
                            htmlFor="assistant-question"
                            className="sr-only"
                        >
                            Ask the AI assistant
                        </label>


                        <textarea
                            id="assistant-question"
                            value={question}
                            disabled={loading}
                            maxLength={
                                MAX_QUESTION_LENGTH
                            }
                            onChange={(event) => {

                                setQuestion(
                                    event.target.value
                                );

                                setError("");

                            }}
                            onKeyDown={
                                handleKeyDown
                            }
                            rows={2}
                            placeholder={
                                "Ask AI about candidates..."
                            }
                            className="
                                max-h-40
                                min-h-12
                                w-full
                                resize-y
                                rounded-xl
                                border
                                border-gray-300
                                px-4
                                py-3
                                text-sm
                                text-gray-900
                                outline-none
                                transition
                                placeholder:text-gray-400
                                focus:border-blue-500
                                focus:ring-4
                                focus:ring-blue-100
                                disabled:cursor-not-allowed
                                disabled:bg-gray-50
                            "
                        />


                        <div
                            className="
                                mt-1
                                flex
                                justify-between
                                gap-3
                                text-xs
                                text-gray-400
                            "
                        >
                            <span>
                                Enter to send · Shift+Enter for a new line
                            </span>

                            <span>
                                {question.length}/{MAX_QUESTION_LENGTH}
                            </span>
                        </div>

                    </div>


                    <button
                        type="submit"
                        disabled={
                            !canSend
                        }
                        aria-label="Send question"
                        className="
                            inline-flex
                            h-12
                            shrink-0
                            items-center
                            justify-center
                            gap-2
                            rounded-xl
                            bg-blue-600
                            px-5
                            text-sm
                            font-medium
                            text-white
                            transition-colors
                            hover:bg-blue-700
                            disabled:cursor-not-allowed
                            disabled:opacity-50
                        "
                    >

                        {loading ? (

                            <Loader2
                                size={18}
                                className="animate-spin"
                            />

                        ) : (

                            <Send size={18} />

                        )}

                        <span className="hidden sm:inline">
                            Send
                        </span>

                    </button>

                </div>

            </form>

        </section>

    );

}