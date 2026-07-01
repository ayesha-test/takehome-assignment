import pytest

from client import MoviesClient
from config import CATALOGUE_FETCH_LIMIT


@pytest.fixture(scope="session")
def movies_client() -> MoviesClient:
    return MoviesClient()


@pytest.fixture(scope="session")
def warm_api(movies_client: MoviesClient) -> None:
    """Prime Cloud Run instance before latency-sensitive tests."""
    response = movies_client.get_movies(limit=1, retry=True)
    response.raise_for_status()


@pytest.fixture(scope="session")
def catalogue_snapshot(movies_client: MoviesClient, warm_api: None) -> dict:
    response = movies_client.get_movies(limit=CATALOGUE_FETCH_LIMIT, retry=True)
    response.raise_for_status()
    return response.json()
