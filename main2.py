#!/usr/bin/env python3
"""
Simple interactive tester using ChatGPT-5-nano.
- Reads system prompt from prompt.txt
- Asks user for a query
- Sends both to OpenAI API
- Prints verbose output for debugging
"""

import os
from openai import OpenAI
from api_key_loader import debug_load_dotenv, debug_get_api_key, debug_openai_client


def read_prompt_file(file_path: str) -> str:
    """Read prompt text from file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"⚠️ prompt file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        prompt = f.read().strip()
    print(f"[DEBUG] Loaded prompt from {file_path} ({len(prompt)} chars)")
    return prompt


def main():
    print("=" * 60)
    print("🤖 ChatGPT-5 Nano Tester (Prompt from prompt.txt)")
    print("=" * 60)

    # Step 1: Load API key
    env_path = "./keys.env"
    debug_load_dotenv(env_path)
    api_key = debug_get_api_key()

    # Step 2: Initialize OpenAI client
    client = debug_openai_client(api_key)

    # Step 3: Load system prompt
    prompt_file = "./prompt.txt"
    system_prompt = read_prompt_file(prompt_file)

    # Step 4: Collect user query
    print("\n--- Input Section ---")
    query = input("Enter your query: ").strip()

    # Step 5: Prepare API request
    model_name = "gpt-5-nano"
    print("\n--- Sending request ---")
    print(f"Model: {model_name}")
    print(f"Prompt (from {prompt_file}):\n{system_prompt}")
    print(f"Query: {query}")

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
        )

        # Step 6: Print response
        print("\n--- Response ---")
        print(response.choices[0].message.content.strip())

    except Exception as e:
        print(f"\n❌ Error: {e}")

    print("\n--- Debug Info ---")
    print("Session ended (OK if no errors).")


if __name__ == "__main__":
    main()
