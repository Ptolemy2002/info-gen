from typo.main import *
from typo.vars import letters, digits, all_characters, filler_words
from utils.math import rand_pick_dstrb

# Set of available typo generators
TYPO_GENERATORS: dict[str, TypoGenerator] = {
    "let-ins": TypoInsertionGenerator(letters),
    "let-sub": TypoSubstitutionGenerator(letters),

    "digit-ins": TypoInsertionGenerator(digits),
    "digit-sub": TypoSubstitutionGenerator(digits),

    "char-ins": TypoInsertionGenerator(all_characters),
    "char-sub": TypoSubstitutionGenerator(all_characters),

    "kb-ins": TypoKeyboardProximityInsertionGenerator(False),
    "kb-sub": TypoKeyboardProximitySubstitutionGenerator(False),

    "kb-ins-as": TypoKeyboardProximityInsertionGenerator(True),
    "kb-sub-as": TypoKeyboardProximitySubstitutionGenerator(True),

    "trans": TypoTranspositionGenerator(),
    "del": TypoDeletionGenerator(),
    "case": TypoCaseChangeGenerator(),
    "word-dup": TypoWordRepetitionGenerator(),

    "dbl-miss": TypoMissedDoubleGenerator(),
    "dbl-ins": TypoExtraDoubleGenerator(),

    "filler-ins": TypoFillerWordInsertionGenerator(filler_words),

    "homophone": TypoHomophoneGenerator()
}

class TypoArgs(TypedDict):
    text: str
    typos: list[str]
    typo_weights: list[int]
    typo_rate: float
    typos_per_word: int

def gen_typos(text: str, typo_distrb: list[tuple[int, str]], rate: float=0.1, typos_per_word: int=1, log: bool = False) -> str:
    words = process_words(text)
    if log: print(f"Got {len(words)} words from input text for typo generation.")
    result = words.copy()
    offset = 0  # Track how much result list has grown/shrunk
    
    for i in range(len(words)):
        # if we're at the end, refuse to do filler word typos unless it's the only option.
        def cannot_do_filler_ins() -> bool:
            return i + offset == len(result) - 1
        
        # if we're generating homophones and the word has no homophones, refuse to do that typo unless it's the only option.
        def cannot_do_homophone() -> bool:
            homophone_gen = TYPO_GENERATORS["homophone"]
            return isinstance(homophone_gen, TypoHomophoneGenerator) and not homophone_gen.has_any_homophones(result[i + offset])

        if random.random() < rate:
            num_typos = random.randint(1, typos_per_word)
            if log: print(f"Generating {num_typos} typos to word '{words[i]}' at original index {i}.")

            for _ in range(num_typos):
                typo_type = rand_pick_dstrb(typo_distrb)
                if log: print(f"Picked typo type '{typo_type}' for word '{result[i + offset]}' at current index {i + offset}.")

                attempts = 0
                while (
                    (typo_type == "filler-ins" and cannot_do_filler_ins())
                    or (typo_type == "homophone" and cannot_do_homophone())
                ) and len(typo_distrb) > 1 and attempts < 10:
                    typo_type = rand_pick_dstrb(typo_distrb)
                    attempts += 1
                    if log:
                        if typo_type == "filler-ins":
                            print(f"Refused to apply 'filler-ins' typo to last word. Picked new typo type '{typo_type}' instead.")
                        elif typo_type == "homophone":
                            print(f"Refused to apply 'homophone' typo to word '{result[i + offset]}' with no homophones. Picked new typo type '{typo_type}' instead.")

                if (typo_type == "filler-ins" and cannot_do_filler_ins()) or (typo_type == "homophone" and cannot_do_homophone()):
                    if log: print(f"Could not find a suitable typo type for word '{result[i + offset]}' after 10 attempts. Skipping typo generation for this word.")
                    continue

                typo_generator = TYPO_GENERATORS[typo_type]
                new_words = typo_generator.generate([result[i + offset]])
                if log: print(f"Generated new word(s) {new_words} from original word '{result[i + offset]}' using typo type '{typo_type}'.")
                
                # Calculate new offset based on word count change
                word_count_diff = len(new_words) - 1
                result = result[:i + offset] + new_words + result[i + offset + 1:]
                offset += word_count_diff
    
    return ' '.join(result)