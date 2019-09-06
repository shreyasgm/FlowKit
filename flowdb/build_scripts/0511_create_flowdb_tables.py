#!/usr/bin/env python3

import os
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Text,
    Boolean,
    TIMESTAMP,
    Numeric,
)
from sqlalchemy.schema import CreateSchema

postgres_user = os.environ["POSTGRES_USER"]
postgres_password = os.environ["POSTGRES_PASSWORD"]

conn_str = "postgresql://{}:{}@localhost:5432/flowdb_revised_schema".format(
    postgres_user, postgres_password
)
engine = create_engine(conn_str)

if not engine.dialect.has_schema(engine, "events"):
    engine.execute(CreateSchema("events"))

metadata = MetaData()

events_calls = Table(
    "calls",
    metadata,
    Column("id", Text()),
    Column("outgoing", Boolean()),
    Column("datetime", TIMESTAMP(timezone=True), nullable=False),
    Column("duration", Numeric()),
    Column("network", Text()),
    Column("msisdn", Text(), nullable=False),
    Column("msisdn_counterpart", Text()),
    Column("location_id", Text()),
    Column("imsi", Text()),
    Column("imei", Text()),
    Column("tac", Numeric(8)),
    Column("operator_code", Numeric()),
    Column("country_code", Numeric()),
    schema="events",
)

metadata.create_all(bind=engine)
