import random
import re
import nltk
from .vars import *

MEANINGFUL_WORD_CHAR_REGEX = re.compile(r'[a-zA-Z\-\']')

def make_word_meaningful(word: str) -> str | None:
    # Remove non-meaningful characters
    meaningful_word = ''.join(c for c in word if MEANINGFUL_WORD_CHAR_REGEX.match(c))

    # If we have nothing left, return None
    if not len(meaningful_word):
        return None

    return meaningful_word

def process_words(s: str) -> list[str]:
    return re.split(r'\s+', s)

def get_homophones(word: str) -> list[str] | None:
    # Ensure you have the dictionary downloaded
    try:
        entries = nltk.corpus.cmudict.entries()
    except LookupError:
        nltk.download('cmudict')
        entries = nltk.corpus.cmudict.entries()
    
    # 1. Find the pronunciation(s) of the input word
    # The dictionary format is a list of tuples: ('word', ['PHONE', 'LIST'])
    pronunciations = [pron for w, pron in entries if w == word.lower()]
    
    if not pronunciations:
        return None
    
    # 2. Find all other words that share those pronunciations
    homophones = []
    for target_pron in pronunciations:
        for w, pron in entries:
            # Check if pronunciation matches AND it's not the same word
            if pron == target_pron and w != word.lower():
                homophones.append(w)
                
    return list(set(homophones)) # Remove duplicates

class TypoGenerator:
    words_accepted: int = 1

    def __init__(self, words_accepted: int = 1):
        self.words_accepted = words_accepted

    def __generate__(self, words: list[str]) -> list[str]:
        raise NotImplementedError("Subclasses must implement the __generate__ method")
    
    def generate(self, words: list[str]) -> list[str]:
        if len(words) != self.words_accepted:
            raise ValueError(f"Generator expects {self.words_accepted} words, but got {len(words)}")
        
        return self.__generate__(words)

class TypoInsertionGenerator(TypoGenerator):
    letter_set: str

    def __init__(
        self,
        letter_set: str = letters
    ):
        super().__init__(1)
        self.letter_set = letter_set

    def __generate__(self, words: list[str]) -> list[str]:
        word = words[0]

        # Insert exactly one letter at a random position
        insert_position = random.randint(0, len(word))
        insert_letter = random.choice(self.letter_set)
        word = word[:insert_position] + insert_letter + word[insert_position:]

        return [word]

class TypoKeyboardProximityInsertionGenerator(TypoGenerator):
    accidental_shift: bool = True

    def __init__(
        self,
        accidental_shift: bool = True
    ):
        super().__init__(1)
        self.accidental_shift = accidental_shift

    def __generate__(self, words: list[str]) -> list[str]:
        word = words[0]

        # Insert exactly one letter based on keyboard proximity at a random position
        insert_position = random.randint(0, len(word))
        
        # Determine the possible letters to insert based on the neighboring characters
        neighboring_chars = set()
        if insert_position > 0:
            neighboring_chars.add(word[insert_position - 1])
        if insert_position < len(word):
            neighboring_chars.add(word[insert_position])

        possible_insertions = set()
        for char in neighboring_chars:
            if char in keyboard_proximity_map:
                proximity_info = keyboard_proximity_map[char]
                possible_insertions.update(proximity_info['bordering'])
                if self.accidental_shift:
                    possible_insertions.update(proximity_info['accidental_shift_bordering'])
                    possible_insertions.add(proximity_info['accidental_shift'])

        if not possible_insertions:
            return [word]

        insert_letter = random.choice(list(possible_insertions))

        before_or_after = random.choice(['before', 'after'])
        if before_or_after == 'before':
            word = word[:insert_position] + insert_letter + word[insert_position:]
        else:
            word = word[:insert_position] + insert_letter + word[insert_position:]

        return [word]

class TypoSubstitutionGenerator(TypoGenerator):
    letter_set: str

    def __init__(
            self,
            letter_set: str = letters
        ):
        super().__init__(1)
        self.letter_set = letter_set

    def __generate__(self, words: list[str]) -> list[str]:
        word = words[0]

        if len(word) == 0:
            return [word]

        # Substitute exactly one letter at a random position
        substitute_position = random.randint(0, len(word) - 1)
        substitute_letter = random.choice(self.letter_set)
        word = word[:substitute_position] + substitute_letter + word[substitute_position + 1:]

        return [word]

class TypoKeyboardProximitySubstitutionGenerator(TypoGenerator):
    accidental_shift: bool = True

    def __init__(
            self,
            accidental_shift: bool = True
        ):
        super().__init__(1)
        self.accidental_shift = accidental_shift

    def __generate__(self, words: list[str]) -> list[str]:
        word = words[0]

        if len(word) == 0:
            return [word]

        # Make exactly one substitution based on keyboard proximity
        # Keep trying until we find a valid position
        max_attempts = len(word)
        remaining_word = word
        for _ in range(max_attempts):
            substitute_position = random.randint(0, len(remaining_word) - 1)
            original_letter = remaining_word[substitute_position]

            if original_letter not in keyboard_proximity_map:
                remaining_word = remaining_word[:substitute_position] + remaining_word[substitute_position + 1:]
                if len(remaining_word) == 0:
                    return [word]
                continue

            proximity_info = keyboard_proximity_map[original_letter]
            possible_substitutes = proximity_info['bordering'][:]
            if self.accidental_shift:
                possible_substitutes += proximity_info['accidental_shift_bordering']
                possible_substitutes.append(proximity_info['accidental_shift'])

            if not possible_substitutes:
                remaining_word = remaining_word[:substitute_position] + remaining_word[substitute_position + 1:]
                if len(remaining_word) == 0:
                    return [word]
                continue

            substitute_letter = random.choice(possible_substitutes)

            # Substitute the letter at the chosen position
            word = word[:substitute_position] + substitute_letter + word[substitute_position + 1:]

            remaining_word = remaining_word[:substitute_position] + remaining_word[substitute_position + 1:]
            break

        return [word]
    
