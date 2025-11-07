#!/usr/bin/env python3
"""
Main simulation script to test automatic calls to get_cantonese_yale()
without user input. It imports the function, calls it on several sentences,
and prints the results.
"""

from get_cantonese_yale import get_cantonese_yale


def main():
    # Test sentences to verify automatic conversion
    test_sentences = [
        "廣東人講廣東話",
        "我哋一齊食飯",
        "佢哋去飲茶",
        "今日好熱",
        "呢度唔錯",
        "世界真細",
    ]

    print("=== Automatic Cantonese Yale Transliteration Test ===\n")

    for i, sentence in enumerate(test_sentences, start=1):
        print(f"[{i}] Chinese: {sentence}")

        # Call the transliteration function automatically (no user input)
        yale_output = get_cantonese_yale(
            sentence,
            debug=False,          # turn off verbose prints
            compound_per_word=True  # glue syllables inside each word
        )

        print(f"     Yale: {yale_output}\n")

    print("=== Test complete ===")


if __name__ == "__main__":
    main()
