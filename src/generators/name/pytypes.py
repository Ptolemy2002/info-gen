from typing import TypedDict, NotRequired, Literal

class NameArgs(TypedDict):
    file_category: NotRequired[str | None]
    file_type: NotRequired[str | None]
    subdomains: NotRequired[int | None]
    gender: NotRequired[Literal["male", "female", "nb"] | None]
    first_name: NotRequired[str | None]
    last_name: NotRequired[str | None]
    music_genre: NotRequired[str | None]
    music_instrument_category: NotRequired[str | None]
    first_only: NotRequired[bool]
    last_only: NotRequired[bool]
    behind_name_key: NotRequired[str | None]
    usage_type: NotRequired[str | None]