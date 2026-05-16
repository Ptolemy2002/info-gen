from typing import TypedDict, NotRequired, Literal

class IdentifierArgs(TypedDict):
    first_name: NotRequired[str | None]
    last_name: NotRequired[str | None]
    username: NotRequired[str | None]
    domain: NotRequired[str | None]
    domain_type: NotRequired[Literal["personal", "business"] | None]
    gender: NotRequired[Literal["male", "female", "nb"] | None]
    min: NotRequired[int | None]
    max: NotRequired[int | None]