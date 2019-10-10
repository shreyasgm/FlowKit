from functools import partial
from typing import Dict

from flask_jwt_extended.exceptions import UserClaimsVerificationError

from flowapi.flowapi_errors import (
    BadQueryError,
    MissingAggregationUnitError,
    MissingQueryKindError,
    AggregationUnitMismatchError,
)


def verify_can_do_action(*, claims: dict, action: str, query_kind: str) -> bool:
    """
    Verify that the claims dictionary allows doing action with query_kind.

    Parameters
    ----------
    claims : dict
        A user's claims dictionary
    action : {'run', 'poll', 'get_results'}
        Action to check
    query_kind : str
        Type of the query

    Returns
    -------
    bool
        True if the claims permit the action with this kind of query

    Raises
    ------
    UserClaimsVerificationError
        If the user cannot do action with this kind of query
    """
    action_rights = claims[query_kind]["permissions"][action]
    if not action_rights:
        raise UserClaimsVerificationError(
            f"Token does not allow {action} for query kind '{query_kind}'"
        )
    return True


def has_access_nonspatial(
    *, claims: dict, action: str, query_kind: str, aggregation: str
) -> bool:
    """
    Returns true if claims permit 'action' with this kind of query at this unit of aggregation.

    Parameters
    ----------
    claims : dict
        A user's claims dictionary
    action : {'run', 'poll', 'get_results'}
        Action to check
    query_kind : str
        Type of the query
    aggregation : str
        Kind of aggregate

    Returns
    -------
    bool
        True if the claims permit 'action' with this query

    Raises
    ------
    UserClaimsVerificationError
        If the user cannot do action with this kind of query at this level of aggregation
    """
    try:
        verify_can_do_action(claims=claims, action=action, query_kind=query_kind)
        aggregation_right = claims[query_kind]["aggregations"][aggregation]
        if not aggregation_right:
            raise UserClaimsVerificationError(
                f"Token does not allow aggregate '{aggregation}' of query kind '{query_kind}'"
            )
    except KeyError:
        raise UserClaimsVerificationError("Claims verification failed.")
    return True


def has_access_spatial(
    *, claims: dict, action: str, query_kinds_and_aggregations: Dict[str, str]
) -> bool:
    """
    Returns true if claims permit 'action' with this kind of query at this unit of aggregation.

    Parameters
    ----------
    claims : dict
        A user's claims dictionary
    action : {'run', 'poll', 'get_results'}
        Action to check
    query_kinds_and_aggregations : list of tuples
        List of tuples giving a query kind and aggregation unit

    Returns
    -------
    bool
        True if the claims permit 'action' with this query

    Raises
    ------
    UserClaimsVerificationError
        If the user cannot do action with this kind of query at this level of aggregation
    """
    for query_kind, aggregation_unit in query_kinds_and_aggregations.items():
        try:
            verify_can_do_action(claims=claims, action=action, query_kind=query_kind)
            aggregation_right = (
                aggregation_unit
                in claims[query_kind]["aggregations"]["spatial_aggregation"]
            )

            if not aggregation_right:
                raise UserClaimsVerificationError(
                    f"Token does not allow query kind '{query_kind}' at spatial aggregation '{aggregation_unit}'"
                )
        except KeyError:
            raise UserClaimsVerificationError("Claims verification failed.")
    return True


def get_kind(query_json):
    try:
        return query_json["query_kind"]
    except KeyError:
        raise MissingQueryKindError


def get_aggregation_unit(query_json):
    try:
        return query_json["aggregation_unit"]
    except KeyError:
        raise MissingAggregationUnitError


def get_kind_and_aggregation_unit(query_json):
    return {get_kind(query_json): get_aggregation_unit(query_json)}


def get_spatial_aggregate_kind_and_claims(query_json):
    try:
        return get_kind_and_aggregation_unit(query_json["locations"])
    except KeyError:
        raise BadQueryError


def get_joined_spatial_aggregate_kind_and_claims(query_json):
    location_spec = get_spatial_aggregate_kind_and_claims(query_json)
    try:
        wrapped_metric = query_json["metric"]
        # Some metrics don't have an aggregation unit
        if "aggregation_unit" not in wrapped_metric:
            wrapped_metric["aggregation_unit"] = query_json["locations"][
                "aggregation_unit"
            ]
    except KeyError:
        raise BadQueryError
    if (
        wrapped_metric["aggregation_unit"]
        != query_json["locations"]["aggregation_unit"]
    ):
        # TODO: add support for different aggregation units
        raise AggregationUnitMismatchError

    return dict(location_spec, **get_kind_and_aggregation_unit(wrapped_metric))


def get_aggregate_network_objects_kind_and_claims(query_json):
    try:
        return get_kind_and_aggregation_unit(query_json["total_network_objects"])
    except KeyError:
        raise BadQueryError


def get_aggregate_query_kind(query_json):
    try:
        return get_kind(query_json["metric"])
    except KeyError:
        raise BadQueryError


def get_verifier(query_json: dict):
    spatial_aggregates = dict(
        spatial_aggregate=get_spatial_aggregate_kind_and_claims,
        joined_spatial_aggregate=get_joined_spatial_aggregate_kind_and_claims,
        aggregate_network_objects=get_aggregate_network_objects_kind_and_claims,
    )
    non_spatial_aggregates = {"histogram_aggregate": get_aggregate_query_kind}
    try:
        aggregate_kind = query_json["query_kind"]
    except KeyError:
        raise MissingQueryKindError

    if aggregate_kind in non_spatial_aggregates:
        return partial(
            has_access_nonspatial,
            aggregate_kind=aggregate_kind,
            query_kind=non_spatial_aggregates[aggregate_kind](query_json),
        )
    else:
        return partial(
            has_access_spatial,
            query_kinds_and_aggregations=spatial_aggregates.get(
                aggregate_kind, get_kind_and_aggregation_unit
            )(query_json),
        )
