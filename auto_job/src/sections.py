import streamlit as st
from src.utils import load_json, format_resume

config_path = "auto_job/config.json" # Path to the config file
config = load_json(config_path)


# ------------------- HOME PAGE -------------------

def sidebar_settings():
    """
    Display the sidebar settings for the user.
    """
    st.sidebar.header("Settings")
    model_list = config["model_list"]
    model_name = st.sidebar.selectbox("Choose a Model", model_list)  # Choose LLM model
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2)  # Adjust creativity of responses
    
    return model_name, temperature  

def display_base_interface(session_input_text):
    col1, col2 = st.columns(2, gap="small", vertical_alignment="top", border=True)

    with col1:
        st.header("Job Profile", divider= "rainbow")
        input_text = st.text_area("Enter Job profile:",value= session_input_text, placeholder="Type something...", height = 500)

    json_resume = load_json("auto_job/data/resume_info.json")

    resume_text = format_resume(json_resume)
    with col2:
        st.header("Resume", divider= "rainbow")
        # Split the text into manageable chunks
        resume_text = st.text_area("Uploaded resume data:", value=resume_text, height=500,disabled=True)
        
    return input_text, resume_text

def display_base_toggle(session_need_short_JB, session_need_match_score, 
                        session_need_missing_skills, session_need_divide_missing_skills):
    # Use columns to arrange toggles side by side
    col1, col2, col3, col4 = st.columns(4,vertical_alignment="center", border=True)

    with col1:
        need_short_JB = st.toggle("Shorten Job Profile", value=session_need_short_JB)

    with col2:
        need_match_score = st.toggle("Calculate Match Score", value=session_need_match_score)

    with col3:
        need_missing_skills = st.toggle("Find Missing Skills", value=session_need_missing_skills)
        
    with col4:
        need_divide_missing_skills = st.toggle("Divide Missing Skills", value=session_need_divide_missing_skills)
        
    return need_short_JB, need_match_score, need_missing_skills, need_divide_missing_skills
    

def display_short_job_profile(clean_job_profile):
    """
    Display the short job profile based on the user input.
    
    """
    st.header("Short Job Profile", divider= "rainbow")
    st.write(clean_job_profile)

def display_match_score(match_score):
    """
    Display the match score based on the user input.
    """
    
    bar_color = "green" if match_score >= 70 else "orange" if match_score >= 40 else "red"
    message = "Good match!" if match_score >= 70 else "Fair match!" if match_score >= 40 else "Poor match!"
            
    # Display the match score as a progress bar
    st.header("Job Match Score:")
    st.markdown(f"""
<div class="progress-bar-container">
<div class="progress-bar" style="width: {match_score}%; background-color: {bar_color};">
{match_score}%
</div>
</div>
""", unsafe_allow_html=True)
    st.write(message)
        
def display_missing_skills(response_miss_skills):
    """
    Display the missing skills based on the user input.
    """ 
    
    
    # Display missing skills
    st.header("Missing Skills", divider= "rainbow")

    # First row of 3 columns
    col1, col2, col3 = st.columns(3,vertical_alignment="top", border=True)

    with col1:
        st.subheader("Programming Languages")
        if response_miss_skills["Programming Languages"]:
            st.markdown("\n".join(f"- {item}" for item in response_miss_skills["Programming Languages"]))
        else:
            st.write("No missing programming languages.")

    with col2:
        st.subheader("Tools")
        if response_miss_skills["Tools"]:
            st.markdown("\n".join(f"- {item}" for item in response_miss_skills["Tools"]))
        else:
            st.write("No missing tools.")

    with col3:
        st.subheader("Libraries")
        if response_miss_skills["Libraries"]:
            st.markdown("\n".join(f"- {item}" for item in response_miss_skills["Libraries"]))
        else:
            st.write("No missing libraries.")

    # Second row of 3 columns
    col4, col5, = st.columns(2,vertical_alignment="top", border=True)

    with col4:
        # st.subheader("Frameworks")
        # if response_miss_skills["Frameworks"]:
        #     st.markdown("\n".join(f"- {item}" for item in response_miss_skills["Frameworks"]))
        # else:
        #     st.write("No missing frameworks.")
        st.subheader("Soft Skills")
        if response_miss_skills["Soft Skills"]:
            st.markdown("\n".join(f"- {item}" for item in response_miss_skills["Soft Skills"]))
        else:
            st.write("No missing soft skills.")

    with col5:
        
        st.subheader("Miscellaneous")
        if response_miss_skills["Miscellaneous"]:
            st.markdown("\n".join(f"- {item}" for item in response_miss_skills["Miscellaneous"]))
        else:
            st.write("No missing miscellaneous skills.")
            
    st.write("Missing skills analysis complete.")
            
                
def display_divide_missing_skills(response_divide_missing_skills):
    """
    Divide the missing skills into categories.
    """
    
    st.header("Divided Missing Skills", divider= "rainbow")
    col1, col2, col3 = st.columns(3,vertical_alignment="top", border=True)
    
    
    with col1:
        st.subheader("Software Developer")
        if response_divide_missing_skills["Software Developer"]:
            st.markdown("\n".join(f"- {item}" for item in response_divide_missing_skills["Software Developer"]))
        else:
            st.write("No missing skills for Software Developer.")
        
    with col2:
        st.subheader("ML Engineer/Data Scientist")
        if response_divide_missing_skills["ML Engineer/Data Scientist"]:
            #for key in response_divide_missing_skills["ML Engineer/Data Scientist"]:
            st.markdown("\n".join(f"- {item}" for item in response_divide_missing_skills["ML Engineer/Data Scientist"]))
        else:
            st.write("No missing skills for Data Scientist.")
            
    with col3:
        st.subheader("Data Analyst")
        if response_divide_missing_skills["Data Analyst"]:
            st.markdown("\n".join(f"- {item}" for item in response_divide_missing_skills["Data Analyst"]))
        else:
            st.write("No missing skills for Data Analyst.")
                
    st.write("Missing skills division complete.")
    return response_divide_missing_skills




# ------------------- JOB TRACKER PAGE -------------------

def display_job_tracker_interface():
    st.title("Job Tracker")
    st.write("")

    # st.header("Job Tracker", divider= "rainbow")
    # input_text = st.text_area("Enter Job Tracker:", placeholder="Type something...", height = 500)
    

    # st.header("LinkedIn Message", divider= "rainbow")
    # input_text = st.text_area("Enter LinkedIn Message:", placeholder="Type something...", height = 500)
    

