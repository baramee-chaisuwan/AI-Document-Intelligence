"use client";

import { Bell, CheckCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import {
    useCallback,
    useEffect,
    useRef,
    useState,
} from "react";

import { useAuth } from "@/contexts/AuthContext";
import {
    markAllNotificationsReadLocally,
    markNotificationReadLocally,
    notificationBadgeLabel,
    notificationCandidatePath,
    notificationPanelState,
} from "@/lib/notification-state";
import {
    getNotifications,
    markAllNotificationsRead,
    markNotificationRead,
} from "@/services/notifications";
import type { Notification } from "@/types/notification";


const POLL_INTERVAL_MS = 60_000;


export default function NotificationBell() {

    const { user } = useAuth();
    const router = useRouter();
    const containerRef = useRef<HTMLDivElement>(null);
    const [open, setOpen] = useState(false);
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [markingAll, setMarkingAll] = useState(false);
    const [updatingId, setUpdatingId] = useState<number | null>(null);
    const badgeLabel = notificationBadgeLabel(unreadCount);
    const panelState = notificationPanelState(
        loading,
        error !== null,
        notifications.length
    );


    const loadNotifications = useCallback(async (
        showLoading = false
    ) => {
        if (!user) {
            return;
        }

        if (showLoading) {
            setLoading(true);
        }

        try {
            const result = await getNotifications();
            setNotifications(result.notifications);
            setUnreadCount(result.unread_count);
            setError(null);
        } catch {
            setError("Notifications are temporarily unavailable.");
        } finally {
            if (showLoading) {
                setLoading(false);
            }
        }
    }, [user]);


    useEffect(() => {
        if (!user) {
            return;
        }

        const initialLoad = window.setTimeout(() => {
            void loadNotifications();
        }, 0);
        const polling = window.setInterval(() => {
            void loadNotifications();
        }, POLL_INTERVAL_MS);

        return () => {
            window.clearTimeout(initialLoad);
            window.clearInterval(polling);
        };
    }, [loadNotifications, user]);


    useEffect(() => {
        function closeOnOutsideClick(event: MouseEvent) {
            if (
                containerRef.current
                && !containerRef.current.contains(event.target as Node)
            ) {
                setOpen(false);
            }
        }

        if (open) {
            document.addEventListener("mousedown", closeOnOutsideClick);
        }

        return () => {
            document.removeEventListener("mousedown", closeOnOutsideClick);
        };
    }, [open]);


    function toggleNotifications() {
        const nextOpen = !open;
        setOpen(nextOpen);

        if (nextOpen) {
            void loadNotifications(notifications.length === 0);
        }
    }


    async function selectNotification(notification: Notification) {
        if (updatingId !== null) {
            return;
        }

        setUpdatingId(notification.id);

        try {
            if (!notification.is_read) {
                const updated = await markNotificationRead(notification.id);
                const localUpdate = markNotificationReadLocally(
                    notifications,
                    updated,
                    unreadCount
                );
                setNotifications(localUpdate.notifications);
                setUnreadCount(localUpdate.unreadCount);
            }

            setError(null);
            setOpen(false);

            const candidatePath = notificationCandidatePath(
                notification.candidate_id
            );

            if (candidatePath) {
                router.push(candidatePath);
            }
        } catch {
            setError("The notification could not be updated.");
        } finally {
            setUpdatingId(null);
        }
    }


    async function markAllRead() {
        if (markingAll || unreadCount === 0) {
            return;
        }

        setMarkingAll(true);

        try {
            await markAllNotificationsRead();
            setNotifications((current) => (
                markAllNotificationsReadLocally(current)
            ));
            setUnreadCount(0);
            setError(null);
        } catch {
            setError("Notifications could not be marked as read.");
        } finally {
            setMarkingAll(false);
        }
    }


    return (
        <div ref={containerRef} className="relative">
            <button
                type="button"
                onClick={toggleNotifications}
                className="relative rounded-full p-2 transition hover:bg-gray-100"
                aria-label="Notifications"
                aria-expanded={open}
                aria-haspopup="dialog"
            >
                <Bell size={20} className="text-gray-600" />
                {badgeLabel && (
                    <span className="absolute -right-1 -top-1 flex min-h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-bold text-white">
                        {badgeLabel}
                    </span>
                )}
            </button>

            {open && (
                <div
                    role="dialog"
                    aria-label="Notifications"
                    className="absolute right-0 mt-3 w-[min(24rem,calc(100vw-2rem))] overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl"
                >
                    <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
                        <div>
                            <p className="font-semibold text-slate-900">
                                Notifications
                            </p>
                            <p className="text-xs text-gray-500">
                                {unreadCount} unread
                            </p>
                        </div>
                        <button
                            type="button"
                            onClick={() => void markAllRead()}
                            disabled={markingAll || unreadCount === 0}
                            className="inline-flex items-center gap-1 text-xs font-medium text-blue-600 disabled:cursor-not-allowed disabled:text-gray-400"
                        >
                            <CheckCheck size={15} />
                            {markingAll ? "Updating..." : "Mark all as read"}
                        </button>
                    </div>

                    {error && (
                        <p className="border-b border-red-100 bg-red-50 px-4 py-2 text-xs text-red-700">
                            {error}
                        </p>
                    )}

                    <div className="max-h-96 overflow-y-auto">
                        {panelState === "loading" ? (
                            <p className="px-4 py-8 text-center text-sm text-gray-500">
                                Loading notifications...
                            </p>
                        ) : panelState === "error" ? (
                            <p className="px-4 py-8 text-center text-sm text-red-600">
                                Notifications are temporarily unavailable.
                            </p>
                        ) : panelState === "empty" ? (
                            <p className="px-4 py-8 text-center text-sm text-gray-500">
                                No notifications yet.
                            </p>
                        ) : (
                            notifications.map((notification) => (
                                <button
                                    key={notification.id}
                                    type="button"
                                    onClick={() => void selectNotification(notification)}
                                    disabled={updatingId === notification.id}
                                    className={`block w-full border-b border-gray-100 px-4 py-3 text-left transition last:border-b-0 hover:bg-gray-50 disabled:cursor-wait ${
                                        notification.is_read
                                            ? "bg-white"
                                            : "bg-blue-50/70"
                                    }`}
                                >
                                    <div className="flex gap-3">
                                        <span
                                            className={`mt-2 h-2 w-2 shrink-0 rounded-full ${
                                                notification.is_read
                                                    ? "bg-gray-300"
                                                    : "bg-blue-600"
                                            }`}
                                        />
                                        <div className="min-w-0">
                                            <p className="text-sm font-semibold text-slate-900">
                                                {notification.title}
                                            </p>
                                            <p className="mt-1 text-sm leading-5 text-gray-600">
                                                {notification.message}
                                            </p>
                                            <p className="mt-2 text-xs text-gray-400">
                                                {formatNotificationDate(notification.created_at)}
                                            </p>
                                        </div>
                                    </div>
                                </button>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}


function formatNotificationDate(value: string): string {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "Recently";
    }

    return new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(date);
}
