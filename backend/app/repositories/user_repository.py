from sqlalchemy.orm import Session

from app.database.models import User


def get_user_by_email(
    db: Session,
    email: str
):

    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_user_by_id(
    db: Session,
    user_id: int
):

    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def get_user_by_email_for_update(
    db: Session,
    email: str
):

    return (
        db.query(User)
        .filter(User.email == email)
        .with_for_update()
        .first()
    )


def get_user_by_id_for_update(
    db: Session,
    user_id: int
):

    return (
        db.query(User)
        .filter(User.id == user_id)
        .with_for_update()
        .first()
    )


def create_user(
    db: Session,
    user: User
):

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
