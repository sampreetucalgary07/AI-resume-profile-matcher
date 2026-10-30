#!/usr/bin/env python3
"""
Ollama Client & Verification Script for AI Resume Profile Matcher.

This script:
1. Verifies if the 'ollama' Python package is installed; installs it automatically if missing.
2. Checks connectivity to the local Ollama server (default: http://localhost:11434).
3. Lists all locally pulled models on the Ollama server.
4. Sends a prompt to the Ollama server and prints the model's response.

Usage:
  python3 run_ollama.py
  python3 run_ollama.py --model llama3.2 --prompt "Tell me about software engineering resumes."
  python3 run_ollama.py --list-models
"""

import sys
import os
import argparse
import subprocess
import json
import urllib.request
import urllib.error

DEFAULT_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_PROMPT = (
    "What are the 3 most critical skills to highlight on an AI/Software Engineer "
    "resume? Answer concisely in 3 bullet points."
)


def ensure_ollama_installed():
    """Ensure the 'ollama' Python library is installed."""
    try:
        import ollama
        return ollama
    except ImportError:
        print("\n[*] 'ollama' Python library is not installed.")
        print("[*] Installing 'ollama' via pip...")
        try:
            cmd = [sys.executable, "-m", "pip", "install", "ollama"]
            subprocess.check_call(cmd)
            import ollama
            print("[✓] Successfully installed 'ollama' Python package!\n")
            return ollama
        except Exception as err:
            print(f"[!] Failed to install 'ollama' package automatically: {err}")
            print("    Please run manually: pip install ollama\n")
            return None


def check_ollama_server(host=DEFAULT_HOST):
    """
    Check if the Ollama server is running and reachable.
    Returns (is_running: bool, models_list: list).
    """
    clean_host = host.rstrip("/")
    url = f"{clean_host}/api/tags"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AI-Resume-Matcher"})
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", [])]
                return True, models
    except urllib.error.URLError:
        return False, []
    except Exception:
        return False, []

    return False, []


def query_ollama(prompt, model="llama3.2", host=DEFAULT_HOST, temperature=0.2):
    """
    Send a prompt to the Ollama server and return the text response.
    Tries the 'ollama' Python package first, with HTTP fallback.
    """
    clean_host = host.rstrip("/")
    clean_model = model.replace("ollama/", "").replace("ollama:", "")

    # Method 1: Using 'ollama' Python package
    try:
        import ollama
        client = ollama.Client(host=clean_host)
        res = client.generate(
            model=clean_model,
            prompt=prompt,
            options={"temperature": float(temperature)}
        )
        return res.get("response", "").strip()
    except Exception as e:
        # Fallback to direct HTTP API if package or client throws
        pass

    # Method 2: Direct HTTP request to Ollama /api/generate
    endpoint = f"{clean_host}/api/generate"
    payload = json.dumps({
        "model": clean_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": float(temperature)}
    }).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "AI-Resume-Matcher"}
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except urllib.error.HTTPError as http_err:
        raise RuntimeError(f"Ollama HTTP error ({http_err.code}): {http_err.read().decode('utf-8', errors='ignore')}")
    except Exception as err:
        raise RuntimeError(f"Could not reach Ollama at {clean_host}: {err}")


def main():
    parser = argparse.ArgumentParser(description="Ollama Client for AI Resume Profile Matcher")
    parser.add_argument("--prompt", "-p", type=str, default=DEFAULT_PROMPT, help="Prompt to send to Ollama")
    parser.add_argument("--model", "-m", type=str, default=None, help="Ollama model to use (default: first available or llama3.2)")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="Ollama server host (default: http://localhost:11434)")
    parser.add_argument("--list-models", "-l", action="store_true", help="List available local Ollama models and exit")
    parser.add_argument("--temperature", "-t", type=float, default=0.2, help="Sampling temperature (0.0 to 1.0)")
    args = parser.parse_args()

    print("=" * 60)
    print("  AI Resume Profile Matcher - Ollama Client & Diagnostics")
    print("=" * 60)

    # Step 1: Ensure ollama python library is present
    ollama_pkg = ensure_ollama_installed()

    # Step 2: Check server status
    print(f"[*] Checking Ollama server at {args.host}...")
    is_running, available_models = check_ollama_server(args.host)

    if not is_running:
        print("\n[!] ERROR: Ollama server is NOT running or not reachable.")
        print(f"    Target host: {args.host}")
        print("\nTo fix this:")
        print("  1. Make sure Ollama is installed (https://ollama.com).")
        print("  2. Start the Ollama server in a terminal:")
        print("       ollama serve")
        print("     Or launch the Ollama desktop app on macOS.")
        print("  3. Pull a model if you haven't yet, e.g.:")
        print("       ollama pull llama3.2")
        print("  4. Re-run this script:")
        print("       python3 run_ollama.py\n")
        sys.exit(1)

    print("[✓] Ollama server is online!")

    # Step 3: Handle models
    if available_models:
        print(f"[✓] Found {len(available_models)} local model(s):")
        for m in available_models:
            print(f"    • {m}")
    else:
        print("\n[!] Warning: Ollama server is running, but no models were found locally.")
        print("    Please pull a model first using:")
        print("       ollama pull llama3.2")
        print("    (or 'ollama pull mistral', 'ollama pull phi3')\n")
        if not args.list_models and not args.model:
            sys.exit(1)

    if args.list_models:
        return

    # Select model
    chosen_model = args.model
    if not chosen_model:
        # Prefer llama3.2 or first available
        if "llama3.2:latest" in available_models or "llama3.2" in available_models:
            chosen_model = "llama3.2"
        elif available_models:
            chosen_model = available_models[0]
        else:
            chosen_model = "llama3.2"

    print(f"\n[*] Active Model: {chosen_model}")
    print(f"[*] Temperature:  {args.temperature}")
    print(f"[*] Prompt:\n    \"{args.prompt}\"\n")
    print("[-] Generating response from Ollama (please wait)...")

    try:
        response = query_ollama(
            prompt=args.prompt,
            model=chosen_model,
            host=args.host,
            temperature=args.temperature
        )
        print("\n" + "=" * 60)
        print("  Ollama Response:")
        print("=" * 60)
        print(response)
        print("=" * 60)
        print("\n[✓] Ollama integration is verified and operational!\n")
    except Exception as err:
        print(f"\n[!] Error during model inference: {err}")
        print("    Ensure the model is pulled: ollama pull", chosen_model)
        sys.exit(1)


if __name__ == "__main__":
    main()

