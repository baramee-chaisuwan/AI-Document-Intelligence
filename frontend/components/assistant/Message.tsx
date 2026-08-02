type Props = {
    role: "user" | "assistant";
    content: string;
};


export default function Message({
    role,
    content,
}: Props) {

    return (

        <div
            className={`
                flex
                ${role === "user"
                    ? "justify-end"
                    : "justify-start"
                }
            `}
        >

            <div
                className={`
                    max-w-xl
                    rounded-xl
                    px-4
                    py-3
                    text-sm
                    ${role === "user"
                        ? "bg-blue-600 text-white"
                        : "bg-gray-100 text-gray-800"
                    }
                `}
            >

                {content}

            </div>

        </div>

    );

}