class TypoTranspositionGenerator(TypoGenerator):
    def __init__(self):
        super().__init__(1)

    def __generate__(self, words: list[str]) -> list[str]:
        word = words[0]

        if len(word) < 2:
            return [word]
        
        # Transpose two adjacent letters at a random position
        transpose_position = random.randint(0, len(word) - 2)
        word = (word[:transpose_position] + word[transpose_position + 1] + word[transpose_position] + word[transpose_position + 2:])
        return [word]
    
class TypoDeletionGenerator(TypoGenerator):
    def __init__(self):
        super().__init__(1)

    def __generate__(self, words: list[str]) -> list[str]:
        word = words[0]

        if len(word) == 0:
            return [word]

        # Delete exactly one letter at a random position
        delete_position = random.randint(0, len(word) - 1)
        word = word[:delete_position] + word[delete_position + 1:]

        return [word]
    
class TypoCaseChangeGenerator(TypoGenerator):
    def __init__(self):
        super().__init__(1)

    def __generate__(self, words: list[str]) -> list[str]:
        word = words[0]

        if len(word) == 0:
            return [word]

        # Change the case of exactly one letter at a random position
        change_position = random.randint(0, len(word) - 1)
        original_letter = word[change_position]
        if original_letter.islower():
            substitute_letter = original_letter.upper()
        elif original_letter.isupper():
            substitute_letter = original_letter.lower()
        else:
            substitute_letter = original_letter

        word = word[:change_position] + substitute_letter + word[change_position + 1:]

        return [word]
    
class TypoWordRepetitionGenerator(TypoGenerator):
    def __init__(self):
        super().__init__(1)

    def __generate__(self, words: list[str]) -> list[str]:
        word = words[0]

        if len(word) == 0:
            return [word]

        # Repeat the entire word
        return [word, word]
    
class TypoMissedDoubleGenerator(TypoGenerator):
    def __init__(self):
        super().__init__(1)

    def __generate__(self, words: list[str]) -> list[str]:
        word = words[0]

        if len(word) < 2:
            return [word]

        # If there are any double letters, randomly choose one pair to miss
        double_letter_positions = [i for i in range(len(word) - 1) if word[i] == word[i + 1]]

        if not double_letter_positions:
            return [word]

        missed_position = random.choice(double_letter_positions)
        word = word[:missed_position] + word[missed_position + 1:]

        return [word]
    
class TypoExtraDoubleGenerator(TypoGenerator):
    def __init__(self):
        super().__init__(1)

    def __generate__(self, words: list[str]) -> list[str]:
        word = words[0]

        if len(word) == 0:
            return [word]

        # Randomly choose a letter to double
        double_position = random.randint(0, len(word) - 1)
        word = word[:double_position] + word[double_position] + word[double_position:]

        return [word]
    
class TypoHomophoneGenerator(TypoGenerator):
    homophone_map: dict[str, list[str]] = {}

    def __init__(self):
        super().__init__(1)

    def has_any_homophones(self, word: str) -> bool:
        meaningful_word = make_word_meaningful(word)
        if meaningful_word is None:
            return False
        
        homophones = self.homophone_map.get(meaningful_word)
        if homophones is None:
            homophones = get_homophones(meaningful_word)
            if homophones is None:
                homophones = []
            self.homophone_map[meaningful_word] = homophones

        return len(homophones) > 0
    
    def get_homophones(self, word: str) -> list[str]:
        meaningful_word = make_word_meaningful(word)
        if meaningful_word is None:
            return []
        
        # Calling this will fetch and cache the homophones if they haven't been fetched already
        if self.has_any_homophones(meaningful_word):
            return self.homophone_map[meaningful_word]

        return self.homophone_map[meaningful_word]

    def __generate__(self, words: list[str]) -> list[str]:
        word = words[0]

        if len(word) == 0:
            return [word]

        meaningful_word = make_word_meaningful(word)
        if meaningful_word is None:
            return [word]
        
        if not self.has_any_homophones(meaningful_word):
            return [word]

        substitute_word = random.choice(self.get_homophones(meaningful_word))

        return [substitute_word]
    
class TypoFillerWordInsertionGenerator(TypoGenerator):
    filler_words: list[str]

    def __init__(self, filler_words: list[str] = filler_words):
        super().__init__(1)
        self.filler_words = filler_words

    def __generate__(self, words: list[str]) -> list[str]:
        word = words[0]

        if len(word) == 0:
            return [word]

        # Insert a random filler word before or after the original word
        filler_word = random.choice(self.filler_words)
        before_or_after = random.choice(['before', 'after'])
        if before_or_after == 'before':
            return [filler_word, word]
        else:
            return [word, filler_word]