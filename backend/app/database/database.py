import logging
import os
import time

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)


load_dotenv()


logger = logging.getLogger(__name__)


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

DATABASE_MAX_RETRIES = int(
    os.getenv(
        "DATABASE_MAX_RETRIES",
        "10"
    )
)

DATABASE_RETRY_DELAY_SECONDS = int(
    os.getenv(
        "DATABASE_RETRY_DELAY_SECONDS",
        "3"
    )
)

DATABASE_POOL_SIZE = int(
    os.getenv(
        "DATABASE_POOL_SIZE",
        "5"
    )
)

DATABASE_MAX_OVERFLOW = int(
    os.getenv(
        "DATABASE_MAX_OVERFLOW",
        "10"
    )
)


if not DATABASE_URL:

    raise RuntimeError(
        "DATABASE_URL is missing"
    )


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=DATABASE_POOL_SIZE,
    max_overflow=DATABASE_MAX_OVERFLOW,
    pool_recycle=1800
)


def check_database_connection():

    last_error = None


    for attempt in range(
        1,
        DATABASE_MAX_RETRIES + 1
    ):

        try:

            with engine.connect() as connection:

                connection.execute(
                    text("SELECT 1")
                )


            logger.info(
                "Database connection established"
            )

            return


        except Exception as error:

            last_error = error


            logger.warning(
                "Database connection attempt "
                "%s/%s failed: %s",
                attempt,
                DATABASE_MAX_RETRIES,
                error
            )


            if (
                attempt
                < DATABASE_MAX_RETRIES
            ):

                time.sleep(
                    DATABASE_RETRY_DELAY_SECONDS
                )


    raise RuntimeError(
        "Database could not be reached "
        f"after {DATABASE_MAX_RETRIES} attempts"
    ) from last_error


if os.getenv(
    "TESTING",
    "false"
).lower() != "true":

    check_database_connection()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)


Base = declarative_base()


def get_db():

    db = SessionLocal()


    try:

        yield db


    except Exception:

        db.rollback()

        raise


    finally:

        db.close()