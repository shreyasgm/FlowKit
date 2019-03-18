# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# -*- coding: utf-8 -*-
"""
Class for calculating top-up recharge amount statistics.
"""

import warnings

from ..utilities.sets import EventsTablesUnion
from .metaclasses import SubscriberFeature

valid_stats = {"count", "sum", "avg", "max", "min", "median", "stddev", "variance"}


class TopUpAmount(SubscriberFeature):
    """
    This class calculates statistics associated with top-up recharge amounts.

    Parameters
    ----------
    start, stop : str
         iso-format start and stop datetimes
    statistic : {'count', 'sum', 'avg', 'max', 'min', 'median', 'mode', 'stddev', 'variance'}, default 'avg'
        Defaults to sum, aggregation statistic over the durations.
    hours : 2-tuple of floats, default 'all'
        Restrict the analysis to only a certain set
        of hours within each day.
    subscriber_identifier : {'msisdn', 'imei'}, default 'msisdn'
        Either msisdn, or imei, the column that identifies the subscriber.
    subscriber_subset : str, list, flowmachine.core.Query, flowmachine.core.Table, default None
        If provided, string or list of string which are msisdn or imeis to limit
        results to; or, a query or table which has a column with a name matching
        subscriber_identifier (typically, msisdn), to limit results to.

    Examples
    --------

    >>> s = TopUpAmount("2016-01-01", "2016-01-08")
    >>> s.get_dataframe()

          subscriber       value
    bjY7mMXxE3zMoelO    5.580000
    dqEQWNwAYEr4Mk3e    5.150000
    BNxWrJ9mqMJ83Mzk    3.968000
    346j7Nq67nvXZR0m    6.265455
    7XebRKr35JMJnq8A    3.748750
                 ...         ...
    """

    def __init__(
        self,
        start,
        stop,
        statistic="avg",
        *,
        subscriber_identifier="msisdn",
        hours="all",
        subscriber_subset=None,
    ):
        self.start = start
        self.stop = stop
        self.subscriber_identifier = subscriber_identifier
        self.hours = hours
        self.statistic = statistic.lower()
        self.tables = "events.topups"

        if self.statistic not in valid_stats:
            raise ValueError(
                "{} is not a valid statistic. Use one of {}".format(
                    self.statistic, valid_stats
                )
            )

        column_list = [self.subscriber_identifier, "recharge_amount"]

        self.unioned_query = EventsTablesUnion(
            self.start,
            self.stop,
            tables=self.tables,
            columns=column_list,
            hours=hours,
            subscriber_identifier=subscriber_identifier,
            subscriber_subset=subscriber_subset,
        )

        super().__init__()

    @property
    def column_names(self):
        return ["subscriber", f"value"]

    def _make_query(self):

        return f"""
        SELECT subscriber, {self.statistic}(recharge_amount) AS value
        FROM ({self.unioned_query.get_query()}) U
        GROUP BY subscriber
        """
