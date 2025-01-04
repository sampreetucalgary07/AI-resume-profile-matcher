import streamlit as st




def init_values():
    if "job_role" not in st.session_state:
        st.session_state.job_role = ""
        
    if "job_profile" not in st.session_state:
        st.session_state.job_profile = ""

    if "company_name" not in st.session_state:
        st.session_state.company_name = ""
        
    if "company_profile" not in st.session_state:
        st.session_state.company_profile = ""
        
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""
        
    if "cover_letter_text" not in st.session_state:
        st.session_state["cover_letter_text"] = ""

    if "recruiter_name" not in st.session_state:
        st.session_state.recruiter_name = ""

    if "cleaned_job_profile" not in st.session_state:
        st.session_state.cleaned_job_profile = ""

    if "cleaned_achievements" not in st.session_state:
        st.session_state.cleaned_achievements = ""

    
    if "need_short_JB" not in st.session_state:
        st.session_state.need_short_JB = False

    # Buttons
    if "generate_cover_letter_button" not in st.session_state:
        st.session_state["generate_cover_letter_button"] = False

    if "cover_letter_generated" not in st.session_state:
        st.session_state["cover_letter_generated"] = False
    
    
    if "need_match_score" not in st.session_state:
        st.session_state.need_match_score = False

    if "need_missing_skills" not in st.session_state:
        st.session_state.need_missing_skills = False

    if "need_divide_missing_skills" not in st.session_state:
        st.session_state.need_divide_missing_skills = False
    if "dataframe_changed" not in st.session_state:
        st.session_state.dataframe_changed = False

    if "save_change_button" not in st.session_state:
        st.session_state.save_change_button = False
        
    if "generate_cold_email_button" not in st.session_state:
        st.session_state.generate_cold_email_button = False

    if "generate_cold_message_button" not in st.session_state:
        st.session_state.generate_cold_message_button = False
        
    # Button to trigger text generation
    if "apply_settings_button" not in st.session_state:
        st.session_state.apply_settings_button = False