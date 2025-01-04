import streamlit as st
from src.sections import (display_short_job_profile, display_match_score,
                          display_base_interface, sidebar_settings, display_base_toggle,
                          display_missing_skills, display_divide_missing_skills)

from src.modify_text import  generate_score, clean_job_profile, missing_skills, divide_missing_skills
from src.utils import load_json, format_resume
from src.initialize import init_values


# Set up Streamlit page configuration
st.set_page_config(page_title="AI Matcher", layout="wide")

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS file
load_css("assets/styles.css")

# Load the sidebar settings
model_name, temperature = sidebar_settings()

json_resume = load_json("data/resume_info.json")

resume_text = format_resume(json_resume)

init_values()

# Main app interface
st.title("AI Resume Job Profile Matcher")    

st.session_state.job_profile, st.session_state.resume_text = display_base_interface(st.session_state.job_profile)

# Use columns to arrange toggles side by side
(
    st.session_state.need_short_JB, st.session_state.need_match_score, 
    st.session_state.need_missing_skills, st.session_state.need_divide_missing_skills
) = display_base_toggle(st.session_state.need_short_JB, st.session_state.need_match_score, 
                        st.session_state.need_missing_skills, st.session_state.need_divide_missing_skills)


st.session_state["job_profile"] = st.session_state.job_profile

if st.button("Apply settings"):
    st.session_state.apply_settings_button = True
    
    if st.session_state.job_profile.strip():  # Check if input is not empty
            
        if st.session_state.need_short_JB:
            with st.spinner("Shortening Job Profile.."):
                st.session_state["short_job_profile"] = clean_job_profile(st.session_state.job_profile, model_name, temperature)      
                #display_short_job_profile(st.session_state["short_job_profile"])
        
        if st.session_state.need_match_score:
            with st.spinner("Calculating match score..."):
                st.session_state["match_score"] = generate_score(st.session_state["job_profile"], resume_text, model_name=model_name, temperature=temperature)
                #display_match_score(st.session_state["match_score"])
            
        if st.session_state.need_missing_skills:
            with st.spinner("Analyzing missing skills..."):
                st.session_state["response_miss_skills"] = missing_skills(st.session_state["job_profile"], resume_text, model_name=model_name, temperature=temperature)
                
                        
        if st.session_state.need_divide_missing_skills:
            with st.spinner("Dividing missing skills..."):    
                st.session_state["divide_missing_skills"] = divide_missing_skills(st.session_state["response_miss_skills"], model_name=model_name, temperature=temperature)
                
    else:
        st.error("Please enter some text.") 
        

if st.session_state.apply_settings_button :
    if "cleaned_job_profile" in st.session_state and st.session_state.need_short_JB:
        display_short_job_profile(st.session_state["short_job_profile"])
        
    if "match_score" in st.session_state:
        display_match_score(st.session_state["match_score"])
        
    if "response_miss_skills" in st.session_state:
        display_missing_skills(st.session_state["response_miss_skills"])
        
    if "divide_missing_skills" in st.session_state:
        display_divide_missing_skills(st.session_state["divide_missing_skills"])

        

# Add a footer to the app
st.markdown(
    """
    <footer>
        <hr>
        <p style="text-align:center; font-size:0.8em;">Built with &#10084;&#65039; by <a href="https://www.linkedin.com/in/sampreet-v-70b36b1a1" target="_blank">Sampreet Vaidya</a></p>
    </footer>
    """,
    unsafe_allow_html=True,
)

            
    
                
    
        


