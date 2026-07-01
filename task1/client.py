from dataclasses import dataclass
from typing import Any, Optional

import requests

from config import BASE_URL, MOVIES_PATH, REQUEST_TIMEOUT_SECONDS
from retry import call_with_retry


@dataclass(frozen=True)
class MoviesClient:
    """Thin HTTP wrapper for GET /movies/ — no assertions."""

    base_url: str = BASE_URL
    timeout: float = REQUEST_TIMEOUT_SECONDS

    @property
    def endpoint(self) -> str:
        return f"{self.base_url}{MOVIES_PATH}"

    def get_movies(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        query: Optional[str] = None,
        retry: bool = False,
    ) -> requests.Response:
        params: dict[str, Any] = {}
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit
        if query is not None:
            params["query"] = query

        def _request() -> requests.Response:
            return requests.get(
                self.endpoint,
                params=params or None,
                timeout=self.timeout,
            )

        if retry:
            return call_with_retry(_request)

        return _request()
