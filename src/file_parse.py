import re
import shlex
from dataclasses import dataclass
from typing import cast

_RESULT_REF_PATTERN = re.compile(r'\$\((\w+)\)')


@dataclass
class Interpolation:
    id: str
    raw_args: str        # args template; may contain $(other_id) references
    result_deps: list[str]  # IDs referenced via $(id) in raw_args, in order
    args: list[str]      # pre-split args; empty list when result_deps is non-empty
    start: int  # start index of the interpolation token in the source text
    end: int    # end index (exclusive)


def extract_interpolations(text: str) -> list[Interpolation]:
    """
    Scan *text* for interpolation tokens of the form::

        {{identifier: arg1 arg2 ...}}

    The identifier is one or more word characters (``\\w+``).  Everything
    after the colon is the raw args template, which is either:

    - Plain args parsed with :func:`shlex.split` (e.g. ``arg1 "arg two"``).
    - A template containing ``$(other_id)`` references whose values come from
      the results of previously-executed generations.  Use
      :func:`resolve_interpolation_args` to substitute and split these at
      call time.

    Rules
    -----
    - The **first** occurrence of an identifier must include arguments
      (``{{id: arg1 arg2 ...}}``).
    - Subsequent occurrences may omit the argument list entirely, written as
      ``{{id}}``; they are treated as back-references and resolve to the same
      raw args as the first occurrence.
    - If a later occurrence *does* include arguments they must exactly match
      the raw args string of the first occurrence; a :class:`ValueError` is
      raised on conflict.

    All returned :class:`Interpolation` objects carry the canonical ``raw_args``
    from the first occurrence, so callers need no special handling for
    back-references.

    Returns a flat list of :class:`Interpolation` objects in source order,
    one per occurrence (including back-references).
    """
    # The args group (after the colon) is optional to support bare {{id}} back-references.
    pattern = re.compile(r'\{\{(\w+)(?::\s*(.*?))?\}\}', re.DOTALL)

    seen: dict[str, str] = {}   # id -> canonical raw_args
    result: list[Interpolation] = []

    for match in pattern.finditer(text):
        ident = match.group(1)
        raw_args = (match.group(2) or '').strip()
        is_back_ref = match.group(2) is None  # colon+args group was absent

        if ident in seen:
            if not is_back_ref and raw_args != seen[ident]:
                raise ValueError(
                    f"Interpolation id '{ident}' used with conflicting arguments.\n"
                    f"  First use : {seen[ident]!r}\n"
                    f"  This use  : {raw_args!r}"
                )
            raw_args = seen[ident]
        else:
            seen[ident] = raw_args

        result_deps = _RESULT_REF_PATTERN.findall(raw_args)
        args = [] if result_deps else (shlex.split(raw_args) if raw_args else [])

        result.append(Interpolation(
            id=ident,
            raw_args=raw_args,
            result_deps=result_deps,
            args=args,
            start=match.start(),
            end=match.end(),
        ))

    return result


def resolve_interpolation_args(interp: Interpolation, results: dict[str, str]) -> list[str]:
    """
    Substitute ``$(id)`` references in *interp*'s args template and return
    the shlex-split argument list.

    *results* is a ``{id: resolved_value}`` mapping of already-completed
    generations.  A :class:`KeyError` is raised if a required ID is absent.

    For interpolations with no ``result_deps`` this is equivalent to
    returning ``interp.args`` directly.
    """
    if not interp.result_deps:
        return interp.args

    raw = interp.raw_args
    for dep_id in interp.result_deps:
        raw = raw.replace(f'$({dep_id})', results[dep_id])

    return shlex.split(raw) if raw else []


def unique_interpolations(interpolations: list[Interpolation]) -> dict[str, list[str]]:
    """
    Collapse a list returned by :func:`extract_interpolations` into a
    ``{id: args}`` mapping containing only one entry per identifier.

    **Note:** for interpolations that contain ``$(id)`` result-references,
    ``args`` will be an empty list.  Use :func:`unique_interpolation_map` and
    :func:`resolve_interpolation_args` instead when result-references are
    present.
    """
    return {interp.id: interp.args for interp in interpolations}


def unique_interpolation_map(interpolations: list[Interpolation]) -> dict[str, Interpolation]:
    """
    Collapse a list returned by :func:`extract_interpolations` into a
    ``{id: Interpolation}`` mapping containing only one entry per identifier.

    Use this in preference to :func:`unique_interpolations` when you need
    access to ``raw_args``, ``result_deps``, or
    :func:`resolve_interpolation_args`.
    """
    return {interp.id: interp for interp in interpolations}


def apply_interpolations(text: str, values: dict[str, str]) -> str:
    """
    Replace every ``{{id: ...}}`` token in *text* with the corresponding
    entry from *values*.

    *values* is a ``{id: resolved_value}`` mapping — typically built by
    calling ``parse_args`` / ``main_exec`` for each entry returned by
    :func:`unique_interpolation_map` and taking the first result.

    Tokens whose ID is not present in *values* are left unchanged.
    """
    pattern = re.compile(r'\{\{(\w+)(?::\s*.*?)?\}\}', re.DOTALL)

    def replacer(match: re.Match) -> str:
        ident = match.group(1)
        return cast(str, values.get(ident, match.group(0)))

    return pattern.sub(replacer, text)
