# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from cryptography.hazmat.backends.openssl.rsa import _RSAPrivateKey
from flask import jsonify, Blueprint, request, current_app
import jwt
import uuid
from flask.json import JSONEncoder
from flask_login import login_required, current_user
from typing import Dict, List, Union, Optional

from .models import *
from .invalid_usage import InvalidUsage, Unauthorized
from zxcvbn import zxcvbn
import jwt
import uuid

blueprint = Blueprint(__name__, __name__)


@blueprint.route("/groups")
@login_required
def list_my_groups():
    """
    Get a list of the groups the logged in user is a member of.

    Notes
    -----
    Returns a list of json objects with "id" and "group_name" keys.
    """
    return jsonify(
        [{"id": group.id, "group_name": group.name} for group in current_user.groups]
    )


@blueprint.route("/servers")
@login_required
def list_my_servers():
    """
    Get a list of all the servers the logged in user has access to.

    Notes
    -----
    Produces a list of json objects with "id" and "server_name" fields.
    """
    servers = set()
    for group in current_user.groups:
        for server_token_limit in group.server_token_limits:
            servers.add(server_token_limit.server)

    return jsonify(
        sorted(
            [{"id": server.id, "server_name": server.name} for server in servers],
            key=lambda s: s["server_name"],
        )
    )


@blueprint.route("/servers/<server_id>")
@login_required
def my_access(server_id):
    """
    Get the api endpoints the logged in user is allowed to use on this
    server, and the latest datetime their token can expire.

    Parameters
    ----------
    server_id: int
        Id of the server to check access on

    Notes
    -----
    Produces a json object with "allowed_claims" and "latest_expiry" keys.
    "allowed_claims" will be an object with claim names as keys, and the
    available rights nested below.

    """
    server = Server.query.filter(Server.id == server_id).first_or_404()
    allowed_claims = current_user.allowed_claims(server)
    return jsonify(
        {
            "allowed_claims": allowed_claims,
            "latest_expiry": current_user.latest_token_expiry(server),
        }
    )


@blueprint.route("/tokens")
@login_required
def list_all_my_tokens():
    """Get a list of all the logged in user's tokens."""
    return jsonify(
        [
            {
                "id": token.id,
                "name": token.name,
                "token": token.decrypted_token,
                "expires": token.expires,
                "server_name": token.server.name,
                "username": token.owner.username,
            }
            for token in Token.query.filter(Token.owner == current_user)
        ]
    )


@blueprint.route("/tokens/<server>")
@login_required
def list_my_tokens(server):
    """Get a list of all the logged in user's tokens on a specific server."""
    server = Server.query.filter(Server.id == server).first_or_404()
    return jsonify(
        [
            {
                "id": token.id,
                "name": token.name,
                "token": token.decrypted_token,
                "expires": token.expires,
                "server_name": token.server.name,
                "username": token.owner.username,
            }
            for token in Token.query.filter(
                Token.owner == current_user, Token.server == server
            )
        ]
    )


