# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# -*- coding: utf-8 -*-
"""
Calculates the total number of unique sites or cells
at the network level.



"""

from typing import List

from ...core.mixins import GeoDataMixin
from ...core import location_joined_query
from ...core.query import Query
from ...core.spatial_unit import (
    CellSpatialUnit,
    VersionedSiteSpatialUnit,
    VersionedCellSpatialUnit,
    admin_spatial_unit,
)
from ..utilities import EventsTablesUnion

valid_stats = {"avg", "max", "min", "median", "mode", "stddev", "variance"}
valid_periods = ["second", "minute", "hour", "day", "month", "year"]


class TotalNetworkObjects(GeoDataMixin, Query):
    """
    Class for calculating unique cells/sites per location
    and aggregate it by period.

    Parameters
    ----------
    start : datetime
        Start time to filter query.
    stop : datetime
        Stop time to filter query.
    total_by : {'second', 'minute', 'hour', 'day', 'month', 'year'}
        A period definition to group data by.
    table : str
        Either 'calls', 'sms', or other table under `events.*`. If
        no specific table is provided this will collect
        statistics from all tables.
    network_object : {Cell,VersionedCell,VersionedSite}SpatialUnit, default CellSpatialUnit()
        Objects to track, defaults to CellSpatialUnit(), the unversioned lowest
        level of infrastructure available.
    spatial_unit : flowmachine.core.spatial_unit.*SpatialUnit,
                   default admin_spatial_unit(level=0)
        Spatial unit to facet on.

    Other Parameters
    ----------------
    Passed to EventsTablesUnion

    Examples
    --------
    >>> t = TotalNetworkObjects()
    >>> t.get_dataframe()
       total                  datetime
    0     55 2016-01-01 00:00:00+00:00
    1     55 2016-01-02 00:00:00+00:00
    ...

    """

    def __init__(
        self,
        start=None,
        stop=None,
        *,
        table="all",
        total_by="day",
        network_object=CellSpatialUnit(),
        spatial_unit=None,
        hours="all",
        subscriber_subset=None,
        subscriber_identifier="msisdn",
    ):
        self.start = (
            self.connection.min_date(table=table).strftime("%Y-%m-%d")
            if start is None
            else start
        )
        self.stop = (
            self.connection.max_date(table=table).strftime("%Y-%m-%d")
            if stop is None
            else stop
        )

        self.table = table.lower()
        if self.table != "all" and not self.table.startswith("events"):
            self.table = "events.{}".format(self.table)

        allowed_network_object_types = [
            CellSpatialUnit,
            VersionedCellSpatialUnit,
            VersionedSiteSpatialUnit,
        ]

        self.network_object = network_object
        if type(self.network_object) not in allowed_network_object_types:
            raise ValueError(
                "{} is not a valid network object type.".format(type(network_object))
            )

        if spatial_unit is None:
            self.spatial_unit = admin_spatial_unit(level=0)
        else:
            self.spatial_unit = spatial_unit
        if type(self.spatial_unit) in allowed_network_object_types:
            # No sense in aggregating network object to network object
            raise ValueError(
                "{} is not a valid spatial unit type for TotalNetworkObjects".format(
                    type(self.spatial_unit)
                )
            )

        events = location_joined_query(
            EventsTablesUnion(
                self.start,
                self.stop,
                tables=self.table,
                columns=["location_id", "datetime"],
                hours=hours,
                subscriber_subset=subscriber_subset,
                subscriber_identifier=subscriber_identifier,
            ),
            spatial_unit=self.network_object,
            time_col="datetime",
        )

        self.joined = location_joined_query(
            events, spatial_unit=self.spatial_unit, time_col="datetime"
        )
        self.total_by = total_by.lower()
        if self.total_by not in valid_periods:
            raise ValueError("{} is not a valid total_by value.".format(self.total_by))

        super().__init__()

    @property
    def column_names(self) -> List[str]:
        return self.spatial_unit.location_columns + ["value", "datetime"]

    def _make_query(self):
        cols = self.network_object.location_columns
        group_cols = self.spatial_unit.location_columns
        for column in group_cols:
            if column in cols:
                cols.remove(column)
        cols_str = ",".join(cols)
        group_cols_str = ",".join(group_cols)
        sql = f"""
        SELECT {group_cols_str}, COUNT(*) as value,
             datetime FROM
              (SELECT DISTINCT {group_cols_str}, {cols_str}, datetime FROM           
                (SELECT {group_cols_str}, {cols_str}, date_trunc('{self.total_by}', x.datetime) AS datetime
                FROM ({self.joined.get_query()}) x) y) _
            GROUP BY {group_cols_str}, datetime
            ORDER BY {group_cols_str}, datetime
        """

        return sql


