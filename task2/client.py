from dataclasses import dataclass
from typing import Any

import requests

from config import BASE_URL, REQUEST_TIMEOUT_SECONDS, SUMMARIES_PATH


@dataclass(frozen=True)
class SummariesClient:
    """Thin HTTP wrapper for GET /summaries — no assertions."""

    base_url: str = BASE_URL
    timeout: float = REQUEST_TIMEOUT_SECONDS

    @property
    def endpoint(self) -> str:
        return f"{self.base_url}{SUMMARIES_PATH}"

    def get_summaries(self) -> list[dict[str, Any]]:
        response = requests.get(
            self.endpoint,
            timeout=self.timeout,
            allow_redirects=True,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError("Expected a JSON array from /summaries")
        return payload
