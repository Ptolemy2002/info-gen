from typing import TypedDict, NotRequired, Literal

class IdentifierArgs(TypedDict):
    first_name: NotRequired[str]
    last_name: NotRequired[str]
    username: NotRequired[str]
    domain: NotRequired[str]
    domain_type: NotRequired[Literal["personal", "business"]]
    gender: NotRequired[Literal["male", "female", "nb"]]
    min: NotRequired[int]
    max: NotRequired[int]