class AggregateNetworkObjects(GeoDataMixin, Query):
    """
    Class for calculating statistics about unique cells/sites
    and aggregate it by period.

    Parameters
    ----------
    total_network_objects : TotalNetworkObjects

    statistic : {'avg', 'max', 'min', 'median', 'mode', 'stddev', 'variance'}
        Statistic to calculate, defaults to 'avg'.

    aggregate_by : {'second', 'minute', 'hour', 'day', 'month', 'year', 'century'}
        A period definition to calculate statistics over, defaults to the one
        greater than total_network_objects.total_by.

    Examples
    --------
    >>> t = AggregateNetworkObjects(total_network_objects=TotalNetworkObjects())
    >>> t.get_dataframe()
          name  total                  datetime
    0  Nepal     55 2016-01-01 00:00:00+00:00
    1  Nepal     55 2016-01-02 00:00:00+00:00
    2  Nepal     55 2016-01-03 00:00:00+00:00
    3  Nepal     55 2016-01-04 00:00:00+00:00
    4  Nepal     55 2016-01-05 00:00:00+00:00
    ...

    """

    def __init__(self, *, total_network_objects, statistic="avg", aggregate_by=None):
        self.total_objs = total_network_objects
        statistic = statistic.lower()
        if statistic in valid_stats:
            self.statistic = statistic
        else:
            raise ValueError(
                "{} is not a valid statistic use one of {!r}".format(
                    statistic, valid_stats
                )
            )
        if aggregate_by is None:
            if self.total_objs.total_by == "second":
                self.aggregate_by = "minute"
            elif self.total_objs.total_by == "minute":
                self.aggregate_by = "hour"
            elif self.total_objs.total_by == "hour":
                self.aggregate_by = "day"
            elif self.total_objs.total_by == "day":
                self.aggregate_by = "month"
            elif self.total_objs.total_by == "month":
                self.aggregate_by = "year"
            else:
                self.aggregate_by = "century"
        else:
            self.aggregate_by = aggregate_by
        if self.aggregate_by not in valid_periods + ["century"]:
            raise ValueError(
                "{} is not a valid aggregate_by value.".format(self.aggregate_by)
            )
        self.spatial_unit = self.total_objs.spatial_unit

        super().__init__()

    @property
    def column_names(self) -> List[str]:
        return self.spatial_unit.location_columns + ["value", "datetime"]

    def _make_query(self):
        group_cols = ",".join(self.spatial_unit.location_columns)
        if self.statistic == "mode":
            av_call = f"pg_catalog.mode() WITHIN GROUP(ORDER BY z.value)"
        else:
            av_call = f"{self.statistic}(z.value)"
        sql = f"""
        SELECT {group_cols}, {av_call} as value,
        date_trunc('{self.aggregate_by}', z.datetime) as datetime FROM 
            ({self.total_objs.get_query()}) z
        GROUP BY {group_cols}, date_trunc('{self.aggregate_by}', z.datetime)
        ORDER BY {group_cols}, date_trunc('{self.aggregate_by}', z.datetime)
        """
        return sql
