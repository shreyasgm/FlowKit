# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from flowapi.flowapi_errors import (
    BadQueryError,
    AggregationUnitMismatchError,
    MissingQueryKindError,
)
from flowapi.permissions import (
    get_spatial_aggregate_kind_and_claims,
    get_joined_spatial_aggregate_kind_and_claims,
    get_aggregate_network_objects_kind_and_claims,
    get_aggregate_query_kind,
    get_kind,
    get_aggregation_unit,
)


def test_get_spatial_aggregate_kind_and_claims_requires_locations():
    with pytest.raises(BadQueryError):
        get_spatial_aggregate_kind_and_claims(dict())


def test_differing_aggregation_units_raises_error():
    with pytest.raises(AggregationUnitMismatchError):
        get_joined_spatial_aggregate_kind_and_claims(
            dict(
                locations=dict(
                    query_kind="DUMMY_LOCATIONS_KIND", aggregation_unit="DUMMY_UNIT_A"
                ),
                metric=dict(
                    query_kind="DUMMY_METRIC_KIND", aggregation_unit="DUMMY_UNIT_B"
                ),
            )
        )


def test_joined_spatial_can_use_location_agg_unit():
    specs = get_joined_spatial_aggregate_kind_and_claims(
        dict(
            locations=dict(
                query_kind="DUMMY_LOCATIONS_KIND", aggregation_unit="DUMMY_UNIT_A"
            ),
            metric=dict(query_kind="DUMMY_METRIC_KIND"),
        )
    )
    assert specs["DUMMY_METRIC_KIND"] == "DUMMY_UNIT_A"


def test_get_aggregate_network_objects_kind_and_claims_requires_tno():
    with pytest.raises(BadQueryError):
        get_aggregate_network_objects_kind_and_claims(dict())


def test_get_aggregate_query_kind_requires_metric():
    with pytest.raises(BadQueryError):
        get_aggregate_query_kind(dict())


def test_get_kind_raises_error_when_missing():
    with pytest.raises(MissingQueryKindError):
        get_kind(dict())


def test_get_aggregation_unit_raises_error_when_missing():
    with pytest.raises(MissingQueryKindError):
        get_aggregation_unit(dict())
