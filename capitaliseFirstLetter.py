#!/usr/bin/env python3
"""
Utility to capitalise the first letter of a string.

Examples:
    "gwongdungyahn" -> "Gwongdungyahn"
    "gwóngdūngyàhn góng gwóngdūngwá" -> "Gwóngdūngyàhn góng gwóngdūngwá"
"""

def capitalise_first_letter(text: str) -> str:
    """
    Capitalise the first character of the string (Unicode-safe), leaving
    the rest of the string unchanged.

    If the string is empty or length 1, returns it appropriately.
    """
    if not text:
        return text

    # Uppercase the first character, keep the rest as-is
    return text[0].upper() + text[1:]


if __name__ == "__main__":
    # Simple manual tests
    samples = [
        "gwongdungyahn",
        "gwóngdūngyàhn góng gwóngdūngwá",
        "",
        " already capitalised?",
    ]
    for s in samples:
        print(f"Original: {s!r} -> Capitalised: {capitalise_first_letter(s)!r}")
