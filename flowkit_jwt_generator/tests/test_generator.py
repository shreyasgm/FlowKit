# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import timedelta

import jwt

from flowkit_jwt_generator.jwt import generate_token


def test_token_generator(private_key, public_key):
    """Test that the baseline token generator behaves as expected"""
    token = generate_token(
        username="test",
        private_key=private_key,
        lifetime=timedelta(seconds=90),
        claims={"A_CLAIM": "A_VALUE"},
    )
    decoded = jwt.decode(jwt=token, key=public_key, verify=True, algorithms=["RS256"])
    assert decoded["identity"] == "test"
    assert decoded["user_claims"] == {"A_CLAIM": "A_VALUE"}
    assert "aud" not in decoded


def test_token_generator_with_audience(private_key, public_key):
    """Test that the baseline token generator behaves as expected when given an audience"""
    token = generate_token(
        flowapi_identifier="test_audience",
        username="test",
        private_key=private_key,
        lifetime=timedelta(seconds=90),
        claims={"A_CLAIM": "A_VALUE"},
    )
    decoded = jwt.decode(
        jwt=token,
        key=public_key,
        verify=True,
        algorithms=["RS256"],
        audience="test_audience",
    )
    assert decoded["identity"] == "test"
    assert decoded["user_claims"] == {"A_CLAIM": "A_VALUE"}