@blueprint.route("/tokens/<server>", methods=["POST"])
@login_required
def add_token(server):
    """
    Generate a new token for a server.

    Parameters
    ----------
    server: int
        ID of the server.

    Notes
    -----
    Expects json with "name", "expiry" and "claims" keys, where "name" is a string,
    expiry is a datetime string of the form ""%Y-%m-%dT%H:%M:%S.%fZ" (e.g. 2018-01-01T00:00:00.0Z),
    and claims is a nested dict of the form {<claim_name>:{<right_name>:<bool>}}.

    Responds with a json object {"token":<token_string>, "id":<token_id>}.

    """
    server = Server.query.filter(Server.id == server).first_or_404()
    json = request.get_json()

    current_app.logger.debug(json)

    if "name" not in json:
        raise InvalidUsage("No name.", payload={"bad_field": "name"})
    expiry = datetime.datetime.strptime(json["expiry"], "%Y-%m-%dT%H:%M:%S.%fZ")
    lifetime = expiry - datetime.datetime.now()
    latest_lifetime = current_user.latest_token_expiry(server)
    if expiry > latest_lifetime:
        raise InvalidUsage("Token lifetime too long", payload={"bad_field": "expiry"})
    allowed_claims = current_user.allowed_claims(server)

    current_app.logger.debug(allowed_claims)
    for claim, rights in json["claims"].items():
        if claim not in allowed_claims:
            raise Unauthorized(f"You do not have access to {claim} on {server.name}")
        for right, setting in rights["permissions"].items():
            if setting and not allowed_claims[claim]["permissions"][right]:
                raise Unauthorized(
                    f"You do not have access to {claim}:{right} on {server.name}"
                )
        for agg_unit in rights["spatial_aggregation"]:
            if agg_unit not in allowed_claims[claim]["spatial_aggregation"]:
                raise Unauthorized(
                    f"You do not have access to {claim} at {agg_unit} on {server.name}"
                )

    token_string = generate_token(
        username=current_user.username,
        flowapi_identifier=server.name,
        lifetime=lifetime,
        claims=json["claims"],
        private_key=current_app.config["PRIVATE_JWT_SIGNING_KEY"],
    )

    token = Token(
        name=json["name"],
        token=token_string,
        expires=expiry,
        owner=current_user,
        server=server,
    )
    db.session.add(token)
    db.session.commit()
    return jsonify({"token": token_string, "id": token.id})


# Duplicated in flowkit_jwt_generator (cannot re-use the implementation
# there because the module is outside the docker build context for flowauth).
# Duplicated in FlowAuth (cannot use this implementation there because
# this module is outside the docker build context for FlowAuth).
# Duplicated in FlowAuth (cannot use this implementation there because
# this module is outside the docker build context for FlowAuth).
def generate_token(
    *,
    flowapi_identifier: Optional[str] = None,
    username: str,
    private_key: Union[str, _RSAPrivateKey],
    lifetime: datetime.timedelta,
    claims: Dict[str, Dict[str, Union[Dict[str, bool], List[str]]]],
) -> str:
    """

    Parameters
    ----------
    username : str
        Username for the token
    private_key : str or _RSAPrivateKey
        Private key to use to sign the token.  May be an _RSAPrivateKey object, or a string
        containing a PEM encoded key
    lifetime : datetime.timedelta
        Lifetime from now of the token
    claims : dict
        Dictionary of claims the token will grant
    flowapi_identifier : str, optional
        Optionally provide a string to identify the audience of the token

    Examples
    --------
    >>> generate_token(flowapi_identifier="TEST_SERVER",username="TEST_USER",private_key=rsa_private_key,lifetime=datetime.timedelta(5),claims={"daily_location":{"permissions": {"run":True},)
            "spatial_aggregation": ["admin3"]}})
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NTc0MDM1OTgsIm5iZiI6MTU1NzQwMzU5OCwianRpIjoiZjIwZmRlYzYtYTA4ZS00Y2VlLWJiODktYjc4OGJhNjcyMDFiIiwidXNlcl9jbGFpbXMiOnsiZGFpbHlfbG9jYXRpb24iOnsicGVybWlzc2lvbnMiOnsicnVuIjp0cnVlfSwic3BhdGlhbF9hZ2dyZWdhdGlvbiI6WyJhZG1pbjMiXX19LCJpZGVudGl0eSI6IlRFU1RfVVNFUiIsImV4cCI6MTU1NzgzNTU5OCwiYXVkIjoiVEVTVF9TRVJWRVIifQ.yxBFYZ2EFyVKdVT9Sc-vC6qUpwRNQHt4KcOdFrQ4YrI'

    Returns
    -------
    str
        Encoded token

    """

    now = datetime.datetime.utcnow()
    token_data = dict(
        iat=now,
        nbf=now,
        jti=str(uuid.uuid4()),
        user_claims=claims,
        identity=username,
        exp=now + lifetime,
    )
    if flowapi_identifier is not None:
        token_data["aud"] = flowapi_identifier
    return jwt.encode(
        payload=token_data, key=private_key, algorithm="RS256", json_encoder=JSONEncoder
    ).decode("utf-8")
