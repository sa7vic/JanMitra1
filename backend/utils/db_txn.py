from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from models.database import db


class DatabaseTransactionError(Exception):
    """Raised when a database transaction cannot be committed."""


def safe_commit(context_message: str = "database transaction") -> None:
    """Commit with rollback and a normalized error for API/service layers."""
    try:
        db.session.commit()
    except (IntegrityError, OperationalError, SQLAlchemyError) as exc:
        db.session.rollback()
        raise DatabaseTransactionError(
            f"{context_message} failed: {exc.__class__.__name__}"
        ) from exc
