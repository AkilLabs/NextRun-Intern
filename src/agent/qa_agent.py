from typing import Dict, List, Optional
from src.agent.base_agent import BaseAgent
from langchain_openai import ChatOpenAI
import os

class QAEngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "QAEngineer-X"
        self.description = "AI-powered QA automation agent for comprehensive testing"
        self.capabilities = [
            "Test Case Generation",
            "Code Analysis",
            "Workflow Introspection",
            "Data Validation",
            "Impact Analysis"
        ]
        self.llm = None

    def initialize_llm(self, api_key: str) -> None:
        """Initialize the LLM with the provided API key"""
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.0,
            api_key=api_key
        )

    async def execute_task(self, task: str) -> Dict:
        """Execute a given task using the appropriate capability"""
        task_lower = task.lower()
        
        if "test case" in task_lower or "test suite" in task_lower:
            return await self.generate_test_cases({"content": task})
        elif "analyze" in task_lower and "code" in task_lower:
            return await self.analyze_code(task)
        elif "review" in task_lower and "code" in task_lower:
            return await self.review_code({"content": task})
        elif "workflow" in task_lower:
            return await self.introspect_workflow({"task": task})
        elif "validate" in task_lower and "data" in task_lower:
            return await self.validate_data({}, {})
        elif "impact" in task_lower:
            return await self.analyze_impact({"task": task})
        else:
            return {"error": "Task type not recognized. Please specify a task related to: test cases, code analysis, code review, workflow, data validation, or impact analysis."}

    async def generate_test_cases(self, input_data: Dict) -> Dict:
        """Generate test cases from Jira story or description"""
        # Check if input_data is a string (backward compatibility) or a dict with 'content' key
        if isinstance(input_data, dict):
            content = input_data.get('content', '')
        else:
            content = input_data  # Assume it's a string
            
        prompt = f"""
        Given this story or description, generate comprehensive test cases:
        {content}
        
        Include:
        - Functional tests
        - Edge cases
        - Data validation tests
        """
        
        if not self.llm:
            return {
                "status": "error",
                "message": "LLM not initialized. Please set your OpenAI API key in Settings."
            }
            
        try:
            from langchain_core.messages import HumanMessage
            messages = [[HumanMessage(content=prompt)]]
            response = await self.llm.agenerate(messages)
            test_cases = response.generations[0][0].text
            
            # Return structured response
            return {
                "status": "success",
                "data": {
                    "test_cases": test_cases
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating test cases: {str(e)}"
            }

    async def analyze_code(self, code_path: str) -> Dict:
        """Analyze code for test coverage and paths"""
        if not self.llm:
            return {"error": "LLM not initialized. Please set your OpenAI API key in Settings."}

        try:
            # Get list of files in the directory
            files = []
            for root, _, filenames in os.walk(code_path):
                for filename in filenames:
                    if filename.endswith(('.py', '.js', '.java', '.cpp')):
                        file_path = os.path.join(root, filename)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            files.append({
                                'name': os.path.relpath(file_path, code_path),
                                'content': content
                            })

            # Prepare prompt for test case generation
            prompt = f"""
            I have a codebase with the following files:
            {', '.join(f['name'] for f in files)}

            For each file, analyze the code and generate appropriate test cases.
            Focus on:
            1. Function/method testing
            2. Edge cases
            3. Input validation
            4. Error handling
            5. Integration points

            For each test case, provide:
            - Test name
            - Description
            - Prerequisites
            - Test steps
            - Expected results
            - Priority (High/Medium/Low)

            Here are the file contents:
            """

            for file in files:
                prompt += f"""
                File: {file['name']}
                ```
                {file['content']}
                ```
                """

            # Get response from LLM
            from langchain_core.messages import HumanMessage
            messages = [[HumanMessage(content=prompt)]]
            response = await self.llm.agenerate(messages)
            test_cases = response.generations[0][0].text

            # Structure the response
            return {
                "status": "success",
                "data": {
                    "test_cases": test_cases,
                    "files_analyzed": [f['name'] for f in files],
                    "total_files": len(files)
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error analyzing code: {str(e)}"
            }

    async def introspect_workflow(self, workflow_data: Dict) -> Dict:
        """Analyze workflow paths and conditions"""
        # Implementation for workflow analysis
        return {
            "status": "not_implemented",
            "message": "Workflow introspection is not yet implemented"
        }

    async def validate_data(self, expected_data: Dict, actual_data: Dict) -> Dict:
        """Compare expected vs actual data"""
        if not self.llm:
            return {"status": "error", "message": "LLM not initialized. Please set your OpenAI API key in Settings."}
        
        try:
            # Extract content and filenames
            expected_content = expected_data.get('content', '')
            expected_filename = expected_data.get('filename', 'expected_data')
            actual_content = actual_data.get('content', '')
            actual_filename = actual_data.get('filename', 'actual_data')
            
            # Prepare prompt for data comparison
            prompt = f"""
            I need to compare expected data with actual data.
            
            Expected data filename: {expected_filename}
            ```
            {expected_content}
            ```
            
            Actual data filename: {actual_filename}
            ```
            {actual_content}
            ```
            
            Perform a detailed comparison between the expected and actual data. Identify:
            1. Missing data in the actual results
            2. Extra data in the actual results
            3. Differences in values between expected and actual
            4. Format inconsistencies
            
            Provide a structured analysis of the differences and a summary of the comparison results.
            If the data is in JSON or tabular format, present the discrepancies in a structured way.
            """
            
            # Get response from LLM
            from langchain_core.messages import HumanMessage
            messages = [[HumanMessage(content=prompt)]]
            response = await self.llm.agenerate(messages)
            comparison_result = response.generations[0][0].text
            
            # Simple discrepancy detection logic based on file types
            discrepancies = []
            # If we're dealing with structured data, we could extract key differences here
            # This is a simple implementation, but you could extend it to handle CSV, JSON, XML, etc.
            
            if expected_filename.endswith('.json') and actual_filename.endswith('.json'):
                import json
                try:
                    expected_json = json.loads(expected_content)
                    actual_json = json.loads(actual_content)
                    
                    # Find discrepancies in JSON data
                    if isinstance(expected_json, dict) and isinstance(actual_json, dict):
                        # Compare keys
                        expected_keys = set(expected_json.keys())
                        actual_keys = set(actual_json.keys())
                        
                        for key in expected_keys.intersection(actual_keys):
                            if expected_json[key] != actual_json[key]:
                                discrepancies.append({
                                    "field": key,
                                    "expected": str(expected_json[key]),
                                    "actual": str(actual_json[key])
                                })
                        
                        for key in expected_keys - actual_keys:
                            discrepancies.append({
                                "field": key,
                                "expected": str(expected_json[key]),
                                "actual": "MISSING"
                            })
                        
                        for key in actual_keys - expected_keys:
                            discrepancies.append({
                                "field": key,
                                "expected": "MISSING",
                                "actual": str(actual_json[key])
                            })
                except:
                    # If JSON parsing fails, continue with the general analysis
                    pass
            
            # Structure the response
            return {
                "status": "success",
                "data": {
                    "comparison": comparison_result,
                    "discrepancies": discrepancies,
                    "expected_filename": expected_filename,
                    "actual_filename": actual_filename
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error validating data: {str(e)}"
            }

    async def analyze_impact(self, code_changes: Dict) -> Dict:
        """Analyze impact of code changes on tests and other components"""
        if not self.llm:
            return {
                "status": "error",
                "message": "LLM not initialized. Please set your OpenAI API key in Settings."
            }
            
        try:
            content = code_changes.get('content', '')
            scope = code_changes.get('scope', ['Unit Tests', 'Integration Tests'])
            
            scope_str = ", ".join(scope)
            
            prompt = f"""
            Analyze the impact of the following code changes:
            ```
            {content}
            ```
            
            Focus on the impact to the following areas: {scope_str}
            
            Your analysis should include:
            1. A summary of the changes
            2. Potential affected components or test areas
            3. Risk assessment (High/Medium/Low)
            4. Recommended testing approach
            5. Any potential regression issues
            
            Format the response in markdown.
            """
            
            from langchain_core.messages import HumanMessage
            from typing import List, cast
            from langchain_core.messages import BaseMessage
            
            # Create the messages and cast to the expected type
            message = HumanMessage(content=prompt)
            messages = cast(List[List[BaseMessage]], [[message]])
            
            response = await self.llm.agenerate(messages)
            analysis = response.generations[0][0].text
            
            # Process the analysis to extract affected areas
            affected_areas = []
            for area in scope:
                if area.lower() in analysis.lower():
                    affected_areas.append(area)
            
            # Return structured response
            return {
                "status": "success",
                "data": {
                    "analysis": analysis,
                    "affected_areas": affected_areas
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error analyzing impact: {str(e)}"
            }

    async def code_review(self, code_content: Dict) -> Dict:
        """Perform code review and identify improvements and issues"""
        if not self.llm:
            return {"status": "error", "message": "LLM not initialized. Please set your OpenAI API key in Settings."}
            
        try:
            content = code_content.get('content', '')
            filename = code_content.get('filename', 'Unknown file')
            file_ext = filename.split('.')[-1] if '.' in filename else ''
            
            prompt = f"""
            Please perform a comprehensive code review on the following {file_ext} code:
            ```
            {content}
            ```
            
            Analyze the code for:
            1. Code quality issues
            2. Potential bugs or errors
            3. Performance concerns
            4. Security vulnerabilities
            5. Best practices violations
            6. Test coverage gaps
            
            For each issue found, provide:
            - Issue description
            - Severity (Critical, High, Medium, Low)
            - Recommended fix with example code if applicable
            
            At the end, provide an overall assessment of the code quality.
            """
            
            from langchain_core.messages import HumanMessage
            messages = [[HumanMessage(content=prompt)]]
            response = await self.llm.agenerate(messages)
            review_result = response.generations[0][0].text
            
            return {
                "status": "success",
                "data": {
                    "review": review_result,
                    "filename": filename
                }
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Error performing code review: {str(e)}"
            }
    
    def _parse_test_cases(self, llm_response: str) -> List[Dict]:
        """Parse LLM response into structured test cases"""
        # For now, return an empty list as this is not implemented
        return []

    async def review_code(self, code_file: Dict) -> Dict:
        """Review code for quality, bugs, and improvements"""
        if not self.llm:
            return {"status": "error", "message": "LLM not initialized. Please set your OpenAI API key in Settings."}
        
        try:
            content = code_file.get('content', '')
            filename = code_file.get('filename', 'Unknown file')
            file_ext = filename.split('.')[-1] if '.' in filename else ''
            
            prompt = f"""
            Please perform a comprehensive code review on the following {file_ext} code:
            ```
            {content}
            ```
            
            Analyze the code for:
            1. Code quality issues
            2. Potential bugs or errors
            3. Performance concerns
            4. Security vulnerabilities
            5. Best practices violations
            6. Test coverage gaps
            
            For each issue found, provide:
            - Issue description
            - Severity (Critical, High, Medium, Low)
            - Recommended fix with example code if applicable
            
            At the end, provide an overall assessment of the code quality.
            """
            
            from langchain_core.messages import HumanMessage
            messages = [[HumanMessage(content=prompt)]]
            response = await self.llm.agenerate(messages)
            review_result = response.generations[0][0].text
            
            # Return structured response
            return {
                "status": "success",
                "data": {
                    "review": review_result,
                    "filename": filename
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error reviewing code: {str(e)}"
            }
