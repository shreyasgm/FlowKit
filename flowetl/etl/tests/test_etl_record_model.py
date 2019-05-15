import pytest
import pendulum
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from etl.model import Base, ETLRecord


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:")
    engine.execute(f"ATTACH DATABASE ':memory:' AS etl;")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_can_set_state(session):
    """
    Make sure we can add a row to the DB and the content
    we expect is in the DB afterwards.
    """
    file_data = {
        "file_name": "bob.csv",
        "cdr_type": "calls",
        "cdr_date": pendulum.parse("2016-01-01").date(),
        "state": "ingest",
    }

    now = pendulum.parse("2016-01-01")
    with patch("pendulum.utcnow", lambda: now):
        ETLRecord.set_state(
            file_name=file_data["file_name"],
            cdr_type=file_data["cdr_type"],
            cdr_date=file_data["cdr_date"],
            state=file_data["state"],
            session=session,
        )

    rows = session.query(ETLRecord).all()
    assert len(rows) == 1

    row = rows[0]
    assert row.file_name == file_data["file_name"]
    assert row.cdr_type == file_data["cdr_type"]
    assert row.cdr_date == file_data["cdr_date"]
    assert row.state == file_data["state"]
    assert row.timestamp == now


def test_exception_raised_with_invalid_state(session):
    """
    Test that we get an exception raised when we try
    to add a new row with an invalid state.
    """
    file_data = {
        "file_name": "bob.csv",
        "cdr_type": "calls",
        "cdr_date": pendulum.parse("2016-01-01").date(),
        "state": "hammer_time",
    }
    with pytest.raises(Exception):
        ETLRecord.set_state(
            file_name=file_data["file_name"],
            cdr_type=file_data["cdr_type"],
            cdr_date=file_data["cdr_date"],
            state=file_data["state"],
            session=session,
        )


def test_exception_raised_with_invalid_cdr_type(session):
    """
    Test that we get an exception raised when we try
    to add a new row with an invalid cdr_type.
    """
    file_data = {
        "file_name": "bob.csv",
        "cdr_type": "spaghetti",
        "cdr_date": pendulum.parse("2016-01-01").date(),
        "state": "ingest",
    }
    with pytest.raises(Exception):
        ETLRecord.set_state(
            file_name=file_data["file_name"],
            cdr_type=file_data["cdr_type"],
            cdr_date=file_data["cdr_date"],
            state=file_data["state"],
            session=session,
        )
