def test_ping_flowmachine_server(send_zmq_message_and_receive_reply):
    """
    Sending the 'ping' action to the flowmachine server evokes a successful 'pong' response.
    """
    msg = {"action": "ping", "request_id": "DUMMY_ID"}
    reply = send_zmq_message_and_receive_reply(msg)
    expected_reply = {"status": "accepted", "msg": "pong", "data": {}}
    assert expected_reply == reply
