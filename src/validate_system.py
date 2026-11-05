#!/usr/bin/env python3
"""Validate a P2 system model against JSON Schema and graph-level rules.

The validator performs two stages:

1. JSON Schema validation using ``schema/system.schema.json``.
2. Semantic validation of the graph represented by ``elements``,
   ``relationships`` and ``flows``.

Typical usage from the repository root::

    python src/validate_system.py cases/case_01/system.json

A different schema can be supplied explicitly::

    python src/validate_system.py path/to/system.json \
        --schema path/to/system.schema.json

Exit codes:
    0 - the system model is valid;
    1 - schema or graph validation failed;
    2 - the input, schema or validator configuration could not be loaded.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from jsonschema import FormatChecker
    from jsonschema.exceptions import SchemaError
    from jsonschema.validators import validator_for
except ImportError:  # pragma: no cover - handled explicitly in main()
    FormatChecker = None  # type: ignore[assignment]
    SchemaError = Exception  # type: ignore[assignment,misc]
    validator_for = None  # type: ignore[assignment]


EXIT_VALID = 0
EXIT_INVALID = 1
EXIT_OPERATIONAL_ERROR = 2

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A single deterministic validation error or warning."""

    code: str
    path: str
    message: str

    def render(self) -> str:
        return f"[{self.code}] {self.path}: {self.message}"


@dataclass(frozen=True, slots=True)
class GraphValidationResult:
    """Semantic validation outcome."""

    errors: tuple[ValidationIssue, ...]
    warnings: tuple[ValidationIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def _json_path(parts: Iterable[Any]) -> str:
    """Convert jsonschema path components to a readable JSONPath-like string."""

    result = "$"
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        elif isinstance(part, str) and _IDENTIFIER_RE.fullmatch(part):
            result += f".{part}"
        else:
            encoded = json.dumps(str(part), ensure_ascii=False)
            result += f"[{encoded}]"
    return result


def _load_json(path: Path, label: str) -> Any:
    """Load a UTF-8 JSON file and raise a concise ValueError on failure."""

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Cannot read {label} '{path}': {exc}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        location = f"line {exc.lineno}, column {exc.colno}"
        raise ValueError(
            f"Invalid JSON in {label} '{path}' at {location}: {exc.msg}"
        ) from exc


def validate_against_schema(
    instance: Any,
    schema: Mapping[str, Any],
) -> tuple[ValidationIssue, ...]:
    """Validate *instance* using the draft declared by *schema*."""

    if validator_for is None or FormatChecker is None:
        raise RuntimeError(
            "Missing dependency 'jsonschema'. Install it with: "
            "python -m pip install 'jsonschema>=4.18,<5'"
        )

    validator_class = validator_for(schema)
    validator_class.check_schema(schema)
    validator = validator_class(schema, format_checker=FormatChecker())

    issues: list[ValidationIssue] = []
    for error in sorted(
        validator.iter_errors(instance),
        key=lambda item: (_json_path(item.absolute_path), item.message),
    ):
        issues.append(
            ValidationIssue(
                code="SCHEMA",
                path=_json_path(error.absolute_path),
                message=error.message,
            )
        )

    return tuple(issues)


def _as_record_list(value: Any) -> list[Mapping[str, Any]]:
    """Return mappings from a list, ignoring malformed items safely.

    Malformed structures are reported by JSON Schema validation. This helper keeps
    semantic validation defensive and prevents secondary exceptions.
    """

    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _element_index(
    elements: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Mapping[str, Any]], list[ValidationIssue]]:
    """Build an element index and report duplicate identifiers."""

    index: dict[str, Mapping[str, Any]] = {}
    first_position: dict[str, int] = {}
    issues: list[ValidationIssue] = []

    for position, element in enumerate(elements):
        element_id = element.get("id")
        if not isinstance(element_id, str) or not element_id:
            # Missing/invalid IDs are schema errors, so avoid duplicating messages.
            continue

        if element_id in index:
            issues.append(
                ValidationIssue(
                    code="DUPLICATE_ELEMENT_ID",
                    path=f"$.elements[{position}].id",
                    message=(
                        f"element ID {element_id!r} is duplicated; first occurrence "
                        f"is at $.elements[{first_position[element_id]}].id"
                    ),
                )
            )
            continue

        index[element_id] = element
        first_position[element_id] = position

    return index, issues


def _validate_endpoint_references(
    records: Sequence[Mapping[str, Any]],
    collection_name: str,
    element_ids: set[str],
) -> list[ValidationIssue]:
    """Verify that every source and target refers to an existing element."""

    issues: list[ValidationIssue] = []

    for position, record in enumerate(records):
        for field in ("source", "target"):
            reference = record.get(field)
            if not isinstance(reference, str) or not reference:
                # Missing/invalid references are handled by JSON Schema.
                continue

            if reference not in element_ids:
                issues.append(
                    ValidationIssue(
                        code="UNKNOWN_ELEMENT_REFERENCE",
                        path=f"$.{collection_name}[{position}].{field}",
                        message=f"references unknown element ID {reference!r}",
                    )
                )

    return issues


