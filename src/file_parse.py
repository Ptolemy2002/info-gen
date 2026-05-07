import re
import shlex
from dataclasses import dataclass
from typing import cast


@dataclass
class Interpolation:
    id: str
    args: list[str]
    start: int  # start index of the interpolation token in the source text
    end: int    # end index (exclusive)


def extract_interpolations(text: str) -> list[Interpolation]:
    """
    Scan *text* for interpolation tokens of the form::

        {{identifier: arg1 arg2 ...}}

    The identifier is one or more word characters (``\\w+``).  Everything
    after the colon is parsed with :func:`shlex.split` so quoted strings and
    escape sequences work exactly as they do on the command line.

    Rules
    -----
    - The **first** occurrence of an identifier must include arguments
      (``{{id: arg1 arg2 ...}}``).
    - Subsequent occurrences may omit the argument list entirely, written as
      ``{{id}}``; they are treated as back-references and resolve to the same
      args as the first occurrence.
    - If a later occurrence *does* include arguments they must exactly match
      the first occurrence; a :class:`ValueError` is raised on conflict.

    All returned :class:`Interpolation` objects carry the canonical ``args``
    from the first occurrence, so callers need no special handling for
    back-references.

    Returns a flat list of :class:`Interpolation` objects in source order,
    one per occurrence (including back-references).
    """
    # The args group (after the colon) is optional to support bare {{id}} back-references.
    pattern = re.compile(r'\{\{(\w+)(?::\s*(.*?))?\}\}', re.DOTALL)

    seen: dict[str, list[str]] = {}   # id -> canonical args
    result: list[Interpolation] = []

    for match in pattern.finditer(text):
        ident = match.group(1)
        raw_args = (match.group(2) or '').strip()
        args = shlex.split(raw_args) if raw_args else []
        is_back_ref = match.group(2) is None  # colon+args group was absent

        if ident in seen:
            if not is_back_ref and args != seen[ident]:
                raise ValueError(
                    f"Interpolation id '{ident}' used with conflicting arguments.\n"
                    f"  First use : {seen[ident]}\n"
                    f"  This use  : {args}"
                )
            args = seen[ident]
        else:
            seen[ident] = args

        result.append(Interpolation(
            id=ident,
            args=args,
            start=match.start(),
            end=match.end(),
        ))

    return result


def unique_interpolations(interpolations: list[Interpolation]) -> dict[str, list[str]]:
    """
    Collapse a list returned by :func:`extract_interpolations` into a
    ``{id: args}`` mapping containing only one entry per identifier.

    Useful when you want to call ``main_exec`` once per unique ID and then
    substitute all occurrences.
    """
    return {interp.id: interp.args for interp in interpolations}


def apply_interpolations(text: str, values: dict[str, str]) -> str:
    """
    Replace every ``{{id: ...}}`` token in *text* with the corresponding
    entry from *values*.

    *values* is a ``{id: resolved_value}`` mapping — typically built by
    calling ``parse_args`` / ``main_exec`` for each entry returned by
    :func:`unique_interpolations` and taking the first result.

    Tokens whose ID is not present in *values* are left unchanged.
    """
    pattern = re.compile(r'\{\{(\w+)(?::\s*.*?)?\}\}', re.DOTALL)

    def replacer(match: re.Match) -> str:
        ident = match.group(1)
        return cast(str, values.get(ident, match.group(0)))

    return pattern.sub(replacer, text)
