# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marshmallow import Schema, fields, post_load
from marshmallow.validate import OneOf, Length

from flowmachine.features import TotalLocationEvents
from flowmachine.features.location.redacted_total_events import RedactedTotalEvents
from .base_exposed_query import BaseExposedQuery
from .custom_fields import EventTypes, SubscriberSubset
from .aggregation_unit import AggregationUnit, get_spatial_unit_obj

__all__ = ["LocationEventCountsSchema", "LocationEventCountsExposed"]


class LocationEventCountsSchema(Schema):
    # query_kind parameter is required here for claims validation
    query_kind = fields.String(validate=OneOf(["location_event_counts"]))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    interval = fields.String(
        required=True, validate=OneOf(TotalLocationEvents.allowed_intervals)
    )
    direction = fields.String(
        required=True, validate=OneOf(["in", "out", "both"])
    )  # TODO: use a globally defined enum for this
    event_types = EventTypes()
    aggregation_unit = AggregationUnit()
    subscriber_subset = SubscriberSubset()

    @post_load
    def make_query_object(self, params, **kwargs):
        return LocationEventCountsExposed(**params)


class LocationEventCountsExposed(BaseExposedQuery):
    def __init__(
        self,
        *,
        start_date,
        end_date,
        interval,
        direction,
        event_types,
        aggregation_unit,
        subscriber_subset=None
    ):
        # Note: all input parameters need to be defined as attributes on `self`
        # so that marshmallow can serialise the object correctly.
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.direction = direction
        self.event_types = event_types
        self.aggregation_unit = aggregation_unit
        self.subscriber_subset = subscriber_subset

    @property
    def _flowmachine_query_obj(self):
        """
        Return the underlying flowmachine daily_location object.

        Returns
        -------
        Query
        """
        return RedactedTotalEvents(
            total_events=TotalLocationEvents(
                start=self.start_date,
                stop=self.end_date,
                interval=self.interval,
                direction=self.direction,
                table=self.event_types,
                spatial_unit=get_spatial_unit_obj(self.aggregation_unit),
                subscriber_subset=self.subscriber_subset,
            )
        )
