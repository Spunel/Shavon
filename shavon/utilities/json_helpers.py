from typing import Any

import sanic
from sanic.response.types import JSONResponse


# AJAX HELPERS
def basic_json(
    status: str, 
    **kwargs: dict[str: Any],
) -> dict[str: Any]:

    """
    Build and return a basic json message
    """
    return {"status": status, **kwargs}


def fail_json(
    **kwargs: dict[str, Any],
) -> dict[str, Any]:
    """
    Build and return a json fail message.
    """
    return basic_json("fail", **kwargs)


def ok_json(**kwargs: dict[str, Any]) -> dict[str, Any]:
    """
    Build and return a json fail message.
    """
    return basic_json("ok", **kwargs)


def fail_response(
    **kwargs: dict[str, Any],
) -> JSONResponse:
    """
    Build and return a json fail message.
    """
    json_response = fail_json(**kwargs)
    return sanic.json(json_response)


def ok_response(**kwargs: dict[str, Any],) -> JSONResponse:
    """
    Build and return a json fail message.
    """
    json_response = ok_json(**kwargs)
    return sanic.json(json_response)

