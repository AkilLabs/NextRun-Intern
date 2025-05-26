import logging
from dotenv import load_dotenv
import os
import streamlit as st
from src.agent.qa_agent import QAEngineerAgent
from src.agent.qa_views import QAViews

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

def main():
    # Set page config
    st.set_page_config(
        page_title="QAEngineer-X",
        page_icon="🧪",
        layout="wide"
    )

    # Initialize QA Engineer Agent
    if 'qa_agent' not in st.session_state:
        st.session_state.qa_agent = QAEngineerAgent()

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.warning("⚠️ OpenAI API key not set. Please set it in the Settings page.")
        st.session_state.api_key_set = False
    else:
        if not getattr(st.session_state, 'api_key_set', False):
            st.session_state.qa_agent.initialize_llm(api_key)
            st.session_state.api_key_set = True

    # Render sidebar and get selected menu
    menu = QAViews.render_sidebar()

    # Render selected view
    if menu == "Test Creation":
        QAViews.render_test_creation()
    elif menu == "Test Execution":
        QAViews.render_test_execution()
    elif menu == "Code Review":
        QAViews.render_code_review()
    elif menu == "Bug Triage":
        QAViews.render_bug_triage()
    elif menu == "Impact Analysis":
        QAViews.render_impact_analysis()
    elif menu == "Data Validation":
        QAViews.render_data_validation()
    elif menu == "Settings":
        st.title("Settings")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Enter your OpenAI API key"
        )
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.session_state.qa_agent.initialize_llm(api_key)
            st.session_state.api_key_set = True
            st.success("API key updated!")

if __name__ == '__main__':
    main()
