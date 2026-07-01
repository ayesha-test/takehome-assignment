import re
from typing import Any, Optional
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, ValidationError

UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

PAGINATED_MOVIES_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["total", "items"],
    "additionalProperties": False,
    "properties": {
        "total": {"type": "integer"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "title", "description", "image_url", "rating"],
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "title": {"type": "string", "minLength": 1},
                    "description": {"type": "string", "minLength": 1},
                    "image_url": {"type": "string", "minLength": 1},
                    "rating": {"type": "number"},
                },
            },
        },
    },
}

_paginated_validator = Draft202012Validator(PAGINATED_MOVIES_SCHEMA)


def validate_paginated_movies(payload: dict[str, Any]) -> None:
    _paginated_validator.validate(payload)


def assert_movie_domain_rules(movie: dict[str, Any]) -> list[str]:
    violations: list[str] = []

    movie_id = movie.get("id", "")
    if not UUID_PATTERN.match(movie_id):
        violations.append(f"id '{movie_id}' is not a UUID")

    for field in ("title", "description"):
        value = movie.get(field, "")
        if not isinstance(value, str) or not value.strip():
            violations.append(f"{field} must be a non-empty string")

    image_url = movie.get("image_url", "")
    parsed = urlparse(image_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        violations.append(f"image_url '{image_url}' is not an absolute http(s) URL")

    rating = movie.get("rating")
    if not isinstance(rating, (int, float)):
        violations.append("rating must be numeric")
    elif rating < 0 or rating > 10:
        violations.append(f"rating {rating} is outside expected range [0, 10]")

    return violations


def assert_no_duplicate_ids(movies: list[dict[str, Any]]) -> None:
    ids = [movie["id"] for movie in movies]
    if len(ids) != len(set(ids)):
        duplicates = sorted({movie_id for movie_id in ids if ids.count(movie_id) > 1})
        raise AssertionError(f"Duplicate movie IDs found: {duplicates}")


def assert_pagination_invariants(payload: dict[str, Any], *, limit: Optional[int]) -> None:
    total = payload["total"]
    items = payload["items"]

    if total < 0:
        raise AssertionError(f"total must be non-negative, got {total}")

    if limit is not None and len(items) > limit:
        raise AssertionError(
            f"items length {len(items)} exceeds requested limit {limit}",
        )

    if len(items) > total:
        raise AssertionError(
            f"items length {len(items)} exceeds catalogue total {total}",
        )


def format_validation_error(error: ValidationError) -> str:
    path = ".".join(str(part) for part in error.absolute_path) or "<root>"
    return f"{path}: {error.message}"
