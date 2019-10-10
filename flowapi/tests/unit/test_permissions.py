# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from flask_jwt_extended.exceptions import UserClaimsVerificationError

from flowapi.flowapi_errors import (
    BadQueryError,
    AggregationUnitMismatchError,
    MissingQueryKindError,
    MissingAggregationUnitError,
)
from flowapi.permissions import (
    get_spatial_aggregate_kind_and_claims,
    get_joined_spatial_aggregate_kind_and_claims,
    get_aggregate_network_objects_kind_and_claims,
    get_aggregate_query_kind,
    get_kind,
    get_aggregation_unit,
    verify_can_do_action,
    has_access_nonspatial,
    get_verifier,
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
    with pytest.raises(MissingAggregationUnitError):
        get_aggregation_unit(dict())


def test_verify_can_do_action():
    assert verify_can_do_action(
        claims=dict(dummy_query=dict(permissions=dict(test_action=True))),
        query_kind="dummy_query",
        action="test_action",
    )


def test_verify_can_do_action_raises_on_unverified():
    with pytest.raises(
        UserClaimsVerificationError,
        match="Token does not allow test_action for query kind 'dummy_query'",
    ):
        verify_can_do_action(
            claims=dict(dummy_query=dict(permissions=dict(test_action=False))),
            query_kind="dummy_query",
            action="test_action",
        )


def test_has_access_nonspatial():
    assert has_access_nonspatial(
        claims=dict(
            dummy_query=dict(
                aggregations=dict(test_aggregation=True),
                permissions=dict(test_action=True),
            )
        ),
        query_kind="dummy_query",
        action="test_action",
        aggregation="test_aggregation",
    )


def test_has_access_nonspatial_raises_on_unverified():
    with pytest.raises(
        UserClaimsVerificationError,
        match="Token does not allow aggregate 'test_aggregation' of query kind 'dummy_query'",
    ):
        has_access_nonspatial(
            claims=dict(
                dummy_query=dict(
                    aggregations=dict(test_aggregation=False),
                    permissions=dict(test_action=True),
                )
            ),
            query_kind="dummy_query",
            action="test_action",
            aggregation="test_aggregation",
        )


def test_has_access_nonspatial_no_verify_with_missing_key():
    with pytest.raises(
        UserClaimsVerificationError, match="Claims verification failed."
    ):
        has_access_nonspatial(
            claims=dict(),
            query_kind="dummy_query",
            action="test_action",
            aggregation="test_aggregation",
        )


def test_verify_access_nonspatial():
    assert get_verifier(
        query_json=dict(
            query_kind="histogram_aggregate", metric=dict(query_kind="dummy_query")
        )
    )(
        claims=dict(
            dummy_query=dict(
                aggregations=dict(histogram_aggregate=True),
                permissions=dict(test_action=True),
            )
        ),
        action="test_action",
    )
