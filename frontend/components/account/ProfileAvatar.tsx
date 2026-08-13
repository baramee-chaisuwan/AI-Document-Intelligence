"use client";

import { useEffect, useState } from "react";

import { accountInitials } from "@/lib/account-ux";
import { getProfilePhoto } from "@/services/auth";
import type { AuthUser } from "@/types/auth";


type ProfileAvatarProps = {
    user: AuthUser;
    className?: string;
    textClassName?: string;
};


export default function ProfileAvatar({
    user,
    className = "h-10 w-10",
    textClassName = "text-sm",
}: ProfileAvatarProps) {
    const [photoUrl, setPhotoUrl] = useState<string | null>(null);

    useEffect(() => {
        let active = true;
        let objectUrl: string | null = null;

        if (!user.has_profile_image) {
            return () => undefined;
        }

        void getProfilePhoto()
            .then((blob) => {
                if (!active) return;
                objectUrl = URL.createObjectURL(blob);
                setPhotoUrl(objectUrl);
            })
            .catch(() => {
                if (active) setPhotoUrl(null);
            });

        return () => {
            active = false;
            if (objectUrl) URL.revokeObjectURL(objectUrl);
        };
    }, [user.has_profile_image, user.updated_at]);

    return (
        <div
            className={`flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-blue-600 font-bold text-white ${className} ${textClassName}`}
        >
            {user.has_profile_image && photoUrl ? (
                // Blob URLs are created from the authenticated API response.
                // eslint-disable-next-line @next/next/no-img-element
                <img
                    src={photoUrl}
                    alt={`${user.full_name} profile`}
                    className="h-full w-full object-cover"
                />
            ) : accountInitials(user.full_name)}
        </div>
    );
}
