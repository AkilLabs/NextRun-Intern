import streamlit as st
import os
import requests

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
                        import tempfile
                        import zipfile
                        import shutil
                        import os

                        with tempfile.TemporaryDirectory() as temp_dir:
                            for uploaded_file in uploaded_files:
                                if uploaded_file.name.endswith('.zip'):
                                    zip_path = os.path.join(temp_dir, uploaded_file.name)
                                    with open(zip_path, 'wb') as f:
                                        f.write(uploaded_file.getvalue())
                                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                        zip_ref.extractall(temp_dir)
                                else:
                                    file_path = os.path.join(temp_dir, uploaded_file.name)
                                    with open(file_path, 'wb') as f:
                                        f.write(uploaded_file.getvalue())

                            qa_agent = st.session_state.qa_agent
                            import asyncio
                            try:
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                result = loop.run_until_complete(qa_agent.analyze_code(temp_dir))
                                loop.close()

                                if result.get("status") == "success":
                                    st.success(f"Successfully analyzed {result['data']['total_files']} files")

                                    with st.expander("Files Analyzed"):
                                        for file in result['data']['files_analyzed']:
                                            st.write(f"- {file}")

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

        st.subheader("Generated Test Cases")

    @staticmethod
    def render_test_execution():
        st.title("Test Execution")

        test_suite = st.selectbox("Select Test Suite", ["Regression", "Integration", "UAT", "Smoke", "Performance"])
        environment = st.selectbox("Environment", ["Dev", "QA", "Staging", "Production"])

        input_method = st.radio(
            "Test Input Method",
            ["Generated Test Cases", "Test Script Files", "Manual Test Steps"]
        )

        test_details = ""
        test_files = []

        if input_method == "Generated Test Cases":
            test_details = st.text_area("Paste Generated Test Cases", height=150)
        elif input_method == "Test Script Files":
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
                    qa_agent = st.session_state.qa_agent
                    import asyncio
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

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

                        if result.get("status") == "success":
                            if 'execution_time' in result['data']:
                                st.success(f"Completed test execution in {result['data']['execution_time']}")

                            if 'test_results' in result['data']:
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

                                st.subheader("Test Results")
                                import pandas as pd
                                test_results_df = pd.DataFrame(result['data']['test_results'])
                                st.dataframe(test_results_df, use_container_width=True)

                                for idx, test in enumerate(result['data']['test_results']):
                                    status_color = "green" if test['status'] == "PASS" else "red"
                                    st.markdown(f"<span style='color:{status_color}'>{test['description']}: {test['status']}</span>", unsafe_allow_html=True)

                                if result['data']['failed_steps'] > 0:
                                    st.subheader("Failed Tests")
                                    failed_tests = [t for t in result['data']['test_results'] if t['status'] == 'FAIL']
                                    for test in failed_tests:
                                        with st.expander(f"{test['description']} - FAILED"):
                                            st.error(test.get('error', 'No error details available'))
                                            st.text(f"Execution time: {test['execution_time']}")

                            if 'execution_plan' in result['data']:
                                with st.expander("Test Execution Plan"):
                                    st.markdown(result['data']['execution_plan'])

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

        if not st.button("Run Tests", key="info_tests_button"):
            st.info("Prepare your test details and click 'Run Tests' to start test execution")

    @staticmethod
    def render_code_review():
        st.title("Code Review")

        uploaded_file = st.file_uploader("Upload Code for Review",
                                        type=["py", "js", "java", "cpp", "cs", "html", "css", "ts", "jsx", "tsx"],
                                        key="review_file")

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
                    content = uploaded_file.getvalue().decode("utf-8")

                    qa_agent = st.session_state.qa_agent
                    import asyncio
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

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

        if not uploaded_file:
            st.info("Upload a code file to get review feedback")

    @staticmethod
    def render_impact_analysis():
        st.title("Impact Analysis")

        code_changes = st.text_area("Enter Code Changes", height=150, key="code_changes")

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
                    qa_agent = st.session_state.qa_agent
                    import asyncio
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

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

                            if result['data'].get('affected_areas'):
                                st.subheader("Affected Areas")
                                st.write(result['data']['affected_areas'])
                        else:
                            st.error(result.get("message", "An unknown error occurred"))
                    except Exception as e:
                        st.error(f"Error analyzing impact: {str(e)}")

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
                expected_content = expected_file.getvalue().decode("utf-8")
                actual_content = actual_file.getvalue().decode("utf-8")

                qa_agent = st.session_state.qa_agent
                import asyncio
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

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

                        if result['data'].get('discrepancies'):
                            st.subheader("Discrepancies")
                            st.dataframe(result['data']['discrepancies'])
                    else:
                        st.error(result.get("message", "An unknown error occurred"))
                except Exception as e:
                    st.error(f"Error validating data: {str(e)}")

        if not (expected_file and actual_file):
            st.info("Upload both expected and actual data files to compare")

    @staticmethod
    def render_bug_triage():
        st.title("Bug Triage")

        col1, col2 = st.columns(2)

        with col1:
            bug_id = st.text_input("Bug ID", key="bug_id")
            bug_title = st.text_input("Bug Title", key="bug_title")
            severity = st.selectbox(
                "Severity",
                ["Critical", "High", "Medium", "Low", "Trivial"],
                index=2,
                key="severity"
            )

        with col2:
            status = st.selectbox(
                "Status",
                ["New", "In Progress", "Fixed", "Verified", "Closed", "Reopened"],
                index=0,
                key="status"
            )
            priority = st.selectbox(
                "Priority",
                ["P0 - Blocker", "P1 - Critical", "P2 - Important", "P3 - Normal", "P4 - Low"],
                index=2,
                key="priority"
            )
            assigned_to = st.text_input("Assigned To", key="assigned_to")

        bug_description = st.text_area("Bug Description", height=150, key="bug_description")

        st.subheader("Steps to Reproduce")
        steps_to_reproduce = st.text_area("Enter Steps to Reproduce", height=100, key="steps_to_reproduce")

        with st.expander("Environment Details"):
            col1, col2, col3 = st.columns(3)
            with col1:
                browser = st.selectbox("Browser", ["Chrome", "Firefox", "Safari", "Edge", "Other"], key="browser")
                os = st.selectbox("Operating System", ["Windows", "macOS", "Linux", "Android", "iOS", "Other"], key="os")
            with col2:
                browser_version = st.text_input("Browser Version", key="browser_version")
                os_version = st.text_input("OS Version", key="os_version")
            with col3:
                device = st.text_input("Device", key="device")
                screen_resolution = st.text_input("Screen Resolution", key="screen_resolution")

        st.subheader("Attachments")
        uploaded_files = st.file_uploader("Upload Screenshots or Evidence",
                                        accept_multiple_files=True,
                                        type=["png", "jpg", "jpeg", "gif", "mp4", "log", "txt"],
                                        key="attachments")

        with st.expander("Advanced Analysis"):
            similar_bugs = st.checkbox("Check for Similar Bugs", value=True, key="similar_bugs")
            root_cause = st.checkbox("AI-powered Root Cause Analysis", value=True, key="root_cause")
            severity_auto = st.checkbox("Auto-calculate Severity", value=True, key="severity_auto")
            impact_assessment = st.checkbox("Impact Assessment", value=True, key="impact_assessment")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Analyze Bug", key="analyze_bug_button"):
                if not bug_description:
                    st.error("Please provide a bug description")
                else:
                    with st.spinner("Analyzing bug..."):
                        qa_agent = st.session_state.qa_agent
                        import asyncio
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                            bug_data = {
                                'bug_id': bug_id,
                                'title': bug_title,
                                'description': bug_description,
                                'steps_to_reproduce': steps_to_reproduce,
                                'severity': severity,
                                'priority': priority,
                                'status': status,
                                'environment': {
                                    'browser': browser,
                                    'browser_version': browser_version,
                                    'os': os,
                                    'os_version': os_version,
                                    'device': device,
                                    'screen_resolution': screen_resolution
                                },
                                'analysis_options': {
                                    'check_similar_bugs': similar_bugs,
                                    'root_cause_analysis': root_cause,
                                    'auto_severity': severity_auto,
                                    'impact_assessment': impact_assessment
                                }
                            }

                            result = loop.run_until_complete(qa_agent.triage_bug(bug_data))
                            loop.close()

                            if result.get("status") == "success":
                                st.success("Bug analysis completed")

                                st.markdown("### Bug Analysis Results")
                                st.markdown(result['data']['analysis'])

                                if 'recommendations' in result['data']:
                                    st.subheader("Recommendations")
                                    st.markdown(result['data']['recommendations'])

                                if similar_bugs and 'similar_bugs' in result['data']:
                                    with st.expander("Similar Bugs"):
                                        for bug in result['data']['similar_bugs']:
                                            st.markdown(f"**{bug['id']} - {bug['title']}**")
                                            st.markdown(f"*Similarity Score: {bug['similarity_score']}%*")
                                            st.markdown(bug['description'])
                                            st.divider()

                                if root_cause and 'root_cause' in result['data']:
                                    with st.expander("Root Cause Analysis"):
                                        st.markdown(result['data']['root_cause'])

                                if impact_assessment and 'impact' in result['data']:
                                    with st.expander("Impact Assessment"):
                                        st.markdown(result['data']['impact'])
                            else:
                                st.error(result.get("message", "An unknown error occurred"))
                        except Exception as e:
                            st.error(f"Error analyzing bug: {str(e)}")

        with col2:
            if st.button("Save Bug Report", key="save_bug_report"):
                if not bug_title or not bug_description:
                    st.error("Please provide at least a bug title and description")
                else:
                    st.success(f"Bug report '{bug_title}' saved successfully!")

            if st.button("Raise Issue on GitHub", key="raise_github_issue"):
                if not bug_title or not bug_description:
                    st.error("Please provide at least a bug title and description")
                else:
                    github_token = "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"
                    repo_owner = "AkilLabs"
                    repo_name = "NextRun-Intern"

                    if not github_token:
                        st.error("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
                    else:
                        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
                        headers = {
                            "Authorization": f"token {github_token}",
                            "Accept": "application/vnd.github.v3+json"
                        }
                        issue_data = {
                            "title": bug_title,
                            "body": f"## Description\n{bug_description}\n\n## Steps to Reproduce\n{steps_to_reproduce}\n\n## Environment\n- Browser: {browser} {browser_version}\n- OS: {os} {os_version}\n- Device: {device}\n- Screen Resolution: {screen_resolution}"
                        }

                        response = requests.post(url, headers=headers, json=issue_data)

                        if response.status_code == 201:
                            st.success(f"Issue '{bug_title}' raised successfully on GitHub!")
                        else:
                            st.error(f"Failed to raise issue on GitHub: {response.content}")

        if not bug_description:
            st.info("Enter bug details and click 'Analyze Bug' to get AI-powered triage assistance")
