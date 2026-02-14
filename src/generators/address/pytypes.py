from typing import TypedDict, NotRequired

class AddressArgs(TypedDict):
    building_number: NotRequired[str | None]
    street: NotRequired[str | None]
    city: NotRequired[str | None]
    state: NotRequired[str | None]
    zip: NotRequired[str | None]