def _find_disconnected_elements(
    elements: Sequence[Mapping[str, Any]],
    relationships: Sequence[Mapping[str, Any]],
    flows: Sequence[Mapping[str, Any]],
) -> list[ValidationIssue]:
    """Return warnings for components/processes absent from all graph edges.

    Resources and trust boundaries are intentionally excluded because the current
    P2 schema does not require them to be graph endpoints.
    """

    connected_ids: set[str] = set()
    for record in (*relationships, *flows):
        for field in ("source", "target"):
            value = record.get(field)
            if isinstance(value, str) and value:
                connected_ids.add(value)

    warnings: list[ValidationIssue] = []
    for position, element in enumerate(elements):
        element_id = element.get("id")
        element_type = element.get("type")

        if (
            isinstance(element_id, str)
            and element_id
            and element_type in {"component", "process"}
            and element_id not in connected_ids
        ):
            warnings.append(
                ValidationIssue(
                    code="DISCONNECTED_ELEMENT",
                    path=f"$.elements[{position}]",
                    message=(
                        f"{element_type} {element_id!r} does not participate in any "
                        "relationship or flow"
                    ),
                )
            )

    return warnings


def validate_graph(
    instance: Mapping[str, Any],
    *,
    check_disconnected: bool = False,
) -> GraphValidationResult:
    """Validate graph-level invariants not expressible in JSON Schema.

    Current invariants:
      * element identifiers are unique;
      * every ``source`` and ``target`` in relationships resolves to an element;
      * every ``source`` and ``target`` in flows resolves to an element;
      * optionally, disconnected components/processes are reported as warnings.
    """

    elements = _as_record_list(instance.get("elements"))
    relationships = _as_record_list(instance.get("relationships"))
    flows = _as_record_list(instance.get("flows"))

    element_index, errors = _element_index(elements)
    element_ids = set(element_index)

    errors.extend(
        _validate_endpoint_references(
            relationships,
            collection_name="relationships",
            element_ids=element_ids,
        )
    )
    errors.extend(
        _validate_endpoint_references(
            flows,
            collection_name="flows",
            element_ids=element_ids,
        )
    )

    warnings: list[ValidationIssue] = []
    if check_disconnected:
        warnings.extend(_find_disconnected_elements(elements, relationships, flows))

    return GraphValidationResult(
        errors=tuple(sorted(errors, key=lambda issue: (issue.path, issue.code))),
        warnings=tuple(sorted(warnings, key=lambda issue: (issue.path, issue.code))),
    )


def _default_schema_path() -> Path:
    """Resolve ``schema/system.schema.json`` relative to the repository root."""

    return Path(__file__).resolve().parents[1] / "schema" / "system.schema.json"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a P2 system model against system.schema.json and semantic "
            "graph constraints."
        )
    )
    parser.add_argument(
        "system_file",
        type=Path,
        help="path to the system model JSON file",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=_default_schema_path(),
        help=(
            "path to system.schema.json "
            "(default: schema/system.schema.json relative to the repository root)"
        ),
    )
    parser.add_argument(
        "--check-disconnected",
        action="store_true",
        help=(
            "report components and processes that do not participate in any "
            "relationship or flow; these are warnings and do not invalidate the model"
        ),
    )
    return parser


def _print_issues(issues: Sequence[ValidationIssue]) -> None:
    for issue in issues:
        print(f"  - {issue.render()}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        instance = _load_json(args.system_file, "system model")
        schema = _load_json(args.schema, "JSON Schema")
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    if not isinstance(schema, Mapping):
        print("ERROR: JSON Schema root must be an object.", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    try:
        schema_issues = validate_against_schema(instance, schema)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR
    except SchemaError as exc:
        print(f"ERROR: Invalid JSON Schema: {exc.message}", file=sys.stderr)
        return EXIT_OPERATIONAL_ERROR

    if schema_issues:
        print(f"Schema validation: FAILED ({len(schema_issues)} error(s))")
        _print_issues(schema_issues)
        print("Graph validation: SKIPPED")
        print("System model is invalid.")
        return EXIT_INVALID

    print("Schema validation: PASSED")

    if not isinstance(instance, Mapping):
        # This should normally be impossible after successful schema validation,
        # but keep the semantic stage safe for non-object custom schemas.
        print("Graph validation: FAILED (1 error)")
        print("  - [GRAPH_ROOT] $: system model root must be an object")
        print("System model is invalid.")
        return EXIT_INVALID

    graph_result = validate_graph(
        instance,
        check_disconnected=args.check_disconnected,
    )

    if graph_result.errors:
        print(f"Graph validation: FAILED ({len(graph_result.errors)} error(s))")
        _print_issues(graph_result.errors)
        if graph_result.warnings:
            print(f"Warnings ({len(graph_result.warnings)}):")
            _print_issues(graph_result.warnings)
        print("System model is invalid.")
        return EXIT_INVALID

    print("Graph validation: PASSED")
    if graph_result.warnings:
        print(f"Warnings ({len(graph_result.warnings)}):")
        _print_issues(graph_result.warnings)

    print("System model is valid.")
    return EXIT_VALID


if __name__ == "__main__":
    raise SystemExit(main())
