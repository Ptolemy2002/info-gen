import random
from fake import get_fake
from faker_music.genres import genre_list
from faker_music.instruments import instrument_list
from .vars import *
from .pytypes import *

def gen_name(type, args: NameArgs, log: bool = False) -> str:
    fake = get_fake()

    match type:
        case "company":
            return fake.company()
        case "file_name":
            category = args.get("file_category")
            file_type = args.get("file_type")

            if file_type is not None:
                if log and category is not None:
                    print(f"Both file category '{category}' and file type '{file_type}' were provided. The file type will be used for generation, and the category will be ignored.")

                return fake.file_name(extension=file_type)
            
            if category is not None:
                if category not in FILE_CATEGORIES:
                    if log: print(f"Provided file category '{category}' is not valid. Generating a random file name without a category.")
                    category = None
                else:
                    if log: print(f"Generating a file name with category '{category}'.")
            else:
                if log: print("No file category or type provided. Generating a random file category.")
                category = random.choice(FILE_CATEGORIES)
                if log: print(f"Selected file category '{category}'.")

            return fake.file_name(category=category)
        case "email":
            category = args.get("email_category")
            if category is not None:
                if category not in EMAIL_CATEGORIES:
                    if log: print(f"Provided email category '{category}' is not valid. Generating a random email without a category.")
                    category = None
                else:
                    if log: print(f"Generating an email with category '{category}'.")
            else:
                if log: print("No email category provided. Generating a random email category.")
                category = random.choice(EMAIL_CATEGORIES)
                if log: print(f"Selected email category '{category}'.")

            if category == "personal":
                return fake.ascii_email()
            else:
                return fake.company_email()
        case "website":
            subdomains = args.get("subdomains", 0)
            if log: print(f"Generating a website with {subdomains} subdomains.")
            return fake.domain_name(subdomains)
        case "user_name":
            return fake.user_name()
        case "job":
            gender = args.get("gender", "nb")

            if gender == "nb":
                if log: print("No specified gender. Generating a random job title with a random gender.")
                gender = random.choice(["male", "female"])

            if log: print(f"Generating a job title for gender '{gender}'.")

            if gender == "male":
                return fake.job_male()
            elif gender == "female":
                return fake.job_female()
        case "person":
            first_name = args.get("first_name")
            last_name = args.get("last_name")
            gender = args.get("gender")

            if gender is None:
                if log: print("No specified gender. Generating a random gender for the person.")
                gender = random.choice(["male", "female", "nb"])
            
            used_first_name: str | None = None
            used_last_name: str | None = None

            if first_name is not None:
                used_first_name = first_name
                if log: print(f"Using provided first name '{first_name}'.")
            else:
                if log: print(f"No first name provided. Generating a random first name with gender '{gender}'.")
                if gender == "nb":
                    used_first_name = fake.first_name_nonbinary()
                elif gender == "male":
                    used_first_name = fake.first_name_male()
                elif gender == "female":
                    used_first_name = fake.first_name_female()

            if last_name is not None:
                used_last_name = last_name
                if log: print(f"Using provided last name '{last_name}'.")
            else:
                if log: print(f"No last name provided. Generating a random last name with gender '{gender}'.")
                if gender == "nb":
                    used_last_name = fake.last_name_nonbinary()
                elif gender == "male":
                    used_last_name = fake.last_name_male()
                elif gender == "female":
                    used_last_name = fake.last_name_female()

            return f"{used_first_name} {used_last_name}"
        case "music_genre":
            genre = args.get("music_genre")
            if genre is not None:
                if genre not in MUSIC_GENRES:
                    if log: print(f"Provided parent music genre '{genre}' is not valid. Generating a random music genre.")
                    genre = None
                else:
                    if log: print(f"Generating a music genre from the parent genre '{genre}'.")

            if genre is None:
                if log: print("No parent music genre provided. Generating a random music genre.")
                genre = random.choice(MUSIC_GENRES)
                if log: print(f"Selected parent music genre '{genre}'.")

            # Get the subgenres for the selected genre
            subgenres: list[str] = []
            for g in genre_list:
                if g["genre"].lower() == genre.lower():
                    subgenres = g["subgenres"]
                    break

            if log: print(f"Found {len(subgenres)} subgenres for parent genre '{genre}'.")
            return random.choice(subgenres) if subgenres else genre
        case "music_instrument":
            category = args.get("music_instrument_category")
            if category is not None:
                if category not in INSTRUMENT_CATEGORIES:
                    if log: print(f"Provided music instrument category '{category}' is not valid. Generating a random music instrument.")
                    category = None
                else:
                    if log: print(f"Generating a music instrument from the category '{category}'.")

            if category is None:
                if log: print("No music instrument category provided. Generating a random music instrument category.")
                category = random.choice(INSTRUMENT_CATEGORIES)
                if log: print(f"Selected music instrument category '{category}'.")

            # Get the instruments for the selected category
            instruments: list[str] = []
            for i in instrument_list:
                if i["category"].lower() == category.lower():
                    instruments = i["instruments"]
                    break

            if log: print(f"Found {len(instruments)} instruments for category '{category}'.")
            return random.choice(instruments)
        case "vehicle":
            return fake.vehicle_year_make_model()
        
    raise ValueError(f"Invalid name type '{type}'. Valid types are: {', '.join(NAME_TYPES)}.")
    
