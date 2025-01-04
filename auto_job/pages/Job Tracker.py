import streamlit as st
# import os
import pandas as pd
import datetime
from src.sections import display_job_tracker_interface    

st.set_page_config(page_title="AI job tracker", layout="wide")

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS file
load_css("auto_job/assets/styles.css")

df = pd.read_csv("auto_job/data/job_tracker/job_applications.csv")
df['Date'] = pd.to_datetime(df['Date'])

display_job_tracker_interface()


if "job_tracker_data_frame" not in st.session_state:
    st.session_state.job_tracker_data_frame = df

config = {
    'Date': st.column_config.DateColumn('Date',required=True,default=datetime.datetime.now().date()),
    'Company': st.column_config.TextColumn('Company',required=True),
    'Position': st.column_config.TextColumn('Position',required=True),
    'Link': st.column_config.LinkColumn('Link',required=True),
    'Applied': st.column_config.CheckboxColumn('Applied',required=True, default=False),
    'Optimized': st.column_config.CheckboxColumn('Optimized',required=True, default=False),
    'LinkedIn Reach': st.column_config.CheckboxColumn('LinkedIn Reach',required=True, default=False),
    'Cold Email': st.column_config.CheckboxColumn('Cold Email',required=True, default=False),
    'Selected': st.column_config.CheckboxColumn('Selected',required=True, default=False),
    'Stage': st.column_config.SelectboxColumn('Stage', default='Applied',
                                              options=['Applied', 'Interview', 'Offer', 'Rejected'],
                                              required=True)
    
    
}


def on_change_function():
    st.session_state.dataframe_changed = True

st.session_state.job_tracker_data_frame = st.data_editor(df, 
                           use_container_width=True,num_rows="dynamic", 
                           column_config=config,
                           key="job_tracker",width=1000,height=500,
                           on_change=on_change_function
)



if st.session_state.dataframe_changed:
    if st.button("Save Changes"):
        st.session_state.save_change_button = True
        
        with st.spinner("Saving changes..."):

            st.session_state.job_tracker_data_frame.to_csv("auto_job/data/job_tracker/job_applications.csv", index=False)
        
            st.warning("Changes saved successfully!")
            st.session_state.dataframe_changed = False


