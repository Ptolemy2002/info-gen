from typing import TypedDict, NotRequired, Literal

class NameArgs(TypedDict):
    file_category: NotRequired[str]
    file_type: NotRequired[str]
    email_category: NotRequired[str]
    subdomains: NotRequired[int]
    gender: NotRequired[Literal["male", "female", "nb"]]
    first_name: NotRequired[str]
    last_name: NotRequired[str]
    music_genre: NotRequired[str]
    music_instrument_category: NotRequired[str]