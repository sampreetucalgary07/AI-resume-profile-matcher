# Add the current directory to sys.path
import  os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import load_json, clean_json_response
from llm_api import gemini_model, call_gemini_api
from prompts import shorten_job_profile_prompt, check_job_match_score_prompt, missing_skills_prompt, divide_missing_skills_prompt
# Importing the LLM API function


prompts = load_json("auto_job/prompts/prompts.json")# Load the prompts

# Load the LLM model

def clean_job_profile(input_text, model_name, temperature):
    """
    Clean the job profile text by removing extra spaces and newlines.
    """
    # Remove extra spaces and newlines
    model = gemini_model(model_name=model_name)
    
    input_text = shorten_job_profile_prompt(input_text)
    
    cleaned_job_profile = call_gemini_api(input_text, model=model, temperature=temperature )
    
    
    #cleaned_job_profile = " ".join(input_text.split())
    return cleaned_job_profile
    

def generate_score(job_profile, resume_text, model_name, temperature):
    """
    Generate a match score based on the user input.
    """
    model = gemini_model(model_name=model_name)
    input_text = check_job_match_score_prompt(job_profile, resume_text)
    response = call_gemini_api(input_text, model=model, temperature=temperature)
    match_score = int(response)
    return match_score

def missing_skills(job_profile, resume_text, model_name, temperature):
    """
    Generate a list of missing skills based on the user input.
    """
    model = gemini_model(model_name=model_name)
    input_text = missing_skills_prompt(job_profile, resume_text)
    response = call_gemini_api(input_text, model=model, temperature=temperature)
    response = clean_json_response(response)

    return response

def divide_missing_skills(missing_skills, model_name, temperature):
    """
    Divide the missing skills into categories.
    """
    model = gemini_model(model_name=model_name)
    input_text = divide_missing_skills_prompt(missing_skills)
    response = call_gemini_api(input_text, model=model, temperature=temperature)
    response = clean_json_response(response)
 
    return response


