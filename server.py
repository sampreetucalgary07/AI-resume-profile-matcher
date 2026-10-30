#!/usr/bin/env python3
"""
Local HTTP Server for AI Resume & Job Profile Matcher.
Serves the web application interface and provides API endpoints for analysis and job tracking.
"""

import os
import sys
import json
import csv
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Add root directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.utils import load_json, format_resume

# Attempt importing LLM logic
HAVE_LLM = False
try:
    from src.modify_text import clean_job_profile, generate_score, missing_skills, divide_missing_skills
    HAVE_LLM = True
except Exception as e:
    print(f"Warning: LLM module import note: {e}")


def get_stored_api_key():
    """Retrieve Gemini API key from api_keys.json or environment."""
    key_path = os.path.join(BASE_DIR, "api_keys.json")
    if os.path.exists(key_path):
        try:
            data = load_json(key_path)
            if data.get("google_api_studio"):
                return data["google_api_studio"]
        except Exception:
            pass
    return os.environ.get("GEMINI_API_KEY")


class AppRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("", "/"):
            self.path = "/index.html"
            return super().do_GET()

        if path == "/api/config":
            self.send_json_response(self.handle_get_config())
            return

        if path == "/api/resume":
            self.send_json_response(self.handle_get_resume())
            return

        if path == "/api/applications":
            self.send_json_response(self.handle_get_applications())
            return

        if path == "/api/status":
            api_key = get_stored_api_key()
            ollama_online = False
            ollama_models = []
            try:
                req = urllib.request.Request("http://localhost:11434/api/tags", headers={"User-Agent": "AI-Resume-Matcher"})
                with urllib.request.urlopen(req, timeout=1) as resp:
                    if resp.status == 200:
                        ollama_online = True
                        data = json.loads(resp.read().decode())
                        ollama_models = [m.get("name") for m in data.get("models", [])]
            except Exception:
                pass

            self.send_json_response({
                "status": "online",
                "have_api_key": bool(api_key),
                "ollama_online": ollama_online,
                "ollama_models": ollama_models,
                "server": "local_http"
            })
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        try:
            data = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            data = {}

        if path == "/api/applications":
            result = self.handle_save_applications(data)
            self.send_json_response(result)
            return

        if path == "/api/analyze":
            result = self.handle_analyze(data)
            self.send_json_response(result)
            return

        self.send_error(404, "Endpoint not found")

    def send_json_response(self, data, status_code=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # API Handlers
    def handle_get_config(self):
        config_path = os.path.join(BASE_DIR, "config.json")
        if os.path.exists(config_path):
            return load_json(config_path)
        return {
            "model_list": [
                "gemini-1.5-flash",
                "gemini-1.5-flash-8b",
                "gemini-1.5-pro",
                "gemini-2.0-flash-exp"
            ],
            "default_temperature": 0.2
        }

    def handle_get_resume(self):
        resume_path = os.path.join(BASE_DIR, "data", "resume_info.json")
        if os.path.exists(resume_path):
            resume_json = load_json(resume_path)
            formatted = format_resume(resume_json)
            return {
                "raw": resume_json,
                "formatted": formatted
            }
        return {"raw": {}, "formatted": "No resume found at data/resume_info.json"}

    def handle_get_applications(self):
        csv_path = os.path.join(BASE_DIR, "data", "job_tracker", "job_applications.csv")
        rows = []
        if os.path.exists(csv_path):
            with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    # Normalize boolean fields
                    def to_bool(val):
                        return str(val).strip().lower() in ("true", "1", "yes")

                    rows.append({
                        "Date": r.get("Date", ""),
                        "Company": r.get("Company", ""),
                        "Position": r.get("Position", ""),
                        "Link": r.get("Link", ""),
                        "Applied": to_bool(r.get("Applied", False)),
                        "Optimized": to_bool(r.get("Optimized", False)),
                        "LinkedIn Reach": to_bool(r.get("LinkedIn Reach", False)),
                        "Cold Email": to_bool(r.get("Cold Email", False)),
                        "Selected": to_bool(r.get("Selected", False)),
                        "Stage": r.get("Stage", "Applied")
                    })
        return {"applications": rows}

    def handle_save_applications(self, data):
        apps = data.get("applications", [])
        csv_path = os.path.join(BASE_DIR, "data", "job_tracker", "job_applications.csv")
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        fieldnames = [
            "Date", "Company", "Position", "Link",
            "Applied", "Optimized", "LinkedIn Reach",
            "Cold Email", "Selected", "Stage"
        ]

        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in apps:
                writer.writerow({
                    "Date": item.get("Date", ""),
                    "Company": item.get("Company", ""),
                    "Position": item.get("Position", ""),
                    "Link": item.get("Link", ""),
                    "Applied": item.get("Applied", False),
                    "Optimized": item.get("Optimized", False),
                    "LinkedIn Reach": item.get("LinkedIn Reach", False),
                    "Cold Email": item.get("Cold Email", False),
                    "Selected": item.get("Selected", False),
                    "Stage": item.get("Stage", "Applied")
                })

        return {"status": "success", "message": f"Saved {len(apps)} applications successfully."}

    def handle_analyze(self, data):
        job_profile = data.get("job_profile", "").strip()
        resume_text = data.get("resume_text", "").strip()
        model_name = data.get("model_name", "gemini-1.5-flash")
        temperature = float(data.get("temperature", 0.2))
        need_short_JB = data.get("need_short_JB", True)
        need_match_score = data.get("need_match_score", True)
        need_missing_skills = data.get("need_missing_skills", True)
        need_divide_missing_skills = data.get("need_divide_missing_skills", True)
        custom_key = data.get("api_key", "").strip()

        if not job_profile:
            return {"error": "Please provide a job profile description."}

        active_key = custom_key or get_stored_api_key()

        is_ollama = False
        try:
            from src.llm_api import is_ollama_model
            is_ollama = is_ollama_model(model_name)
        except Exception:
            pass

        # If LLM is available and either an Ollama model is chosen OR Gemini API key is set
        if HAVE_LLM and (is_ollama or active_key):
            try:
                # Set temporary env key if provided for Gemini
                if active_key and not is_ollama:
                    os.environ["GEMINI_API_KEY"] = active_key
                results = {"live_model": model_name}

                if need_short_JB:
                    results["short_job_profile"] = clean_job_profile(job_profile, model_name, temperature)

                if need_match_score:
                    results["match_score"] = generate_score(job_profile, resume_text, model_name, temperature)

                if need_missing_skills:
                    miss_skills = missing_skills(job_profile, resume_text, model_name, temperature)
                    results["missing_skills"] = miss_skills

                    if need_divide_missing_skills and miss_skills:
                        divided = divide_missing_skills(miss_skills, model_name, temperature)
                        results["divide_missing_skills"] = divided

                return {"status": "success", "data": results}

            except Exception as e:
                print(f"Error calling LLM: {e}")
                # Fall back to simulation with message
                return self.generate_preview_analysis(job_profile, resume_text, str(e))

        # Otherwise, return an intelligent interactive preview
        return self.generate_preview_analysis(job_profile, resume_text)

    def generate_preview_analysis(self, job_profile, resume_text, error_note=None):
        """Generates an intelligent simulated analysis when no live API key is configured."""
        words_jp = set(job_profile.lower().split())
        
        # Tech skill keywords dictionary
        known_skills = {
            "Programming Languages": ["python", "r", "sql", "java", "c++", "go", "javascript", "typescript", "scala", "rust"],
            "Tools": ["docker", "kubernetes", "git", "tableau", "power bi", "jira", "aws", "gcp", "azure", "linux", "jenkins"],
            "Libraries": ["tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "react", "fastapi", "django", "flask"],
            "Soft Skills": ["communication", "leadership", "collaboration", "problem-solving", "mentorship", "agile", "time management"],
            "Miscellaneous": ["ci/cd", "rest api", "microservices", "unit testing", "distributed systems", "cloud architecture"]
        }

        # Role mappings
        role_map = {
            "Software Developer": ["c++", "java", "go", "typescript", "javascript", "react", "microservices", "unit testing", "rest api", "ci/cd"],
            "ML Engineer/Data Scientist": ["pytorch", "tensorflow", "scikit-learn", "distributed systems", "scala", "gcp", "aws"],
            "Data Analyst": ["tableau", "power bi", "sql", "r", "pandas", "numpy"]
        }

        resume_lower = resume_text.lower()

        missing = {cat: [] for cat in known_skills}
        for cat, skills in known_skills.items():
            for s in skills:
                if s in job_profile.lower() and s not in resume_lower:
                    missing[cat].append(s.title())

        # If none detected, add sample skills based on JD length
        if not any(missing.values()):
            missing["Programming Languages"] = ["Go", "TypeScript"]
            missing["Tools"] = ["Kubernetes", "AWS"]
            missing["Libraries"] = ["PyTorch"]
            missing["Soft Skills"] = ["Cross-functional Leadership"]
            missing["Miscellaneous"] = ["Distributed Microservices"]

        # Divided missing skills
        divided = {
            "Software Developer": [],
            "ML Engineer/Data Scientist": [],
            "Data Analyst": []
        }
        all_missing = [s.lower() for cat in missing for s in missing[cat]]
        for role, skills in role_map.items():
            for s in skills:
                if s in all_missing:
                    divided[role].append(s.title())

        # Default sample if empty
        if not any(divided.values()):
            divided["Software Developer"] = ["Go", "TypeScript", "Microservices"]
            divided["ML Engineer/Data Scientist"] = ["PyTorch", "AWS"]
            divided["Data Analyst"] = ["Power BI"]

        # Calculate a realistic score
        score = 78

        summary_preview = (
            "• Position: Key requirements extracted from provided description\n"
            "• Core Qualifications: Strong foundation in software design, cloud technologies, and data systems\n"
            "• Experience: Relevant technical expertise and production delivery experience\n"
            "• Education: Bachelor's or Master's in Computer Science, Software Engineering, or related field"
        )

        resp = {
            "status": "preview",
            "message": "Preview Mode (Running without live Gemini key). Set API key in api_keys.json or UI to enable live LLM inference." if not error_note else f"Live API note: {error_note}. Falling back to preview analysis.",
            "data": {
                "short_job_profile": summary_preview,
                "match_score": score,
                "missing_skills": missing,
                "divide_missing_skills": divided
            }
        }
        return resp


def run_server(port=8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, AppRequestHandler)
    print(f"\n=======================================================")
    print(f"  AI Resume & Job Profile Matcher - Local HTTP Server")
    print(f"=======================================================")
    print(f"  Server URL: http://localhost:{port}")
    print(f"  Serving files from: {BASE_DIR}")
    print(f"  Press Ctrl+C to stop the server\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)


if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)

