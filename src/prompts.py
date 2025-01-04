import  os
import sys



def shorten_job_profile_prompt(job_profile):
    """
    Generate a input text prompt for the job profile.
    """
    text = f"You are a job profile shortener. Your task is to shorten the job profile to its key qualifications. Begin by removing any irrelevant information and focusing on the most important aspects. Use concise language to highlight the key skills and requirements. you need to make sure to extract relevant job skills/experience/education/any other special requirements required for the job. Here is the job profile: \n{job_profile}."
    return text

def check_job_match_score_prompt(job_profile, resume_text):
    """
    Generate a input text prompt for the match score.
    """
    
    text = f"You are an advanced match score calculator tasked with evaluating the alignment between a job profile and a resume. Begin by thoroughly comparing the two documents, focusing on key qualifications such as skills, experience, education, and certifications. For each major criterion, assign a score on a scale of 1-100, utilizing a customizable weighting system to calculate an overall match score. The default weights are as follows: skills (40%), experience (30%), education (20%), and certifications (10%). Additionally, identify any critical qualifications mentioned in the job profile that are absent from the resume. Conduct a keyword analysis to note the frequency of important terms from the job description within the resume. If applicable, assess the alignment of soft skills highlighted in the job profile. Furthermore, compare the required years of experience with the candidate's actual experience and consider any industry-specific knowledge or requirements indicated in the job profile. If the job profile doesn't seem like a job profile, score will be 0. OUTPUT SHOULD BE JUST DIGITS. Here is the resume: \n{resume_text}. Here is the job profile: \n{job_profile}."
    
    return text

def missing_skills_prompt(job_profile, resume_text):
    """
    Generate an input text prompt for the missing skills.
    """
    text = f"""You are an expert in analyzing job profiles and resumes to identify skill gaps. Your task is to compare the given job profile and resume, then list the skills mentioned in the job profile that are missing from the resume. Categorize these missing skills into: Programming Languages, Tools, Libraries, Soft Skills, and Miscellaneous.

    Output ONLY a JSON object with these categories as keys. The values should be arrays of missing skills. If a category has no missing skills, use an empty array. Be precise - only include skills explicitly mentioned in the job profile and clearly absent from the resume.

    The format of the JSON object should be as follows:
    {{
        "Programming Languages": ["skill1", "skill2"],
        "Tools": ["skill3", "skill4"],
        "Libraries": ["skill5", "skill6"],
        "Soft Skills": ["skill7", "skill8"],
        "Miscellaneous": ["skill9", "skill10"]
    }}

    Guidelines:
    - If a skill could fit multiple categories, place it in the most specific applicable category.
    - For ambiguous cases, use your best judgment to categorize consistently.
    - Soft Skills include interpersonal and non-technical professional skills.
    - Miscellaneous is for skills that don't fit the other categories.
    - If you can't determine if a skill is missing due to vague descriptions, omit it.

    Provide only the JSON output. Any input other than a job profile and resume pair should result in:
    {{
        "error": "Invalid input. Please provide both a job profile and a resume."
    }}

    Job Profile:
    {job_profile}

    Resume:
    {resume_text}"""    
    return text

def divide_missing_skills_prompt(missing_skills):
    
    """
    Generate a prompt to divide missing skills into non-overlapping categories.
    """
    text = f"""You are an expert in categorizing technical skills. Given the following missing skills from a resume, divide them into 3 NON-OVERLAPPING categories: 1) Software Developer, 2) ML Engineer/Data Scientist, and 3) Data Analyst.

    Important instructions:
    1. Analyze ONLY THE MISSING SKILLS provided.
    2. If a skill doesn't clearly fit into any of the three categories, do not include it.
    3. Ensure categories are mutually exclusive - each skill should appear in only one category.
    4. Produce your answer as a JSON object with the exact format specified below.

    The format of the JSON object should be as follows:
    {{
        "Software Developer": ["skill1", "skill2"],
        "ML Engineer/Data Scientist": ["skill3", "skill4"],
        "Data Analyst": ["skill5", "skill6"]
    }}

    If a category has no relevant skills, use an empty array for that category.

    Missing skills to categorize:
    {missing_skills}

    Provide only the JSON output, ensuring the JSON format is correct and adheres to the specified structure.
    """
    return text

