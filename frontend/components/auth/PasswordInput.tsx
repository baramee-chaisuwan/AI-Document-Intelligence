"use client";

import { useState } from "react";
import type { InputHTMLAttributes } from "react";
import { Eye, EyeOff, LockKeyhole } from "lucide-react";

import {
    passwordInputType,
    passwordToggleLabel,
} from "@/lib/account-ux";


type PasswordInputProps = Omit<
    InputHTMLAttributes<HTMLInputElement>,
    "type"
>;


export default function PasswordInput({
    className = "",
    disabled,
    ...inputProps
}: PasswordInputProps) {
    const [isVisible, setIsVisible] = useState(false);
    const toggleLabel = passwordToggleLabel(isVisible);

    return (
        <div className="relative mt-2">
            <LockKeyhole
                size={18}
                className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
            />
            <input
                {...inputProps}
                type={passwordInputType(isVisible)}
                disabled={disabled}
                className={`w-full rounded-xl border border-gray-300 py-3 pl-10 pr-12 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 ${className}`}
            />
            <button
                type="button"
                onClick={() => setIsVisible((current) => !current)}
                disabled={disabled}
                aria-label={toggleLabel}
                title={toggleLabel}
                className="absolute right-2 top-1/2 inline-flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-lg text-gray-500 transition hover:bg-gray-100 hover:text-gray-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
                {isVisible ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
        </div>
    );
}
