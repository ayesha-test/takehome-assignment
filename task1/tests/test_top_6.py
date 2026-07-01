"""Six automated checks for GET /movies/."""

from typing import Optional

import pytest
from jsonschema import ValidationError

from client import MoviesClient
from config import MAX_RESPONSE_TIME_SECONDS
from retry import is_transient_movies_response
from validators import (
    assert_movie_domain_rules,
    assert_no_duplicate_ids,
    assert_pagination_invariants,
    format_validation_error,
    validate_paginated_movies,
)


def _fetch(client: MoviesClient, **params) -> dict:
    """GET /movies/ with retry (functional tests only — not used for reliability)."""
    response = client.get_movies(retry=True, **params)
    response.raise_for_status()
    return response.json()


def _check_page(payload: dict, *, limit: Optional[int] = None) -> None:
    """Contract + pagination invariants + domain rules for one page."""
    try:
        validate_paginated_movies(payload)
    except ValidationError as exc:
        pytest.fail(format_validation_error(exc))
    assert_pagination_invariants(payload, limit=limit)
    for movie in payload["items"]:
        errors = assert_movie_domain_rules(movie)
        assert not errors, f"Movie {movie.get('id')}: {errors}"


# --- 1. Contract validation ---


def test_contract_validation(movies_client: MoviesClient, warm_api: None) -> None:
    payload = _fetch(movies_client)
    _check_page(payload, limit=10)


# --- 2. Pagination invariants ---


def test_pagination_invariants(movies_client: MoviesClient, warm_api: None) -> None:
    page_limit = 10
    last_page_skip = 30
    pages = [
        _fetch(movies_client, skip=skip, limit=page_limit)
        for skip in (0, 10, last_page_skip)
    ]
    totals = {page["total"] for page in pages}
    assert len(totals) == 1, f"total changed across pages: {totals}"

    ids_page_1 = {m["id"] for m in pages[0]["items"]}
    ids_page_2 = {m["id"] for m in pages[1]["items"]}
    assert ids_page_1.isdisjoint(ids_page_2), "page 1 and page 2 share movie IDs"

    total = pages[0]["total"]
    expected_last_page = min(page_limit, max(0, total - last_page_skip))
    assert len(pages[2]["items"]) == expected_last_page, (
        f"last page item count wrong (skip={last_page_skip}, limit={page_limit}, total={total})"
    )

    beyond = _fetch(movies_client, skip=100)
    assert beyond["items"] == []
    assert beyond["total"] == total


# --- 3. Data integrity ---


def test_data_integrity(catalogue_snapshot: dict) -> None:
    _check_page(catalogue_snapshot, limit=100)
    assert_no_duplicate_ids(catalogue_snapshot["items"])
    assert len(catalogue_snapshot["items"]) == catalogue_snapshot["total"]


# --- 4. Search behaviour ---


def test_search_behaviour(
    movies_client: MoviesClient,
    catalogue_snapshot: dict,
    warm_api: None,
) -> None:
    payload = _fetch(movies_client, query="Godfather")
    _check_page(payload)

    page_limit = 10
    assert payload["total"] >= 1
    assert any("Godfather" in movie["title"] for movie in payload["items"])
    assert payload["total"] >= len(payload["items"])
    if len(payload["items"]) < page_limit:
        assert payload["total"] == len(payload["items"]), (
            "when all filtered results fit on one page, total should match len(items)"
        )
    assert payload["total"] < catalogue_snapshot["total"], "search total should be less than full catalogue"


# --- 5. Reliability probe (no retries) ---


@pytest.mark.reliability
def test_reliability_probe(movies_client: MoviesClient, warm_api: None) -> None:
    # CI probe: 20 requests (fast). Strategy §2.4 soak gate: 50 requests / 10 min.
    sample_size = 20
    oops_count = sum(
        1
        for _ in range(sample_size)
        if is_transient_movies_response(movies_client.get_movies(limit=1))
    )

    rate = oops_count / sample_size
    max_rate = 0.001  # 0.1% release gate (strategy §1.1 criterion 7, §2.4 step 4)
    assert rate <= max_rate, (
        f"'Oops!' rate {rate:.1%} ({oops_count}/{sample_size}) exceeds {max_rate:.1%} threshold"
    )


# --- 6. Performance smoke ---


@pytest.mark.performance
def test_performance_smoke(movies_client: MoviesClient, warm_api: None) -> None:
    movies_client.get_movies(limit=1, retry=True)  # warm within test

    response = movies_client.get_movies(limit=10, retry=True)
    assert response.status_code == 200
    elapsed = response.elapsed.total_seconds()
    assert elapsed <= MAX_RESPONSE_TIME_SECONDS, (
        f"Warm response took {elapsed:.3f}s; limit is {MAX_RESPONSE_TIME_SECONDS}s"
    )
