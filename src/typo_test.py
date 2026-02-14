from typo import *

if __name__ == "__main__":
    def run_test(phrase: str, generator: TypoGenerator, count: int=1):
        print(f"Original phrase: {phrase}")
        
        for _ in range(count):
            chosen_index = random.randint(0, len(phrase.split()) - 1)

            chosen_word = phrase.split()[chosen_index]
            generated_words = generator.generate([chosen_word])

            phrase = ' '.join(phrase.split()[:chosen_index] + generated_words + phrase.split()[chosen_index + 1:])

        print(f"Phrase with generated typo(s) ({count}): {phrase}\n")

    print("--- Insertion Test ---")
    run_test("example", TypoInsertionGenerator(), 1)

    print("--- Keyboard Proximity Insertion Test ---")
    run_test("example", TypoKeyboardProximityInsertionGenerator(), 1)

    print("--- Substitution Test ---")
    run_test("example", TypoSubstitutionGenerator(), 1)

    print("--- Keyboard Proximity Substitution Test ---")
    run_test("example", TypoKeyboardProximitySubstitutionGenerator(), 1)

    print("--- Transposition Test ---")
    run_test("example", TypoTranspositionGenerator(), 1)

    print("--- Deletion Test ---")
    run_test("example", TypoDeletionGenerator(), 2)

    print("--- Case Change Test ---")
    run_test("Example", TypoCaseChangeGenerator(), 3)

    print("--- Word Repetition Test ---")
    run_test("This is an example", TypoWordRepetitionGenerator(), 2)

    print("--- Missed Double Test ---")
    run_test("bookkeeper", TypoMissedDoubleGenerator(), 1)

    print("--- Extra Double Test ---")
    run_test("example", TypoExtraDoubleGenerator(), 1)

    print("--- Homophone Test ---")
    run_test("The Right way to do things", TypoHomophoneGenerator(), 3)

    print("--- Filler Word Insertion Test ---")
    run_test("This is an example", TypoFillerWordInsertionGenerator(), 2)