# Add the current directory to sys.path
import os
import sys
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import load_json, clean_json_response
from llm_api import gemini_model, call_gemini_api, call_llm
from prompts import (
    shorten_job_profile_prompt,
    check_job_match_score_prompt,
    missing_skills_prompt,
    divide_missing_skills_prompt
)


def clean_job_profile(input_text, model_name, temperature):
    """
    Clean and summarize the job profile text.
    """
    input_text = shorten_job_profile_prompt(input_text)
    cleaned_job_profile = call_llm(input_text, model_name=model_name, temperature=temperature)
    return cleaned_job_profile


def generate_score(job_profile, resume_text, model_name, temperature):
    """
    Generate a match score based on the user input.
    """
    input_text = check_job_match_score_prompt(job_profile, resume_text)
    response = call_llm(input_text, model_name=model_name, temperature=temperature)
    
    # Robustly parse integer score (handles extra prose or formatting from local LLMs)
    cleaned = str(response).strip()
    match = re.search(r'\b(100|[1-9]?[0-9])\b', cleaned)
    if match:
        return int(match.group(0))
    try:
        return min(max(int(cleaned), 0), 100)
    except ValueError:
        return 50


def missing_skills(job_profile, resume_text, model_name, temperature):
    """
    Generate a list of missing skills categorized into domains.
    """
    input_text = missing_skills_prompt(job_profile, resume_text)
    response = call_llm(input_text, model_name=model_name, temperature=temperature)
    response = clean_json_response(response)
    return response


def divide_missing_skills(missing_skills, model_name, temperature):
    """
    Divide the missing skills into 3 job roles.
    """
    input_text = divide_missing_skills_prompt(missing_skills)
    response = call_llm(input_text, model_name=model_name, temperature=temperature)
    response = clean_json_response(response)
    return response
