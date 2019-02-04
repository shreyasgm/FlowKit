# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# -*- coding: utf-8 -*-
"""
Calculates the proportion of calls that a
subscriber makes during night time. Nocturnal
hour definitions can be specified.



"""
from .metaclasses import SubscriberFeature
from ...utils.utils import parse_tables_ensuring_columns
from ..utilities import EventsTablesUnion


class NocturnalEvents(SubscriberFeature):
    """
    Represents the percentage of events that a subscriber make/receives which
    are at night. The definition of night is configurable.

    Parameters
    ----------
    start, stop : str
         iso-format start and stop datetimes
    hours : tuple of ints, default (20, 4)
        Hours that count as being nocturnal. e.g. (20,4)
        will be the times after 8pm and before 4 am.
    subscriber_identifier : {'msisdn', 'imei'}, default 'msisdn'
        Either msisdn, or imei, the column that identifies the subscriber.
    subscriber_subset : str, list, flowmachine.core.Query, flowmachine.core.Table, default None
        If provided, string or list of string which are msisdn or imeis to limit
        results to; or, a query or table which has a column with a name matching
        subscriber_identifier (typically, msisdn), to limit results to.
    direction : {'in', 'out', 'both'}, default 'out'
        Whether to consider calls made, received, or both. Defaults to 'out'.
    tables : str or list of strings, default 'all'
        Can be a string of a single table (with the schema)
        or a list of these. The keyword all is to select all
        subscriber tables

    Examples
    --------

    >>> s = NocturnalEvents("2016-01-01", "2016-01-02")
    >>> s.get_dataframe()

          subscriber  percentage_nocturnal
    2ZdMowMXoyMByY07              0.000000
    MobnrVMDK24wPRzB             40.000000
    0Ze1l70j0LNgyY4w             16.666667
    Nnlqka1oevEMvVrm             33.333333
    4dqenN2oQZExwEK2             83.333333
                 ...                   ...
    """

    def __init__(
        self,
        start,
        stop,
        hours=(20, 4),
        *,
        subscriber_identifier="msisdn",
        direction="both",
        subscriber_subset=None,
        tables="all",
    ):
        self.start = start
        self.stop = stop
        self.subscriber_identifier = subscriber_identifier
        self.direction = direction
        self.hours = hours

        if direction not in {"in", "out", "both"}:
            raise ValueError("{} is not a valid direction.".format(self.direction))

        if self.direction == "both":
            column_list = [self.subscriber_identifier, "datetime"]
            self.tables = tables
        else:
            column_list = [self.subscriber_identifier, "datetime", "outgoing"]
            self.tables = parse_tables_ensuring_columns(
                self.connection, tables, column_list
            )

        self.unioned_query = EventsTablesUnion(
            self.start,
            self.stop,
            tables=self.tables,
            columns=column_list,
            hours="all",
            subscriber_identifier=subscriber_identifier,
            subscriber_subset=subscriber_subset,
        )
        super().__init__()

    def _make_query(self):
        where_clause = ""
        if self.direction != "both":
            where_clause = (
                f"WHERE outgoing IS {'TRUE' if self.direction == 'out' else 'FALSE'}"
            )

        sql = f"""
        SELECT
            subscriber,
            AVG(nocturnal)*100 AS percentage_nocturnal
        FROM (
            SELECT
                subscriber,
                CASE
                    WHEN extract(hour FROM datetime) >= {self.hours[0]}
                      OR extract(hour FROM datetime) < {self.hours[1]}
                    THEN 1
                ELSE 0
            END AS nocturnal
            FROM ({self.unioned_query.get_query()}) U
            {where_clause}
        ) U
        GROUP BY subscriber
        """

        return sql
