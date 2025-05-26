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
            if st.button("Generate Test Cases from Story", key="generate_story_button"):
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
                if st.button("Generate Test Cases from Code", key="generate_code_button"):
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
            if st.button("Generate Test Cases from Description", key="generate_desc_button"):
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
        test_suite = st.selectbox("Select Test Suite", ["Regression", "Integration", "UAT", "Smoke", "Performance"])
        
        # Environment selection
        environment = st.selectbox("Environment", ["Dev", "QA", "Staging", "Production"])
        
        # Input method for test details
        input_method = st.radio(
            "Test Input Method",
            ["Generated Test Cases", "Test Script Files", "Manual Test Steps"]
        )
        
        test_details = ""
        test_files = []
        
        if input_method == "Generated Test Cases":
            # Allow user to paste previously generated test cases
            test_details = st.text_area("Paste Generated Test Cases", height=150)
        elif input_method == "Test Script Files":
            # Allow users to upload test script files
            uploaded_files = st.file_uploader(
                "Upload Test Script Files", 
                accept_multiple_files=True,
                type=["py", "js", "feature", "robot", "java", "spec.js", "test.js", "spec.ts", "test.ts"]
            )
            
            if uploaded_files:
                test_files = [file.name for file in uploaded_files]
                test_details = f"Execute the following test files: {', '.join(test_files)}"
        else:  # Manual Test Steps
            test_details = st.text_area("Enter Manual Test Steps", height=150)
        
        # Additional test parameters
        with st.expander("Advanced Options"):
            retry_failed = st.checkbox("Retry Failed Tests", value=False)
            test_tags = st.text_input("Test Tags (comma-separated)")
            parallel_execution = st.slider("Parallel Execution Threads", 1, 10, 1)
            timeout = st.number_input("Test Timeout (seconds)", 30, 3600, 300)
        
        if st.button("Run Tests", key="execute_tests_button"):
            if not test_details and not test_files:
                st.error("Please provide test details or upload test files")
            else:
                with st.spinner("Executing tests..."):
                    # Call the QA agent
                    qa_agent = st.session_state.qa_agent
                    import asyncio
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        # Create input data for test execution
                        test_data = {
                            'content': test_details,
                            'test_suite': test_suite,
                            'environment': environment,
                            'test_files': test_files,
                            'options': {
                                'retry_failed': retry_failed,
                                'test_tags': test_tags,
                                'parallel_execution': parallel_execution,
                                'timeout': timeout
                            }
                        }
                        
                        result = loop.run_until_complete(qa_agent.execute_tests(test_data))
                        loop.close()
                        
                        # Display results
                        if result.get("status") == "success":
                            # Test execution summary
                            if 'execution_time' in result['data']:
                                st.success(f"Completed test execution in {result['data']['execution_time']}")
                            
                            # Check if this is a live test with detailed results or just an execution plan
                            if 'test_results' in result['data']:
                                # Display summary metrics
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Total Tests", result['data']['total_tests'])
                                with col2:
                                    st.metric("Passed", result['data']['passed_steps'])
                                with col3:
                                    st.metric("Failed", result['data']['failed_steps'])
                                with col4:
                                    success_rate = int((result['data']['passed_steps'] / result['data']['total_tests']) * 100)
                                    st.metric("Success Rate", f"{success_rate}%")
                                
                                # Display detailed test results
                                st.subheader("Test Results")
                                
                                # Convert test results to a DataFrame for better display
                                import pandas as pd
                                test_results_df = pd.DataFrame(result['data']['test_results'])
                                
                                # Display the dataframe with custom formatting
                                st.dataframe(test_results_df, use_container_width=True)
                                
                                # Show pass/fail summary with color coding
                                for idx, test in enumerate(result['data']['test_results']):
                                    status_color = "green" if test['status'] == "PASS" else "red"
                                    st.markdown(f"<span style='color:{status_color}'>{test['description']}: {test['status']}</span>", unsafe_allow_html=True)
                                
                                # Display failed test details if any
                                if result['data']['failed_steps'] > 0:
                                    st.subheader("Failed Tests")
                                    failed_tests = [t for t in result['data']['test_results'] if t['status'] == 'FAIL']
                                    for test in failed_tests:
                                        with st.expander(f"{test['description']} - FAILED"):
                                            st.error(test.get('error', 'No error details available'))
                                            st.text(f"Execution time: {test['execution_time']}")
                            
                            # Display execution plan
                            if 'execution_plan' in result['data']:
                                with st.expander("Test Execution Plan"):
                                    st.markdown(result['data']['execution_plan'])
                                    
                                # If we only have execution plan but no real test results, show info message
                                if 'test_results' not in result['data'] and 'recommendation' in result['data']:
                                    st.info(result['data']['recommendation'])
                        elif result.get("status") == "info":
                            st.info(result.get("message", "For real-time testing, please provide a URL"))
                            if 'data' in result and 'execution_plan' in result['data']:
                                with st.expander("Test Execution Plan"):
                                    st.markdown(result['data']['execution_plan'])
                                
                                if 'recommendation' in result['data']:
                                    st.info(result['data']['recommendation'])
                        else:
                            st.error(result.get("message", "An unknown error occurred during test execution"))
                    except Exception as e:
                        st.error(f"Error executing tests: {str(e)}")

        # Display test execution tips
        if not st.button("Run Tests", key="info_tests_button"):
            st.info("Prepare your test details and click 'Run Tests' to start test execution")

    @staticmethod
    def render_code_review():
        st.title("Code Review")
        
        # Code input
        uploaded_file = st.file_uploader("Upload Code for Review", 
                                        type=["py", "js", "java", "cpp", "cs", "html", "css", "ts", "jsx", "tsx"],
                                        key="review_file")
        
        # Analysis options
        options = st.multiselect(
            "Analysis Options",
            ["Test Coverage", "Security", "Performance", "Best Practices"],
            default=["Test Coverage", "Security", "Performance", "Best Practices"]
        )
        
        if uploaded_file and st.button("Review Code", key="review_code_button"):
            if not options:
                st.error("Please select at least one analysis option")
            else:
                with st.spinner("Analyzing code..."):
                    # Read file content
                    content = uploaded_file.getvalue().decode("utf-8")
                    
                    # Call the QA agent
                    qa_agent = st.session_state.qa_agent
                    import asyncio
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        # Create input data for review_code
                        review_data = {
                            'content': content,
                            'filename': uploaded_file.name,
                            'options': options
                        }
                        
                        result = loop.run_until_complete(qa_agent.review_code(review_data))
                        loop.close()
                        
                        if result.get("status") == "success":
                            st.success(f"Successfully reviewed {result['data']['filename']}")
                            st.markdown("### Code Review Results")
                            st.markdown(result['data']['review'])
                        else:
                            st.error(result.get("message", "An unknown error occurred"))
                    except Exception as e:
                        st.error(f"Error reviewing code: {str(e)}")
                        
        # Results section when no file is uploaded
        if not uploaded_file:
            st.info("Upload a code file to get review feedback")

    @staticmethod
    def render_impact_analysis():
        st.title("Impact Analysis")
        
        # Code changes input
        code_changes = st.text_area("Enter Code Changes", height=150, key="code_changes")
        
        # Analysis scope
        analysis_scope = st.multiselect(
            "Analysis Scope",
            ["Unit Tests", "Integration Tests", "UI Tests", "Data Validation"],
            default=["Unit Tests", "Integration Tests"]
        )
        
        if st.button("Analyze Impact", key="analyze_impact_button"):
            if not code_changes:
                st.error("Please enter code changes to analyze")
            elif not analysis_scope:
                st.error("Please select at least one analysis scope")
            else:
                with st.spinner("Analyzing impact..."):
                    # Call the QA agent
                    qa_agent = st.session_state.qa_agent
                    import asyncio
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        # Create input data for analyze_impact
                        impact_data = {
                            'content': code_changes,
                            'scope': analysis_scope
                        }
                        
                        result = loop.run_until_complete(qa_agent.analyze_impact(impact_data))
                        loop.close()
                        
                        if result.get("status") == "success":
                            st.success("Impact analysis completed")
                            st.markdown("### Impact Analysis Results")
                            st.markdown(result['data']['analysis'])
                            
                            # Display affected areas if any
                            if result['data'].get('affected_areas'):
                                st.subheader("Affected Areas")
                                st.write(result['data']['affected_areas'])
                        else:
                            st.error(result.get("message", "An unknown error occurred"))
                    except Exception as e:
                        st.error(f"Error analyzing impact: {str(e)}")
                
        # Show info message when no code changes are entered
        if not code_changes:
            st.info("Enter code changes to analyze their impact")

    @staticmethod
    def render_data_validation():
        st.title("Data Validation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Expected Data")
            expected_file = st.file_uploader("Upload Expected Data", key="expected_data")
            
        with col2:
            st.subheader("Actual Data")
            actual_file = st.file_uploader("Upload Actual Data", key="actual_data")
        
        if expected_file and actual_file and st.button("Compare Data", key="compare_data_button"):
            with st.spinner("Comparing data..."):
                # Read file contents
                expected_content = expected_file.getvalue().decode("utf-8")
                actual_content = actual_file.getvalue().decode("utf-8")
                
                # Call the QA agent
                qa_agent = st.session_state.qa_agent
                import asyncio
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Create input data for validate_data
                    expected_data = {
                        'content': expected_content,
                        'filename': expected_file.name
                    }
                    
                    actual_data = {
                        'content': actual_content,
                        'filename': actual_file.name
                    }
                    
                    result = loop.run_until_complete(qa_agent.validate_data(expected_data, actual_data))
                    loop.close()
                    
                    if result.get("status") == "success":
                        st.success("Data validation completed")
                        st.markdown("### Validation Results")
                        st.markdown(result['data']['comparison'])
                        
                        # Display discrepancies if any
                        if result['data'].get('discrepancies'):
                            st.subheader("Discrepancies")
                            st.dataframe(result['data']['discrepancies'])
                    else:
                        st.error(result.get("message", "An unknown error occurred"))
                except Exception as e:
                    st.error(f"Error validating data: {str(e)}")
        
        # Show info message when files aren't uploaded
        if not (expected_file and actual_file):
            st.info("Upload both expected and actual data files to compare")
