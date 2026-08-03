import {
    Bot,
    User,
} from "lucide-react";


type Props = {
    role: "user" | "assistant";
    content: string;
};


export default function Message({
    role,
    content,
}: Props) {

    const isUser =
        role === "user";


    return (

        <div
            className={`
                flex
                gap-3
                ${isUser
                    ? "justify-end"
                    : "justify-start"
                }
            `}
        >

            {!isUser && (

                <div
                    className="
                        flex
                        h-10
                        w-10
                        shrink-0
                        items-center
                        justify-center
                        rounded-full
                        bg-purple-100
                    "
                >
                    <Bot
                        size={20}
                        className="text-purple-600"
                    />
                </div>

            )}


            <div
                className={`
                    max-w-[80%]
                    ${isUser
                        ? "order-first"
                        : ""
                    }
                `}
            >

                <p
                    className={`
                        mb-1
                        text-xs
                        font-medium
                        ${isUser
                            ? "text-right text-gray-500"
                            : "text-gray-500"
                        }
                    `}
                >

                    {
                        isUser
                            ? "You"
                            : "AI Assistant"
                    }

                </p>


                <div
                    className={`
                        rounded-2xl
                        px-4
                        py-3
                        text-sm
                        leading-7
                        break-words
                        whitespace-pre-wrap
                        shadow-sm
                        ${isUser
                            ? "bg-blue-600 text-white"
                            : "border border-gray-200 bg-white text-gray-800"
                        }
                    `}
                >

                    {content}

                </div>

            </div>


            {isUser && (

                <div
                    className="
                        flex
                        h-10
                        w-10
                        shrink-0
                        items-center
                        justify-center
                        rounded-full
                        bg-blue-100
                    "
                >
                    <User
                        size={20}
                        className="text-blue-600"
                    />
                </div>

            )}

        </div>

    );

}