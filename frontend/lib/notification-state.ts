import type { Notification } from "@/types/notification";


export type NotificationPanelState = (
    | "loading"
    | "error"
    | "empty"
    | "notifications"
);


export function notificationBadgeLabel(
    unreadCount: number
): string | null {
    if (unreadCount <= 0) {
        return null;
    }

    return unreadCount > 99 ? "99+" : String(unreadCount);
}


export function notificationPanelState(
    loading: boolean,
    hasError: boolean,
    notificationCount: number
): NotificationPanelState {
    if (loading) {
        return "loading";
    }

    if (hasError && notificationCount === 0) {
        return "error";
    }

    if (notificationCount === 0) {
        return "empty";
    }

    return "notifications";
}


export function markNotificationReadLocally(
    notifications: Notification[],
    updated: Notification,
    unreadCount: number
): {
    notifications: Notification[];
    unreadCount: number;
} {
    const wasUnread = notifications.some(
        (item) => item.id === updated.id && !item.is_read
    );

    return {
        notifications: notifications.map((item) => (
            item.id === updated.id ? updated : item
        )),
        unreadCount: wasUnread
            ? Math.max(0, unreadCount - 1)
            : unreadCount,
    };
}


export function markAllNotificationsReadLocally(
    notifications: Notification[]
): Notification[] {
    return notifications.map((item) => ({
        ...item,
        is_read: true,
    }));
}


export function notificationCandidatePath(
    candidateId: number | null
): string | null {
    return candidateId === null
        ? null
        : `/candidates/${candidateId}`;
}
