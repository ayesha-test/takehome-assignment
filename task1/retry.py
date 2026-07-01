import time
from typing import Callable, Optional

import requests

TRANSIENT_STATUS_CODES = {400, 401, 404, 502, 503, 504}


def is_transient_movies_response(response: requests.Response) -> bool:
    if response.status_code in TRANSIENT_STATUS_CODES:
        return True

    if response.headers.get("Content-Type", "").startswith("application/json"):
        try:
            payload = response.json()
        except ValueError:
            return False
        return payload.get("detail") == "Oops!"

    return False


def call_with_retry(
    fn: Callable[[], requests.Response],
    *,
    max_attempts: int = 3,
    pause_seconds: float = 0.5,
) -> requests.Response:
    last_response: Optional[requests.Response] = None

    for attempt in range(1, max_attempts + 1):
        response = fn()
        last_response = response

        if response.ok and not is_transient_movies_response(response):
            return response

        if attempt < max_attempts:
            time.sleep(pause_seconds * attempt)

    assert last_response is not None
    return last_response
