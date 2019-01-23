# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from flowmachine.core.server.query_proxy import construct_query_object


@pytest.mark.parametrize(
    "expected_md5, query_spec",
    [
        (
            "7ea3c788cb7f5829ee2a69494e502765",
            {
                "query_kind": "daily_location",
                "params": {
                    "date": "2016-01-01",
                    "aggregation_unit": "admin3",
                    "daily_location_method": "last",
                    "subscriber_subset": "all",
                },
            },
        ),
        (
            "74144a23f168a1e33618c2125382d854",
            {
                "query_kind": "location_event_counts",
                "params": {
                    "start_date": "2016-01-01",
                    "end_date": "2016-01-02",
                    "interval": "day",
                    "aggregation_unit": "admin3",
                    "direction": "all",
                    "event_types": "all",
                    "subscriber_subset": "all",
                },
            },
        ),
        (
            "53a49e08294bf1d83d8122ee211f3bf5",
            {
                "query_kind": "modal_location",
                "params": {
                    "locations": (
                        {
                            "query_kind": "daily_location",
                            "params": {
                                "date": "2016-01-01",
                                "aggregation_unit": "admin3",
                                "daily_location_method": "last",
                                "subscriber_subset": "all",
                            },
                        },
                        {
                            "query_kind": "daily_location",
                            "params": {
                                "date": "2016-01-02",
                                "aggregation_unit": "admin3",
                                "daily_location_method": "last",
                                "subscriber_subset": "all",
                            },
                        },
                    ),
                    "aggregation_unit": "admin3",
                },
            },
        ),
        (
            "8429a8f8f7681468ddb52e24ff95433a",
            {
                "query_kind": "meaningful_locations_aggregate",
                "params": {
                    "aggregation_unit": "admin1",
                    "meaningful_locations": {
                        "query_kind": "meaningful_locations",
                        "params": {
                            "label": "unknown",
                            "clusters": {
                                "query_kind": "hartigan_cluster",
                                "params": {
                                    "radius": 1.0,
                                    "buffer": 0.0,
                                    "call_threshold": 0,
                                    "call_days": {
                                        "query_kind": "call_days",
                                        "params": {
                                            "subscriber_locations": {
                                                "query_kind": "subscriber_locations",
                                                "params": {
                                                    "start": "2016-01-01",
                                                    "stop": "2016-01-02",
                                                    "level": "versioned-site",
                                                    "subscriber_subset": "all",
                                                },
                                            }
                                        },
                                    },
                                },
                            },
                            "scores": {
                                "query_kind": "event_score",
                                "params": {
                                    "score_hour": [
                                        -1,
                                        -1,
                                        -1,
                                        -1,
                                        -1,
                                        -1,
                                        -1,
                                        0,
                                        0,
                                        1,
                                        1,
                                        1,
                                        1,
                                        1,
                                        1,
                                        1,
                                        1,
                                        0,
                                        0,
                                        0,
                                        0,
                                        -1,
                                        -1,
                                        -1,
                                    ],
                                    "score_dow": {
                                        "monday": 1,
                                        "tuesday": 1,
                                        "wednesday": 1,
                                        "thursday": 0,
                                        "friday": -1,
                                        "saturday": -1,
                                        "sunday": -1,
                                    },
                                    "start": "2016-01-01",
                                    "stop": "2016-01-02",
                                    "level": "versioned-site",
                                    "subscriber_subset": "all",
                                },
                            },
                            "labels": {
                                "evening": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [1e-06, -0.5],
                                            [1e-06, -1.1],
                                            [1.1, -1.1],
                                            [1.1, -0.5],
                                        ]
                                    ],
                                },
                                "day": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [-1.1, -0.5],
                                            [-1.1, 0.5],
                                            [-1e-06, 0.5],
                                            [0, -0.5],
                                        ]
                                    ],
                                },
                            },
                        },
                    },
                },
            },
        ),
        (
            "90f9ce2ded9d3b0d3b9090ff4062350d",
            {
                "query_kind": "meaningful_locations_od_matrix",
                "params": {
                    "aggregation_unit": "admin1",
                    "meaningful_locations_a": {
                        "query_kind": "meaningful_locations",
                        "params": {
                            "label": "unknown",
                            "clusters": {
                                "query_kind": "hartigan_cluster",
                                "params": {
                                    "radius": 1.0,
                                    "buffer": 0.0,
                                    "call_threshold": 0,
                                    "call_days": {
                                        "query_kind": "call_days",
                                        "params": {
                                            "subscriber_locations": {
                                                "query_kind": "subscriber_locations",
                                                "params": {
                                                    "start": "2016-01-01",
                                                    "stop": "2016-01-02",
                                                    "level": "versioned-site",
                                                    "subscriber_subset": "all",
                                                },
                                            }
                                        },
                                    },
                                },
                            },
                            "scores": {
                                "query_kind": "event_score",
                                "params": {
                                    "score_hour": [
                                        -1,
                                        -1,
                                        -1,
                                        -1,
                                        -1,
                                        -1,
                                        -1,
                                        0,
                                        0,
                                        1,
                                        1,
                                        1,
                                        1,
                                        1,
                                        1,
                                        1,
                                        1,
                                        0,
                                        0,
                                        0,
                                        0,
                                        -1,
                                        -1,
                                        -1,
                                    ],
                                    "score_dow": {
                                        "monday": 1,
                                        "tuesday": 1,
                                        "wednesday": 1,
                                        "thursday": 0,
                                        "friday": -1,
                                        "saturday": -1,
                                        "sunday": -1,
                                    },
                                    "start": "2016-01-01",
                                    "stop": "2016-01-02",
                                    "level": "versioned-site",
                                    "subscriber_subset": "all",
                                },
                            },
                            "labels": {
                                "evening": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [1e-06, -0.5],
                                            [1e-06, -1.1],
                                            [1.1, -1.1],
                                            [1.1, -0.5],
                                        ]
                                    ],
                                },
                                "day": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [-1.1, -0.5],
                                            [-1.1, 0.5],
                                            [-1e-06, 0.5],
                                            [0, -0.5],
                                        ]
                                    ],
                                },
                            },
                        },
                    },
                    "meaningful_locations_b": {
                        "query_kind": "meaningful_locations",
                        "params": {
                            "label": "evening",
                            "clusters": {
                                "query_kind": "hartigan_cluster",
                                "params": {
                                    "radius": 1.0,
                                    "buffer": 0.0,
                                    "call_threshold": 0,
                                    "call_days": {
                                        "query_kind": "call_days",
                                        "params": {
                                            "subscriber_locations": {
                                                "query_kind": "subscriber_locations",
                                                "params": {
                                                    "start": "2016-01-01",
                                                    "stop": "2016-01-02",
                                                    "level": "versioned-site",
                                                    "subscriber_subset": "all",
                                                },
                                            }
                                        },
                                    },
                                },
                            },
                            "scores": {
                                "query_kind": "event_score",
                                "params": {
                                    "score_hour": [
                                        -1,
                                        -1,
                                        -1,
                                        -1,
                                        -1,
                                        -1,
                                        -1,
                                        0,
                                        0,
                                        1,
                                        1,
                                        1,
                                        1,
                                        1,
                                        1,
                                        1,
                                        1,
                                        0,
                                        0,
                                        0,
                                        0,
                                        -1,
                                        -1,
                                        -1,
                                    ],
                                    "score_dow": {
                                        "monday": 1,
                                        "tuesday": 1,
                                        "wednesday": 1,
                                        "thursday": 0,
                                        "friday": -1,
                                        "saturday": -1,
                                        "sunday": -1,
                                    },
                                    "start": "2016-01-01",
                                    "stop": "2016-01-02",
                                    "level": "versioned-site",
                                    "subscriber_subset": "all",
                                },
                            },
                            "labels": {
                                "evening": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [1e-06, -0.5],
                                            [1e-06, -1.1],
                                            [1.1, -1.1],
                                            [1.1, -0.5],
                                        ]
                                    ],
                                },
                                "day": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [-1.1, -0.5],
                                            [-1.1, 0.5],
                                            [-1e-06, 0.5],
                                            [0, -0.5],
                                        ]
                                    ],
                                },
                            },
                        },
                    },
                },
            },
        ),
    ],
)
def test_construct_query(expected_md5, query_spec):
    """
    Test that expected query objects are constructed by construct_query_object
    """
    obj = construct_query_object(**query_spec)
    assert expected_md5 == obj.md5
