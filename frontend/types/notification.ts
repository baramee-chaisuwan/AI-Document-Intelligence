export type NotificationType = (
    | "RESUME_PROCESSING_COMPLETED"
    | "RESUME_PROCESSING_FAILED"
    | "CANDIDATE_STAGE_CHANGED"
);


export interface Notification {
    id: number;
    type: NotificationType;
    title: string;
    message: string;
    candidate_id: number | null;
    is_read: boolean;
    created_at: string;
}


export interface NotificationListResponse {
    notifications: Notification[];
    unread_count: number;
}


export interface NotificationReadAllResponse {
    marked_read: number;
}
