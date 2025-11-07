#!/usr/bin/env python3
import pycantonese as pc


def get_cantonese_yale(chinese_text: str | None = None, *, debug: bool = True) -> str:
    """
    Convert Chinese text (Cantonese) into Yale romanization with tone marks,
    with spaces between syllables.

    - If chinese_text is None, prompt the user for input (interactive use).
    - If chinese_text is given, use it directly (for calling from other code).
    - Prints debug info (Jyutping and Yale) if debug=True.
    - Returns the final Yale string (syllables space-separated).
    """
    # Interactive mode if no text is provided
    if chinese_text is None:
        chinese_text = input("Enter Chinese text to convert to Cantonese Yale: ").strip()
        if not chinese_text:
            if debug:
                print("No text entered. Aborting.")
            return ""

    # 1) Chinese → Jyutping word-level pairs
    pairs = pc.characters_to_jyutping(chinese_text)
    # e.g. [('廣東人', 'gwong2dung1jan4')]

    if debug:
        print("\n=== Jyutping pairs (word -> jyutping) ===")
        for word, jp in pairs:
            print(f"{word!r} -> {jp}")

    # 2) For each word's Jyutping, let PyCantonese split into syllables itself
    all_yale_syllables: list[str] = []

    if debug:
        print("\n=== Yale (per word, syllable list) ===")

    for word, jp in pairs:
        if jp is None:
            # punctuation / unknown
            if debug:
                print(f"{word!r} -> (no Jyutping / no Yale)")
            continue

        # This already returns syllable-level Yale: ['gwóng', 'dūng', 'yàhn']
        yale_syllables = pc.jyutping_to_yale(jp, as_list=True)

        if debug:
            print(f"{word!r} ({jp}) -> {yale_syllables}")

        all_yale_syllables.extend(yale_syllables)

    # 3) Join all syllables with spaces
    yale_result = " ".join(all_yale_syllables)

    if debug:
        print("\n=== Yale (final result) ===")
        print(yale_result)

    # 4) Return final Yale string (this is the “for real” output)
    return yale_result


if __name__ == "__main__":
    result = get_cantonese_yale(debug=True)
    if result:
        print("\n[RETURNED YALE STRING]")
        print(result)
