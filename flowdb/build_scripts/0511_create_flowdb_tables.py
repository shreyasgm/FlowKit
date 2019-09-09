#!/usr/bin/env python3

import os
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    ForeignKey,
    Boolean,
    Integer,
    Text,
    TIMESTAMP,
    Numeric,
    func,
)
from geoalchemy2 import Geometry
from sqlalchemy.schema import CreateSchema
from sqlalchemy.dialects.postgresql import UUID

postgres_user = os.environ["POSTGRES_USER"]
postgres_password = os.environ["POSTGRES_PASSWORD"]

conn_str = "postgresql://{}:{}@localhost:5432/flowdb_revised_schema".format(
    postgres_user, postgres_password
)
engine = create_engine(conn_str)


def create_schema_if_not_exists(schema_name):
    if not engine.dialect.has_schema(engine, schema_name):
        engine.execute(CreateSchema(schema_name))


metadata = MetaData()

cell_locations = Table(
    "cells",
    metadata,
    Column(
        "id",
        Integer,
        primary_key=True,
        comment=(
            "FlowDB-internal cell identifier. Note: a new id (and new table row) is created "
            "if any cell attributes change, even if the `mno_cell_code` remains the same."
        ),
    ),
    Column(
        "mno_cell_code",
        Text(),
        nullable=False,
        comment="Cell identifier provided by the MNO.",
    ),
    Column(
        "valid_from",
        TIMESTAMP(timezone=True),
        nullable=False,
        comment="First date from which the cell is valid.",
    ),
    Column(
        "valid_to",
        TIMESTAMP(timezone=True),
        comment="Last date on which the cell was valid; NULL indicates an active cell.",
    ),
    Column("longitude", Numeric(), comment="Longitude of the cell location."),
    Column("latitude", Numeric(), comment="Latitude of the cell location."),
    Column(
        "geom_point",
        Geometry("POINT", srid=4326),
        comment="Point location of the cell (equivalent to longitude/latitude).",
    ),
    Column(
        "record_created",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        comment="Timestamp when this cell record was created.",
    ),
    schema="infrastructure",
)

subscribers = Table(
    "subscribers",
    metadata,
    Column(
        "id",
        Integer(),
        primary_key=True,
        comment="FlowDB_internal subscriber identifier.",
    ),
    Column("msisdn", Text(), nullable=False, comment="MSISDN"),
    Column("imei", Text(), nullable=False, comment="IMEI"),
    Column("imsi", Text(), nullable=False, comment="IMSI"),
    Column("tac", Text(), nullable=False, comment="TAC"),
)

events_calls = Table(
    "calls",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        comment="FlowdDB-internal identifier for call events.",
    ),
    Column(
        "start_time",
        TIMESTAMP(timezone=True),
        nullable=False,
        comment="Timestamp of the start of the call.",
    ),
    Column("duration", Integer(), comment="Call duration in seconds"),
    schema="events",
)

events_call_parties = Table(
    "call_parties",
    metadata,
    Column(
        "id", UUID(), ForeignKey("events.calls.id"), comment="Call event identifier"
    ),
    Column(
        "is_outgoing",
        Boolean(),
        nullable=False,
        comment="If TRUE, the record refers to the calling subscriber; if FALSE, the record refers to the receiving subscriber.",
    ),
    Column(
        "subscriber_id",
        Integer(),
        ForeignKey("subscribers.id"),
        comment="Subscriber who initiated or received the call (depending on the value of `is_outgoing`).",
    ),
    Column(
        "cell_id",
        Integer(),
        ForeignKey("infrastructure.cells.id"),
        comment="Cell connected to by the subscriber.",
    ),
    schema="events",
)

create_schema_if_not_exists("events")
create_schema_if_not_exists("infrastructure")
metadata.create_all(bind=engine)

engine.execute(
    """
    BEGIN;

    CREATE OR REPLACE FUNCTION update_cell_point_location()
       RETURNS trigger AS
    $BODY$
    BEGIN
       IF NEW.geom_point IS NULL
       AND NEW.longitude IS NOT NULL
       AND NEW.latitude IS NOT NULL
       THEN
           NEW.geom_point := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
       END IF;

       RETURN NEW;
    END;
    $BODY$
    LANGUAGE plpgsql;

    CREATE TRIGGER cell_point_location_trigger BEFORE INSERT OR UPDATE
    ON infrastructure.cells
    FOR EACH ROW EXECUTE PROCEDURE update_cell_point_location();

    COMMIT;
    """
)
