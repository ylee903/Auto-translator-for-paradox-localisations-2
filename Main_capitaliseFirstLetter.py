#!/usr/bin/env python3
"""
Batch YML key-value replacer for Paradox localisation-style files.

This version:
- Reads .yml/.yaml files from an input folder
  (default: ./capitaliseFirstLetter_input)
- Writes transformed files to an output folder
  (default: ./capitaliseFirstLetter_output)
- For each line like:

      c_guangdong: "gwongdungyahn"

  it extracts the value ("gwongdungyahn"), calls capitalise_first_letter()
  to capitalise the first letter, and replaces the value, e.g.:

      c_guangdong: "Gwongdungyahn"

- Uses:
    - capitaliseFirstLetter.py in the same directory
      (function: capitalise_first_letter)
"""

from pathlib import Path
import sys

from capitaliseFirstLetter import capitalise_first_letter


# ---- CONFIG ----

# Default folders for batch processing
DEFAULT_INPUT_DIR = Path("capitaliseFirstLetter_input")
DEFAULT_OUTPUT_DIR = Path("capitaliseFirstLetter_output")


# ---- REPLACER ----

def make_replacer():
    """
    Returns a function replacewithrealname1(original_text: str) -> str
    that calls capitalise_first_letter() on the original value.
    """

    def replacewithrealname1(original_text: str) -> str:
        if not original_text:
            return original_text

        try:
            capitalised = capitalise_first_letter(original_text)
            return capitalised
        except Exception as e:
            print(
                f"[ERROR] capitalise_first_letter() failed for value {original_text!r}: {e}\n"
                "        Keeping original value."
            )
            return original_text

    return replacewithrealname1


# ---- YAML LINE PROCESSING ----

def process_line(line: str, replacer) -> str:
    """
    Process a single line of a Paradox-style YAML localisation file.

    - Skips empty lines and full-line comments starting with '#'
    - Looks for the first ':' in the line (key-value separator)
    - Finds the first '"' after the colon and the last '"' on the line
    - Extracts the original value inside the quotes
    - Calls replacer(original_value) to get new_value
    - Rebuilds the line with the same key/comment structure, but with
      the value replaced.

    Example:
        input:  c_guangdong: "gwongdungyahn"
        output: c_guangdong: "Gwongdungyahn"

    Lines like:
        #  h_dar_al_islam: "Dar al-Islam"
    are left untouched, because they start with '#'.
    """
    stripped = line.lstrip()

    # Skip empty lines and comment-only lines
    if not stripped or stripped.startswith("#"):
        return line

    # We only care about lines that have a ':' (a key-value pair)
    colon_index = line.find(":")
    if colon_index == -1:
        return line

    # Find the first double quote AFTER the colon (start of the value)
    first_quote = line.find('"', colon_index)
    if first_quote == -1:
        # No quoted value on this line
        return line

    # Find the last double quote on the line (end of the value)
    last_quote = line.rfind('"')
    if last_quote == first_quote:
        # Only one quote found; not a proper "value"
        return line

    # Extract the original value inside the quotes
    original_value = line[first_quote + 1 : last_quote]

    # Build the new value using the replacer (capitalisation)
    new_value = replacer(original_value)

    # Rebuild the line, preserving everything outside the quotes
    before = line[: first_quote + 1]  # includes the opening quote
    after = line[last_quote:]         # includes the closing quote + trailing stuff
    new_line = before + new_value + after
    return new_line


# ---- FILE & FOLDER PROCESSING ----

def process_file_streaming(input_path: Path, output_path: Path, replacer):
    """
    Read a .yml file line-by-line, replace values via replacer(), and write
    immediately to the output file.

    This keeps processing "live": each processed line is flushed as we go.
    """
    print(f"Processing file: {input_path} -> {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8") as f_in, output_path.open(
        "w", encoding="utf-8", newline=""
    ) as f_out:

        for line_number, line in enumerate(f_in, start=1):
            new_line = process_line(line, replacer)
            f_out.write(new_line)
            # Optional live feedback:
            if new_line != line:
                print(f"  line {line_number}: updated")


def process_folder(input_dir: Path, output_dir: Path, replacer_factory):
    """
    Process all .yml / .yaml files in input_dir (non-recursive),
    writing transformed versions to output_dir with the same filenames.

    replacer_factory is a function that returns a per-file replacer, in case
    you ever want different behaviour per file. Right now we just reuse
    the same replacer across files.
    """
    if not input_dir.is_dir():
        print(f"Error: input folder {input_dir} does not exist or is not a directory.")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        f
        for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in {".yml", ".yaml"}
    )

    if not files:
        print(f"No .yml or .yaml files found in {input_dir}")
        return

    print(f"Found {len(files)} file(s) in {input_dir}")

    # We currently use the same replacer for all files.
    replacer = replacer_factory()

    for i, input_file in enumerate(files, start=1):
        output_file = output_dir / input_file.name
        print(f"[{i}/{len(files)}] {input_file.name}")
        process_file_streaming(input_file, output_file, replacer)

    print("All files processed.")


# ---- MAIN ENTRYPOINT ----

def main(argv=None):
    """
    Usage:
        python Main_capitaliseFirstLetter.py [input_folder] [output_folder]

    Defaults:
        input_folder  = ./capitaliseFirstLetter_input
        output_folder = ./capitaliseFirstLetter_output
    """
    if argv is None:
        argv = sys.argv[1:]

    input_folder = Path(argv[0]) if len(argv) >= 1 else DEFAULT_INPUT_DIR
    output_folder = Path(argv[1]) if len(argv) >= 2 else DEFAULT_OUTPUT_DIR

    print("=" * 60)
    print("🗂  YML Capitalise-First-Letter Replacer")
    print("=" * 60)
    print(f"Input folder:  {input_folder}")
    print(f"Output folder: {output_folder}")

    def replacer_factory():
        return make_replacer()

    process_folder(input_folder, output_folder, replacer_factory)


if __name__ == "__main__":
    main()
