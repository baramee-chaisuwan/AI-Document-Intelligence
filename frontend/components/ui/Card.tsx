type CardProps = {
    title: string;
    value: string | number;
};

export default function Card({
    title,
    value,
}: CardProps) {

    return (

        <div
            className="
                rounded-2xl
                border
                border-gray-200
                bg-white
                p-6
                shadow-sm
                transition-all
                duration-200
                hover:-translate-y-1
                hover:shadow-lg
            "
        >

            <p
                className="
                    text-sm
                    font-medium
                    uppercase
                    tracking-wide
                    text-gray-500
                "
            >
                {title}
            </p>

            <h2
                className="
                    mt-4
                    break-words
                    text-4xl
                    font-bold
                    text-gray-900
                "
            >
                {value}
            </h2>

        </div>

    );

}