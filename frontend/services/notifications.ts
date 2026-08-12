import axios from "axios";

import { api } from "./api";
import type {
    Notification,
    NotificationListResponse,
    NotificationReadAllResponse,
} from "@/types/notification";


const NOTIFICATION_ERROR = (
    "Notifications are temporarily unavailable."
);


export async function getNotifications(
    limit = 20
): Promise<NotificationListResponse> {

    try {
        const response = await api.get<NotificationListResponse>(
            "/notifications",
            {
                params: { limit },
            }
        );

        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            throw new Error(NOTIFICATION_ERROR);
        }

        throw new Error(NOTIFICATION_ERROR);
    }
}


export async function markNotificationRead(
    notificationId: number
): Promise<Notification> {

    try {
        const response = await api.patch<Notification>(
            `/notifications/${notificationId}/read`
        );

        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            throw new Error(NOTIFICATION_ERROR);
        }

        throw new Error(NOTIFICATION_ERROR);
    }
}


export async function markAllNotificationsRead(): Promise<
    NotificationReadAllResponse
> {

    try {
        const response = await api.patch<NotificationReadAllResponse>(
            "/notifications/read-all"
        );

        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            throw new Error(NOTIFICATION_ERROR);
        }

        throw new Error(NOTIFICATION_ERROR);
    }
}
