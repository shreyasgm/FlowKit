# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marshmallow import Schema, fields, post_load
from marshmallow.validate import OneOf, Length

from flowmachine.features import TopUpBalance
from .base_exposed_query import BaseExposedQuery
from .custom_fields import AggregationUnit, Statistic, SubscriberSubset

__all__ = ["TopUpBalanceSchema", "TopUpBalanceExposed"]

class TopUpBalanceSchema(Schema):
    query_kind = fields.String(validate=OneOf(["topup_balance"]))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    statistic = Statistic()
    subscriber_subset = SubscriberSubset()

    @post_load
    def make_query_object(self, params, **kwargs):
        return TopUpBalanceExposed(**params)

class TopUpBalanceExposed(BaseExposedQuery):
    def __init__(self, *, start_date, end_date, statistic="avg", subscriber_subset=None):
        # Note: all input parameters need to be defined as attributes on `self`
        # so that marshmallow can serialise the object correctly.
        self.start_date = start_date
        self.end_date = end_date
        self.statistic = statistic
        self.subscriber_subset = subscriber_subset

    @property
    def _flowmachine_query_obj(self):
        """
        Return the underlying flowmachine TopUpBalance object.

        Returns
        -------
        Query
        """
        return TopUpBalance(
            start=start,
            stop=stop,
            statistic=statistic,
            subscriber_subset=subscriber_subset,
        )
