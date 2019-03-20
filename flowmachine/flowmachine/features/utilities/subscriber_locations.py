# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from abc import ABCMeta

from typing import List

"""
Classes for determining elementary location elements.
These are used for creating base objects that are
later used for computing subscriber features.

"""
import logging

from .events_tables_union import EventsTablesUnion
from .spatial_aggregates import SpatialAggregate, JoinedSpatialAggregate

from ...core.query import Query
from ...core.join_to_location import JoinToLocation

logger = logging.getLogger("flowmachine").getChild(__name__)


class _SubscriberCells(Query):
    # Passing table='all' means it will look at all tables with location
    # data.
    def __init__(
        self,
        start,
        stop,
        hours="all",
        table="all",
        subscriber_identifier="msisdn",
        ignore_nulls=True,
        *,
        subscriber_subset=None,
    ):

        self.start = start
        self.stop = stop
        self.hours = hours
        self.table = table
        self.subscriber_identifier = subscriber_identifier
        self.ignore_nulls = ignore_nulls
        self.spatial_unit = None

        self.tables = table
        cols = [self.subscriber_identifier, "datetime", "location_id"]
        self.unioned = EventsTablesUnion(
            self.start,
            self.stop,
            columns=cols,
            tables=self.table,
            hours=self.hours,
            subscriber_subset=subscriber_subset,
            subscriber_identifier=self.subscriber_identifier,
        )
        super().__init__()

    @property
    def column_names(self) -> List[str]:
        return ["subscriber", "time", "location_id"]

    def _make_query(self):

        if self.ignore_nulls:
            where_clause = "WHERE location_id IS NOT NULL AND location_id !=''"
        else:
            where_clause = ""

        sql = f"""
                SELECT
                    subscriber, datetime as time, location_id
                FROM
                    ({self.unioned.get_query()}) AS foo
                {where_clause}
                """
        return sql


class BaseLocation:
    """
    Mixin for all daily and home location methods.
    Provides the method to aggregate spatially.
    """

    def aggregate(self):
        """
        Aggregate to the spatial level returning a query object
        that represents the location, and the total counts of
        subscribers.
        """
        return SpatialAggregate(self)

    def join_aggregate(self, metric, method="mean"):
        """
        Join with a metric representing object and aggregate
        spatially.

        Parameters
        ----------
        metric : Query
        method : {"mean", "mode", "median"}

        Returns
        -------
        JoinedSpatialAggregate
        """

        return JoinedSpatialAggregate(metric, self, method=method)

    def __getitem__(self, item):

        return self.subset(col="subscriber", subset=item)


def subscriber_locations(
    start,
    stop,
    *,
    spatial_unit=None,
    hours="all",
    table="all",
    subscriber_identifier="msisdn",
    ignore_nulls=True,
    subscriber_subset=None,
):
    """
    Class representing all the locations for which a subscriber has been found.
    Can be at the level of a tower, lat-lon, or an admin unit.

    Parameters
    ----------
    start : str
        iso format date range for the beginning of the time frame,
        e.g. 2016-01-01 or 2016-01-01 14:03:01
    stop : str
        As above
    spatial_unit : flowmachine.core.spatial_unit.*SpatialUnit or None,
                   default None
        Spatial unit to which subscriber locations will be mapped. See the
        docstring of spatial_unit.py for more information. Use None for no
        location join (i.e. just the cell identifier in the CDR itself).
    hours : tuple of ints, default 'all'
        subset the result within certain hours, e.g. (4,17)
        This will subset the query only with these hours, but
        across all specified days. Or set to 'all' to include
        all hours.
    table : str, default 'all'
        schema qualified name of the table which the analysis is
        based upon. If 'all' it will pull together all of the tables
        specified as flowmachine.yml under 'location_tables'
    subscriber_identifier : str, default 'msisdn'
        whether to identify a subscriber by either msisdn, imei or imsi.
    ignore_nulls : bool, default True
        ignores those values that are null. Sometime data appears for which
        the cell is null. If set to true this will ignore those lines. If false
        these lines with null cells should still be present, although they contain
        no information on the subscribers location, they still tell us that the subscriber made
        a call at that time.

    Notes
    -----
    * A date without a hours and mins will be interpreted as
      midnight of that day, so to get data within a single day
      pass (e.g.) '2016-01-01', '2016-01-02'.

    * Use 24 hr format!

    Examples
    --------
    >>> subscriber_locs = subscriber_locations('2016-01-01 13:30:30',
                               '2016-01-02 16:25:00'
                               spatial_unit = None)
    >>> subscriber_locs.head()
     subscriber                 time    cell
    subscriberA  2016-01-01 12:42:11  233241
    subscriberA  2016-01-01 12:52:11  234111
    subscriberB  2016-01-01 12:52:16  234111
    ...

    """
    # Here we call the hidden class _SubscriberCells which is every spotting
    # of all subscribers. We then join to the appropriate level if necessary.
    subscriber_cells = _SubscriberCells(
        start,
        stop,
        hours,
        table=table,
        subscriber_subset=subscriber_subset,
        subscriber_identifier=subscriber_identifier,
        ignore_nulls=ignore_nulls,
    )

    if spatial_unit is None:
        return subscriber_cells
    else:
        return JoinToLocation(
            subscriber_cells, spatial_unit=spatial_unit, time_col="time"
        )

