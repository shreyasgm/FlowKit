from quart import request
from quart.exceptions import HTTPException


async def get_params_from_flowmachine(*, query_id) -> dict:
    """
    Get the parameters of a query from flowmachine.

    Parameters
    ----------
    query_id : str
        ID of the query to get params for

    Returns
    -------
    dict
        Dictionary containing the query's original parameters

    Raises
    ------
    HTTPException
        404 if the query id is not known.

    """
    request.socket.send_json(
        {
            "request_id": request.request_id,
            "action": "get_query_params",
            "params": {"query_id": query_id},
        }
    )
    reply = await request.socket.recv_json()
    if reply["status"] == "error":
        raise HTTPException(
            description=f"Unknown query ID '{query_id}'",
            name="Query ID not found",
            status_code=404,
        )
    return reply["payload"]["query_params"]
