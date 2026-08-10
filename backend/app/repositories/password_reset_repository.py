from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import PasswordResetToken


def count_recent_requests(
    db: Session,
    user_id: int,
    window_start: datetime
) -> int:

    return (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.created_at
            >= window_start
        )
        .count()
    )


def invalidate_active_tokens(
    db: Session,
    user_id: int,
    invalidated_at: datetime
) -> None:

    (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.consumed_at.is_(None),
            PasswordResetToken.invalidated_at.is_(None)
        )
        .update(
            {
                PasswordResetToken.invalidated_at:
                    invalidated_at
            },
            synchronize_session="fetch"
        )
    )


def create_token(
    db: Session,
    token: PasswordResetToken
) -> PasswordResetToken:

    db.add(token)
    db.flush()

    return token


def get_current_token_for_update(
    db: Session,
    user_id: int
):

    return (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.consumed_at.is_(None),
            PasswordResetToken.invalidated_at.is_(None)
        )
        .order_by(
            PasswordResetToken.created_at.desc(),
            PasswordResetToken.id.desc()
        )
        .with_for_update()
        .first()
    )


def get_token_by_id_for_update(
    db: Session,
    token_id: int
):

    return (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.id == token_id)
        .with_for_update()
        .first()
    )
