from fake import get_fake
from generators import gen_name, NameArgs, gen_number
from typing import cast
from utils import to_casing, CASING_TYPES, value_or_default
import random
from .pytypes import IdentifierArgs
from .vars import USER_NAME_SCHEMES

def gen_identifier(type: str, args: IdentifierArgs, log: bool = False) -> str:
    fake = get_fake()

    match type:
        case "email":
            username = args.get("username")

            if username is None:
                if log: print("No user name provided. Generating a random user name for the email.")
                username = gen_identifier("username", args, log)
            
            domain = args.get("domain")
            domain_type = args.get("domain_type")

            if domain is None:
                if log: print("No domain provided. Generating a random domain for the email.")
                if domain_type is None:
                    domain_type = random.choice(["personal", "business"])
                    if log: print(f"No domain type provided. Randomly selected domain type: '{domain_type}'")

                if domain_type == "personal":
                    domain = fake.free_email_domain()
                    if log: print(f"Generated personal domain: '{domain}'")
                else:
                    domain = fake.domain_name()
                    if log: print(f"Generated business domain: '{domain}'")

            return f"{username}@{domain}"

        case "username":
            if args.get("first_name") is None or args.get("last_name") is None:
                if log: print("Either first name or last name is missing. Delegating to gen_name for generation of the missing name components.")

                name_args = cast(NameArgs, {
                    "first_name": args.get("first_name"),
                    "last_name": args.get("last_name"),
                    "gender": args.get("gender")
                })

                first_name, last_name = gen_name("person", name_args, False).split(" ")

                args["first_name"] = first_name
                args["last_name"] = last_name

                if log: print(f"Using first name '{first_name}' and last name '{last_name}' for username generation.")

            scheme = random.choice(USER_NAME_SCHEMES)
            if log: print(f"Selected username scheme: '{scheme}'")

            first_name = value_or_default(args, "first_name", "")
            last_name = value_or_default(args, "last_name", "")
            result = scheme

            result = result.replace("{{first_name}}", to_casing([first_name], random.choice(CASING_TYPES)))
            result = result.replace("{{last_name}}", to_casing([last_name], random.choice(CASING_TYPES)))

            result = result.replace("{{name_ff}}", to_casing([first_name, last_name], random.choice(CASING_TYPES)))
            result = result.replace("{{name_ii}}", to_casing([first_name[0], last_name[0]], random.choice(["upper", "lower", "camel", "pascal"])))
            result = result.replace("{{name_fi}}", to_casing([first_name, last_name[0]], random.choice(CASING_TYPES)))
            result = result.replace("{{name_if}}", to_casing([first_name[0], last_name], random.choice(CASING_TYPES)))

            if "{{num}}" in result or "{{num?}}" in result:
                min = int(value_or_default(args, "min", 0))
                max = int(value_or_default(args, "max", 9999))
                num = gen_number(min, max, precision=0, log=False)
                
                result = result.replace("{{num}}", str(num).zfill(len(str(max))))
                if random.choice([True, False]):    
                    result = result.replace("{{num?}}", str(num).zfill(len(str(max))))
                else:
                    result = result.replace("{{num?}}", "")

                

            if log: print(f"Generated username: '{result}'")
            return result
        
    # Should be unreachable
    return ""