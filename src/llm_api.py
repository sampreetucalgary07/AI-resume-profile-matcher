import os
import json
import urllib.request
import urllib.error
import google.generativeai as genai

try:
    from utils import load_json
except ImportError:
    from src.utils import load_json

api_keys = {}
if os.path.exists("api_keys.json"):
    try:
        api_keys = load_json("api_keys.json")
    except Exception:
        api_keys = {}


def is_ollama_model(model_name: str) -> bool:
    """Check whether a model name refers to an Ollama model."""
    if not model_name:
        return False
    lower = str(model_name).lower()
    if lower.startswith("ollama/") or lower.startswith("ollama:"):
        return True
    # Common local Ollama model families
    ollama_families = (
        "llama", "mistral", "mixtral", "phi", "gemma", "qwen", "deepseek",
        "codellama", "starcoder", "vicuna", "tinyllama", "orca", "neural-chat"
    )
    return any(lower.startswith(fam) for fam in ollama_families)


def gemini_model(api_key = None, model_name = "gemini-1.5-flash"):
    key = api_key or api_keys.get("google_api_studio") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("Google Gemini API key not found. Please provide it in api_keys.json or GEMINI_API_KEY environment variable.")
    genai.configure(api_key=key)
    model = genai.GenerativeModel(model_name, system_instruction="You are an expert resume builder.")   
    return model


def call_gemini_api(input_text, model, temperature):
    """
    Call the Google Gemini API to generate text based on user input.
    """
    response = model.generate_content(
        input_text,
        generation_config=genai.types.GenerationConfig(temperature=temperature),
        stream=False
    )
    response = response.candidates[0].content.parts[0].text
    return response


def call_ollama_api(input_text, model_name="llama3.2", temperature=0.2, host=None):
    """
    Call the local Ollama server to generate text based on user input.
    Supports the 'ollama' Python library if available, with direct HTTP fallback.
    """
    clean_host = (host or os.environ.get("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")
    clean_model = model_name.replace("ollama/", "").replace("ollama:", "")

    # Method 1: Using 'ollama' Python library
    try:
        import ollama
        client = ollama.Client(host=clean_host)
        res = client.generate(
            model=clean_model,
            prompt=input_text,
            options={"temperature": float(temperature)}
        )
        return res.get("response", "").strip()
    except Exception:
        pass

    # Method 2: Direct HTTP request fallback
    endpoint = f"{clean_host}/api/generate"
    payload = json.dumps({
        "model": clean_model,
        "prompt": input_text,
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
    except urllib.error.URLError as err:
        raise RuntimeError(
            f"Could not connect to Ollama server at {clean_host}. "
            f"Ensure Ollama is running ('ollama serve') and model '{clean_model}' is pulled. Error: {err}"
        )


def call_llm(input_text, model_name="gemini-1.5-flash", temperature=0.2):
    """
    Unified LLM call: routes to local Ollama or Google Gemini depending on the model name.
    """
    if is_ollama_model(model_name):
        return call_ollama_api(input_text, model_name=model_name, temperature=temperature)
    else:
        model = gemini_model(model_name=model_name)
        return call_gemini_api(input_text, model=model, temperature=temperature)
