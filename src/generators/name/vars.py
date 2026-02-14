from faker_music.genres import genre_list
from faker_music.instruments import instrument_list

NAME_TYPES = [
    "company",
    "file_name",
    "email",
    "website",
    "user_name",
    "job",
    "person",
    "music_genre",
    "music_instrument",
    "vehicle"
]

FILE_CATEGORIES = [
    "audio",
    "image",
    "office",
    "text",
    "video"
]

EMAIL_CATEGORIES = [
    "company",
    "personal"
]

MUSIC_GENRES = [g["genre"] for g in genre_list]
INSTRUMENT_CATEGORIES = [i["category"] for i in instrument_list]