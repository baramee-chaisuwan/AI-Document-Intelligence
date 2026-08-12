import assert from "node:assert/strict";
import test from "node:test";

import {
    markAllNotificationsReadLocally,
    markNotificationReadLocally,
    notificationBadgeLabel,
    notificationCandidatePath,
    notificationPanelState,
} from "../lib/notification-state.ts";
import type { Notification } from "../types/notification.ts";


function notification(
    id: number,
    isRead: boolean,
    candidateId: number | null = null
): Notification {
    return {
        id,
        type: "CANDIDATE_STAGE_CHANGED",
        title: "Candidate stage updated",
        message: "A candidate moved to Interview.",
        candidate_id: candidateId,
        is_read: isRead,
        created_at: "2026-08-13T00:00:00Z",
    };
}


test("bell badge renders bounded unread counts", () => {
    assert.equal(notificationBadgeLabel(0), null);
    assert.equal(notificationBadgeLabel(4), "4");
    assert.equal(notificationBadgeLabel(100), "99+");
});


test("dropdown selects loading, empty, error, and content states", () => {
    assert.equal(notificationPanelState(true, false, 0), "loading");
    assert.equal(notificationPanelState(false, false, 0), "empty");
    assert.equal(notificationPanelState(false, true, 0), "error");
    assert.equal(notificationPanelState(false, true, 2), "notifications");
});


test("mark-read updates only the selected notification and badge", () => {
    const current = [notification(1, false), notification(2, false)];
    const result = markNotificationReadLocally(
        current,
        notification(1, true),
        2,
    );

    assert.deepEqual(
        result.notifications.map((item) => item.is_read),
        [true, false],
    );
    assert.equal(result.unreadCount, 1);
});


test("mark-all reads every notification without mutating inputs", () => {
    const current = [notification(1, false), notification(2, true)];
    const updated = markAllNotificationsReadLocally(current);

    assert.deepEqual(updated.map((item) => item.is_read), [true, true]);
    assert.equal(current[0].is_read, false);
});


test("candidate navigation exists only when candidate ID is present", () => {
    assert.equal(notificationCandidatePath(42), "/candidates/42");
    assert.equal(notificationCandidatePath(null), null);
});
