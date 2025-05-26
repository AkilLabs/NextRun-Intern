from typing import Dict, List
import streamlit as st

class QAViews:
    @staticmethod
    def render_sidebar():
        st.sidebar.title("QA Engineer Agent")
        
        menu = st.sidebar.radio(
            "Menu",
            ["Test Creation", "Test Execution", "Code Review", "Bug Triage", 
             "Impact Analysis", "Data Validation", "Settings"]
        )
        return menu

    @staticmethod
    def render_test_creation():
        st.title("Test Creation")
        
        # Input methods
        input_method = st.radio(
            "Select Input Method",
            ["Jira Story", "Code Analysis", "Manual Entry"]
        )

        if input_method == "Jira Story":
            story = st.text_area("Enter Jira Story", height=150, key="jira_story")
            if st.button("Generate Test Cases from Story"):
                if not story:
                    st.error("Please enter a Jira story")
                else:
                    with st.spinner("Generating test cases..."):
                        qa_agent = st.session_state.qa_agent
                        import asyncio
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            # Wrap the story in a dictionary with a 'content' key
                            input_data = {'content': story}
                            result = loop.run_until_complete(qa_agent.generate_test_cases(input_data))
                            loop.close()

                            if result.get("status") == "success":
                                st.markdown("### Generated Test Cases")
                                st.markdown(result['data']['test_cases'])
                            else:
                                st.error(result.get("message", "An unknown error occurred"))
                        except Exception as e:
                            st.error(f"Error generating test cases: {str(e)}")

        elif input_method == "Code Analysis":
            uploaded_files = st.file_uploader("Upload Code Files", 
                                            accept_multiple_files=True,
                                            type=['py', 'js', 'java', 'cpp', 'zip'],
                                            key="code_files")
            
            if uploaded_files:
                st.write(f"Uploaded {len(uploaded_files)} files")
                if st.button("Generate Test Cases from Code"):
                    with st.spinner("Analyzing code and generating test cases..."):
                        # Create a temporary directory for the files
                        import tempfile
                        import zipfile
                        import shutil
                        import os

                        with tempfile.TemporaryDirectory() as temp_dir:
                            # Process each uploaded file
                            for uploaded_file in uploaded_files:
                                if uploaded_file.name.endswith('.zip'):
                                    # Extract zip file
                                    zip_path = os.path.join(temp_dir, uploaded_file.name)
                                    with open(zip_path, 'wb') as f:
                                        f.write(uploaded_file.getvalue())
                                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                        zip_ref.extractall(temp_dir)
                                else:
                                    # Save individual file
                                    file_path = os.path.join(temp_dir, uploaded_file.name)
                                    with open(file_path, 'wb') as f:
                                        f.write(uploaded_file.getvalue())
                            
                            # Analyze the code and generate test cases
                            qa_agent = st.session_state.qa_agent
                            
                            import asyncio
                            try:
                                # Run the async function in a new event loop
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                result = loop.run_until_complete(qa_agent.analyze_code(temp_dir))
                                loop.close()

                                if result.get("status") == "success":
                                    st.success(f"Successfully analyzed {result['data']['total_files']} files")
                                    
                                    # Display files analyzed
                                    with st.expander("Files Analyzed"):
                                        for file in result['data']['files_analyzed']:
                                            st.write(f"- {file}")
                                    
                                    # Display test cases
                                    st.markdown("### Generated Test Cases")
                                    st.markdown(result['data']['test_cases'])
                                else:
                                    st.error(result.get("message", "An unknown error occurred"))
                            except Exception as e:
                                st.error(f"Error processing code: {str(e)}")

        else:  # Manual Entry
            description = st.text_area("Enter Test Description", height=150, key="test_desc")
            if st.button("Generate Test Cases from Description"):
                if not description:
                    st.error("Please enter a test description")
                else:
                    with st.spinner("Generating test cases..."):
                        qa_agent = st.session_state.qa_agent
                        import asyncio
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            # Wrap the description in a dictionary with a 'content' key
                            input_data = {'content': description}
                            result = loop.run_until_complete(qa_agent.generate_test_cases(input_data))
                            loop.close()

                            if result.get("status") == "success":
                                st.markdown("### Generated Test Cases")
                                st.markdown(result['data']['test_cases'])
                            else:
                                st.error(result.get("message", "An unknown error occurred"))
                        except Exception as e:
                            st.error(f"Error generating test cases: {str(e)}")

        # Results section
        st.subheader("Generated Test Cases")

    @staticmethod
    def render_test_execution():
        st.title("Test Execution")
        
        # Test suite selection
        st.selectbox("Select Test Suite", ["Regression", "Integration", "UAT"])
        
        # Environment selection
        st.selectbox("Environment", ["Dev", "QA", "Staging"])
        
        st.button("Run Tests")

        # Results section
        st.subheader("Test Results")
        st.empty()  # Placeholder for test results

    @staticmethod
    def render_code_review():
        st.title("Code Review")
        
        # Code input
        st.file_uploader("Upload Code for Review")
        
        # Analysis options
        st.multiselect(
            "Analysis Options",
            ["Test Coverage", "Security", "Performance", "Best Practices"]
        )
        
        st.button("Analyze Code")

    @staticmethod
    def render_impact_analysis():
        st.title("Impact Analysis")
        
        # Code changes input
        st.text_area("Enter Code Changes", height=150)
        
        # Analysis scope
        st.multiselect(
            "Analysis Scope",
            ["Unit Tests", "Integration Tests", "UI Tests", "Data Validation"]
        )
        
        st.button("Analyze Impact")

    @staticmethod
    def render_data_validation():
        st.title("Data Validation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Expected Data")
            st.file_uploader("Upload Expected Data")
            
        with col2:
            st.subheader("Actual Data")
            st.file_uploader("Upload Actual Data")
            
        st.button("Compare Data")
