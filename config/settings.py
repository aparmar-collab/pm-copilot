import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

try:
    JIRA_BASE_URL = st.secrets["JIRA_BASE_URL"]
    JIRA_EMAIL = st.secrets["JIRA_EMAIL"]
    JIRA_API_TOKEN = st.secrets["JIRA_API_TOKEN"]
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error(
        "Missing Jira configuration. "
        "Please set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN in Streamlit Secrets."
    )
    st.stop()
# JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
#JIRA_EMAIL = os.getenv("JIRA_EMAIL")
#JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
#GROQ_API_KEY = os.getenv("GROQ_API_KEY")
