#!/usr/bin/env python3

import os
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    Text,
    TIMESTAMP,
    Numeric,
    func,
)
from geoalchemy2 import Geometry
from sqlalchemy.schema import CreateSchema

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

# events_calls = Table(
#     "calls",
#     metadata,
#     Column("id", Text()),
#     Column("outgoing", Boolean()),
#     Column("datetime", TIMESTAMP(timezone=True), nullable=False),
#     Column("duration", Numeric()),
#     Column("network", Text()),
#     Column("msisdn", Text(), nullable=False),
#     Column("msisdn_counterpart", Text()),
#     Column("location_id", Text()),
#     Column("imsi", Text()),
#     Column("imei", Text()),
#     Column("tac", Numeric(8)),
#     Column("operator_code", Numeric()),
#     Column("country_code", Numeric()),
#     schema="events",
# )

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
