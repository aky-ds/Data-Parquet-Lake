"""Normalize, convert, and enrich records."""

from datetime import UTC, datetime
from hashlib import sha256
import json
import re


def normalize_header(header):
    """Convert a header to lowercase snake_case."""

    value = str(header).strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)

    return value.strip("_")


def normalize_headers(record):
    """Normalize every key and detect naming collisions."""

    cleaned = {}

    for key, value in record.items():
        new_key = normalize_header(key)

        if not new_key:
            raise ValueError(
                f"Column name {key!r} becomes empty."
            )

        if new_key in cleaned:
            raise ValueError(
                f"Duplicate normalized column: {new_key}"
            )

        cleaned[new_key] = value

    return cleaned


def coerce_value(value, data_type):
    """Convert a value to its configured type."""

    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if value == "":
            return None

    if data_type == "string":
        return str(value)

    if data_type == "int":
        number = float(value)

        if not number.is_integer():
            raise ValueError(
                f"Expected integer, received {value!r}"
            )

        return int(number)

    if data_type == "float":
        return float(value)

    if data_type == "bool":
        normalized = str(value).strip().lower()

        if normalized in {"true", "1", "yes", "y"}:
            return True

        if normalized in {"false", "0", "no", "n"}:
            return False

        raise ValueError(
            f"Expected boolean, received {value!r}"
        )

    if data_type == "datetime":
        parsed = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)

        return parsed.astimezone(UTC).isoformat()

    raise ValueError(f"Unsupported type: {data_type}")


def coerce_record(record, schema):
    """Apply the configured data types."""

    cleaned = dict(record)

    for column, rules in schema.items():
        try:
            cleaned[column] = coerce_value(
                cleaned.get(column),
                rules["type"],
            )
        except (ValueError, TypeError, OverflowError) as exc:
            raise ValueError(
                f"Column '{column}': {exc}"
            ) from exc

    return cleaned


def generate_record_id(record):
    """Generate a deterministic identifier."""

    payload = json.dumps(
        record,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
        separators=(",", ":"),
    )

    return sha256(payload.encode("utf-8")).hexdigest()


def enrich_record(record, project_title):
    """Add the record ID and processing metadata."""

    cleaned = dict(record)

    # Hash only the normalized source fields.
    cleaned["record_id"] = generate_record_id(cleaned)

    cleaned["processed_at"] = (
        datetime.now(UTC).isoformat()
    )

    cleaned["project"] = project_title

    return cleaned