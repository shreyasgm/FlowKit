from marshmallow import Schema, fields, post_load
from marshmallow.validate import OneOf

from flowmachine.features import subscriber_locations


class SubscriberLocationsSchema(Schema):
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    aggregation_unit = fields.String(
        required=True, validate=OneOf(["admin0", "admin1", "admin2", "admin3"])
    )
    subscriber_subset = fields.String(
        required=False, allow_none=True, validate=OneOf([None])
    )

    @post_load
    def make_query_object(self, params):
        return SubscriberLocationsExposed(**params)


class SubscriberLocationsExposed:
    __schema__ = SubscriberLocationsSchema

    def __init__(
        self, *, start_date, end_date, aggregation_unit, subscriber_subset=None
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.aggregation_unit = aggregation_unit
        self.subscriber_subset = subscriber_subset
        super().__init__()  # NOTE: this *must* be called at the end of the __init__() method of any subclass of BaseExposedQuery

    @property
    def _flowmachine_query_obj(self):
        """
        Return the underlying flowmachine query object.

        Returns
        -------
        Query
        """
        return subscriber_locations(
            start=self.start_date,
            stop=self.end_date,
            level=self.aggregation_unit,
            subscriber_subset=self.subscriber_subset,
        )
