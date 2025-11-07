#!/usr/bin/env python3
"""
Utility to remove diacritics (accents) from text.

Example:
    "gwóngdūngyàhn" -> "gwongdungyahn"
"""

import unicodedata


def remove_diacritics(text: str) -> str:
    """
    Remove diacritics from the input string by Unicode normalization.

    - Normalizes to NFD (decomposed form)
    - Drops all combining marks (category 'Mn')
    - Re-composes to NFC for a clean result (optional)
    """
    # Decompose characters into base + combining marks
    decomposed = unicodedata.normalize("NFD", text)

    # Filter out all combining marks
    stripped = "".join(
        ch for ch in decomposed
        if unicodedata.category(ch) != "Mn"
    )

    # You can either return NFD-stripped directly, or re-compose to NFC.
    # Re-compose for safety.
    return unicodedata.normalize("NFC", stripped)


if __name__ == "__main__":
    # Simple manual test
    sample = "gwóngdūngyàhn nīdouh m̀hchó"
    print("Original:", sample)
    print("Stripped:", remove_diacritics(sample))
