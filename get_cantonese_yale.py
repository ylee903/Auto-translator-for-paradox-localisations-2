#!/usr/bin/env python3
import pycantonese as pc


def get_cantonese_yale(
    chinese_text: str | None = None,
    *,
    debug: bool = True,
    compound_per_word: bool = False,
) -> str:
    """
    Convert Chinese text (Cantonese) into Yale romanization with tone marks.

    Modes:
      - compound_per_word = False (default):
          "gwóng dūng yàhn góng gwóng dūng wá"
      - compound_per_word = True:
          "gwóngdūngyàhn góng gwóngdūngwá"

    - If chinese_text is None, prompt the user for input (interactive use).
    - If chinese_text is given, use it directly (for calling from other code).
    - Prints debug info (Jyutping and Yale) if debug=True.
    - Returns the final Yale string.
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
    # e.g. [('廣東人', 'gwong2dung1jan4'), ('講', 'gong2'), ('廣東話', 'gwong2dung1waa2')]

    if debug:
        print("\n=== Jyutping pairs (word -> jyutping) ===")
        for word, jp in pairs:
            print(f"{word!r} -> {jp}")

    # We'll keep:
    # - a flat list of all syllables (for the fully spaced form)
    # - per-word syllables (for the compounded form)
    all_yale_syllables: list[str] = []
    per_word_yale_syllables: list[tuple[str, list[str]]] = []

    if debug:
        print("\n=== Yale (per word, syllable list) ===")

    for word, jp in pairs:
        if jp is None:
            # punctuation / unknown; for now we just skip
            if debug:
                print(f"{word!r} -> (no Jyutping / no Yale)")
            continue

        # Let PyCantonese handle syllable splitting for us
        yale_syllables = pc.jyutping_to_yale(jp, as_list=True)
        # e.g. ['gwóng', 'dūng', 'yàhn']

        if debug:
            print(f"{word!r} ({jp}) -> {yale_syllables}")

        all_yale_syllables.extend(yale_syllables)
        per_word_yale_syllables.append((word, yale_syllables))

    # 2) Build final string depending on mode
    if compound_per_word:
        # Glue syllables inside each word, spaces only between words
        # e.g. ["gwóngdūngyàhn", "góng", "gwóngdūngwá"]
        word_chunks = ["".join(syls) for (_w, syls) in per_word_yale_syllables]
        yale_result = " ".join(word_chunks)
    else:
        # Fully spaced syllables
        yale_result = " ".join(all_yale_syllables)

    if debug:
        print("\n=== Yale (final result) ===")
        print(yale_result)

    return yale_result


if __name__ == "__main__":
    # Interactive test
    result = get_cantonese_yale(debug=True, compound_per_word=True)
    if result:
        print("\n[RETURNED YALE STRING]")
        print(result)
