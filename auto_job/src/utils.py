import json

def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)
    

def format_resume(json_data):
    """
    Formats a JSON resume into a readable string for display in Streamlit.

    Args:
    - json_data (dict): The resume details in JSON format.

    Returns:
    - str: A formatted string representing the resume details.
    """
    formatted_text = []

    if "education" in json_data:
        formatted_text.append("Education:")
        formatted_text.append("----------")
        formatted_text.append(f"- *Degree*: {json_data['education']['degree']}")
        formatted_text.append(f"- *fieldOfStudy*: {json_data['education']['fieldOfStudy']}")
        formatted_text.append(f"- *School*: {json_data['education']['school']}")
        formatted_text.append(f"- *Courses*: {', '.join(json_data['education']['courses'])}")
            
        formatted_text.append("")  # Add blank line for spacing
            
    
    # Work Experience
    if "work" in json_data:
        formatted_text.append("Work Experience:")
        formatted_text.append("-----------------")
        for i, (company_key, company_details) in enumerate(json_data["work"].items(), 1):
            formatted_text.append(f"{i}. **{company_details['name']}**")
            formatted_text.append(f"   *Position*: {company_details['position']}")
            formatted_text.append(f"   *Duration*: {company_details['startDate']} - {company_details['endDate']}")
            formatted_text.append("   *Highlights*:")
            for highlight in company_details["highlights"]:
                formatted_text.append(f"   - {highlight}")
            formatted_text.append("")  # Add blank line for spacing

    # Skills
    if "skills" in json_data:
        formatted_text.append("Skills:")
        formatted_text.append("-------")
        for skill_category, skills in json_data["skills"].items():
            formatted_text.append(f"- **{skill_category}**: {', '.join(skills)}")

    return "\n".join(formatted_text)

def clean_json_response(response_text):
    """
    Clean the JSON parameter by removing extra spaces and newlines.
    """
    response = response_text.replace("json", "")
    response = response.strip('```').strip('\n').strip('```').strip('\n')
    response = json.loads(response)
    return response

