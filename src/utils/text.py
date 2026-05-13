from typing import Literal
import re

CasingType = Literal["lower", "upper", "camel", "pascal", "snake", "upper-snake", "kebab", "upper-kebab"]
CASING_TYPES: list[CasingType] = ["lower", "upper", "camel", "pascal", "snake", "upper-snake", "kebab", "upper-kebab"]

def to_alpha(s: str) -> str:
    return re.sub(r"[^a-zA-Z]", "", s)

def get_casing(s: str) -> CasingType:
    s = re.sub(r"\s+", "", s)  # Remove all whitespace

    is_alpha = s.isalpha()
    is_lower = s.islower()
    is_upper = s.isupper()

    def pascal_vs_camel(alpha_s: str) -> CasingType:
        is_first_upper = alpha_s[0].isupper()
        if is_first_upper:
            return "pascal"
        else:
            return "camel"

    if is_alpha:
        if is_lower:
            return "lower"
        elif is_upper:
            return "upper"
        
        return pascal_vs_camel(s)
    else:
        # Determine the casing type based on the presence of delimiters and the case of the letters
        alpha_s = to_alpha(s)

        if "-" in s:
            if alpha_s.isupper():
                return "upper-kebab"
            else:
                return "kebab"
        elif "_" in s:
            if alpha_s.isupper():
                return "upper-snake"
            else:
                return "snake"
        
        return pascal_vs_camel(alpha_s)

def to_casing(s: str | list[str], target_casing: CasingType) -> str:
    words: list[str] = []
    if isinstance(s, str):
        existing_casing = get_casing(s)

        match existing_casing:
            case "lower" | "upper":
                # Treat the entire string as a single word
                words = [s]
            case "camel" | "pascal":
                # Split on uppercase letters
                for c in s:
                    is_upper = c.isupper()

                    if is_upper or len(words) == 0:
                        words.append(c)
                    else:
                        words[-1] += c
            case "snake" | "upper-snake":
                words = s.split("_")
            case "kebab" | "upper-kebab":
                words = s.split("-")
    else:
        words = s
        
    match target_casing:
        case "lower":
            return "".join(word.lower() for word in words)
        case "upper":
            return "".join(word.upper() for word in words)
        case "camel":
            return words[0].lower() + "".join(word.capitalize() for word in words[1:])
        case "pascal":
            return "".join(word.capitalize() for word in words)
        case "snake":
            return "_".join(word.lower() for word in words)
        case "upper-snake":
            return "_".join(word.upper() for word in words)
        case "kebab":
            return "-".join(word.lower() for word in words)
        case "upper-kebab":
            return "-".join(word.upper() for word in words)
        
    return s
