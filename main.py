#!/usr/bin/env python3
"""
Batch YML key-value replacer for Paradox localisation-style files.

This version:
- Reads .yml/.yaml files from an input folder (default: ./read1)
- Writes transformed files to an output folder (default: ./write1)
- For each line like:

      c_ruzhou: "汝州"

  it extracts the value ("汝州"), calls an OpenAI model (gpt-5-nano)
  with a separate prompt file (prompt.txt), and replaces the value with
  the model's output, e.g.:

      c_ruzhou: "some snarky nonsense"

- Uses:
    - keys.env  (contains OPENAI_API_KEY=...)
    - api_key_loader.py (debug_load_dotenv, debug_get_api_key, debug_openai_client)
    - prompt.txt in the same directory as this script
"""

from pathlib import Path
import sys
import os

from openai import OpenAI  # imported just like in the working tester
from api_key_loader import (
    debug_load_dotenv,
    debug_get_api_key,
    debug_openai_client,
)

# ---- CONFIG ----

# .env / key file
ENV_FILE = Path("keys.env")

# Prompt file in root. Contents might be something like:
# "Please ignore the provided text and replace with nonsense or make some snarky commentary."
PROMPT_FILE = Path("prompt.txt")

# Default folders for batch processing
DEFAULT_INPUT_DIR = Path("read1")
DEFAULT_OUTPUT_DIR = Path("write1")

# Model to call – small & cheap GPT-5 variant
MODEL_NAME = "gpt-4.1-nano"


# ---- PROMPT LOADING (copied style from working tester) ----

def read_prompt_file(file_path: Path) -> str:
    """Read prompt text from file."""
    if not file_path.is_file():
        raise FileNotFoundError(f"⚠️ prompt file not found: {file_path}")
    prompt = file_path.read_text(encoding="utf-8").strip()
    print(f"[DEBUG] Loaded prompt from {file_path} ({len(prompt)} chars)")
    return prompt


# ---- OPENAI-BASED REPLACER ----

def make_replacer(client, model_name: str, system_prompt: str):
    """
    Returns a function replacewithrealname1(original_text: str) -> str
    that calls the Chat Completions API with:

      - system message: system_prompt (from prompt.txt)
      - user message:   original_text (the original value inside the quotes)

    and returns the model's text output.
    """

    def replacewithrealname1(original_text: str) -> str:
        print(f"[DEBUG] Calling model for value: {original_text!r}")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": original_text},
                ],
            )

            # DEBUG – you can comment these out if too noisy
            print("[DEBUG] Raw API response object:", response)
            content = response.choices[0].message.content or ""
            new_text = content.strip()
            print(f"[DEBUG] Model returned: {new_text!r}")

            if not new_text:
                print(
                    "[WARN] Model returned empty text, keeping original value "
                    f"for {original_text!r}"
                )
                return original_text

            return new_text

        except Exception as e:
            # Fail safe: keep the original localisation if the API call fails
            print(
                f"[ERROR] OpenAI call failed for value {original_text!r}: {e}\n"
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
        input:  d_sanggan: "桑干"
        output: d_sanggan: "some snark"

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

    # Build the new value using the replacer (OpenAI call)
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
        python yml_openai_replace.py [input_folder] [output_folder]

    Defaults:
        input_folder  = ./read1
        output_folder = ./write1
    """
    if argv is None:
        argv = sys.argv[1:]

    input_folder = Path(argv[0]) if len(argv) >= 1 else DEFAULT_INPUT_DIR
    output_folder = Path(argv[1]) if len(argv) >= 2 else DEFAULT_OUTPUT_DIR

    print("=" * 60)
    print("🗂  YML OpenAI Key-Value Replacer (gpt-5-nano)")
    print("=" * 60)
    print(f"Input folder:  {input_folder}")
    print(f"Output folder: {output_folder}")

    # Step 1: Load env + API key
    env_path = str(ENV_FILE)
    print(f"[DEBUG] Loading env from {env_path}")
    debug_load_dotenv(env_path)
    api_key = debug_get_api_key()

    # Step 2: Initialize OpenAI client (same as working tester)
    client = debug_openai_client(api_key)

    # Step 3: Load system prompt from file
    system_prompt = read_prompt_file(PROMPT_FILE)

    print("\n--- OpenAI Setup ---")
    print(f"Model: {MODEL_NAME}")
    print(f"System prompt (from {PROMPT_FILE}):")
    print(system_prompt)
    print("--- End prompt ---\n")

    # Factory that creates the replacer (we could extend this per-file later)
    def replacer_factory():
        return make_replacer(client, MODEL_NAME, system_prompt)

    # Step 4: Process folder
    process_folder(input_folder, output_folder, replacer_factory)


if __name__ == "__main__":
    main()
