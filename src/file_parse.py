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
    start: int  # start index of the interpolation token in the source text; -1 for programmatic
    end: int    # end index (exclusive); -1 for programmatic
    synthetic: bool = False  # True => token stripped from output (not substituted)
    static: bool = False     # True => raw_args is the literal value, not generator argv


def extract_interpolations(text: str) -> list[Interpolation]:
    """
    Scan *text* for interpolation tokens of the forms::

        {{id: arg1 arg2 ...}}    regular — generator argv, result emitted in place
        {{#id: arg1 arg2 ...}}   synthetic — generator argv, token stripped from output
        {{id = some text}}       static — literal value, result emitted in place
        {{#id = some text}}      synthetic static — literal value, token stripped

    The identifier is one or more word characters (``\\w+``).

    For generator tokens (``:`` separator), everything after the colon is the
    raw args template passed to the generator, either plain args or a template
    containing ``$(other_id)`` references.  Use :func:`resolve_interpolation_args`
    to substitute and split at call time.

    For static tokens (``=`` separator), the text after ``=`` is the value itself
    (not generator argv) and may also contain ``$(other_id)`` references.  Use
    :func:`resolve_static_value` to resolve them.  No generator is invoked.

    Synthetic tokens (``#`` prefix) are executed/resolved normally and their
    results are available for ``$(id)`` references, but
    :func:`apply_interpolations` strips their tokens rather than substituting.

    Rules
    -----
    - The **first** occurrence of an identifier must include a separator and
      content (e.g. ``{{id: args}}`` or ``{{id = value}}``).
    - Subsequent occurrences may omit the separator entirely (``{{id}}`` or
      ``{{#id}}``); they inherit the ``raw_args`` and ``static`` flag of the
      first occurrence.
    - If a later occurrence *does* include a separator, its content and static
      flag must exactly match the first occurrence; a :class:`ValueError` is
      raised on conflict.

    Returns a flat list of :class:`Interpolation` objects in source order,
    one per occurrence (including back-references).
    """
    # Group 1: optional '#' for synthetic; group 2: identifier;
    # group 3: separator ('=' or ':') or None for bare back-refs; group 4: content.
    pattern = re.compile(r'\{\{(#?)(\w+)(?:\s*([=:])\s*(.*?))?\}\}', re.DOTALL)

    seen: dict[str, tuple[str, bool]] = {}  # id -> (canonical raw_args, static)
    result: list[Interpolation] = []

    for match in pattern.finditer(text):
        synthetic = bool(match.group(1))
        ident = match.group(2)
        separator = match.group(3)           # '=', ':', or None
        is_back_ref = separator is None
        static = (separator == '=')
        raw_args = (match.group(4) or '').strip()

        if ident in seen:
            canonical_raw_args, canonical_static = seen[ident]
            if not is_back_ref and (raw_args != canonical_raw_args or static != canonical_static):
                raise ValueError(
                    f"Interpolation id '{ident}' used with conflicting arguments.\n"
                    f"  First use : {canonical_raw_args!r} (static={canonical_static})\n"
                    f"  This use  : {raw_args!r} (static={static})"
                )
            raw_args = canonical_raw_args
            static = canonical_static
        else:
            seen[ident] = (raw_args, static)

        result_deps = _RESULT_REF_PATTERN.findall(raw_args)
        args = [] if static or result_deps else (shlex.split(raw_args) if raw_args else [])

        result.append(Interpolation(
            id=ident,
            raw_args=raw_args,
            result_deps=result_deps,
            args=args,
            start=match.start(),
            end=match.end(),
            synthetic=synthetic,
            static=static,
        ))

    return result


def make_synthetic_interpolation(id: str, raw_args: str) -> Interpolation:
    """
    Programmatically create a synthetic :class:`Interpolation` with no source-text token.

    Equivalent to declaring ``{{#id: raw_args}}`` in the file, except there is
    no token at all — ``start`` and ``end`` are ``-1``.  Results are available
    for ``$(id)`` references in other interpolations and are not emitted by
    :func:`apply_interpolations`.
    """
    result_deps = _RESULT_REF_PATTERN.findall(raw_args)
    args = [] if result_deps else (shlex.split(raw_args) if raw_args else [])
    return Interpolation(
        id=id,
        raw_args=raw_args,
        result_deps=result_deps,
        args=args,
        start=-1,
        end=-1,
        synthetic=True,
    )


def make_static_interpolation(id: str, value: str, synthetic: bool = False) -> Interpolation:
    """
    Programmatically create a static :class:`Interpolation` with a literal value template.

    Equivalent to ``{{id = value}}`` (or ``{{#id = value}}`` when
    *synthetic* is ``True``) in the file, except there is no source token —
    ``start`` and ``end`` are ``-1``.  The value may contain ``$(other_id)``
    result-references resolved via :func:`resolve_static_value`.
    """
    result_deps = _RESULT_REF_PATTERN.findall(value)
    return Interpolation(
        id=id,
        raw_args=value,
        result_deps=result_deps,
        args=[],
        start=-1,
        end=-1,
        synthetic=synthetic,
        static=True,
    )


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


def resolve_static_value(interp: Interpolation, results: dict[str, str]) -> str:
    """
    Resolve ``$(id)`` references in a static interpolation's value template and
    return the final string.

    *results* is a ``{id: resolved_value}`` mapping of already-completed
    generations.  A :class:`KeyError` is raised if a required ID is absent.

    For static interpolations with no ``result_deps`` this returns
    ``interp.raw_args`` directly.
    """
    if not interp.result_deps:
        return interp.raw_args

    value = interp.raw_args
    for dep_id in interp.result_deps:
        value = value.replace(f'$({dep_id})', results[dep_id])
    return value


def apply_interpolations(text: str, values: dict[str, str]) -> str:
    """
    Replace every non-synthetic token in *text* with the corresponding entry
    from *values*, and strip every synthetic token (``{{#id ...}}``).

    *values* is a ``{id: resolved_value}`` mapping — built by running the
    generator (or :func:`resolve_static_value`) for each unique interpolation.

    Regular tokens whose ID is not present in *values* are left unchanged.
    Synthetic tokens are always removed regardless of *values*.
    """
    pattern = re.compile(r'\{\{(#?)(\w+)(?:\s*[=:]\s*.*?)?\}\}', re.DOTALL)

    def replacer(match: re.Match) -> str:
        if match.group(1):  # synthetic — strip
            return ''
        ident = match.group(2)
        return cast(str, values.get(ident, match.group(0)))

    return pattern.sub(replacer, text)
