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
            return await self.generate_test_cases(task)
        elif "analyze" in task_lower and "code" in task_lower:
            return await self.analyze_code(task)
        elif "workflow" in task_lower:
            return await self.introspect_workflow({"task": task})
        elif "validate" in task_lower and "data" in task_lower:
            return await self.validate_data({}, {})
        elif "impact" in task_lower:
            return await self.analyze_impact({"task": task})
        else:
            return {"error": "Task type not recognized. Please specify a task related to: test cases, code analysis, workflow, data validation, or impact analysis."}

    async def generate_test_cases(self, jira_story: str) -> List[Dict]:
        """Generate test cases from Jira story"""
        prompt = f"""
        Given this Jira story, generate comprehensive test cases:
        {jira_story}
        
        Include:
        - Functional tests
        - Edge cases
        - Data validation tests
        """
        response = await self.llm.agenerate([prompt])
        # Process and structure the response
        return self._parse_test_cases(response.generations[0].text)

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
            response = await self.llm.agenerate([prompt])
            test_cases = response.generations[0].text

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
        pass

    async def validate_data(self, expected_data: Dict, actual_data: Dict) -> Dict:
        """Compare expected vs actual data"""
        # Implementation for data validation
        pass

    async def analyze_impact(self, code_changes: Dict) -> Dict:
        """Analyze impact of code changes on tests"""
        # Implementation for impact analysis
        pass

    def _parse_test_cases(self, llm_response: str) -> List[Dict]:
        """Parse LLM response into structured test cases"""
        # Implementation for parsing test cases
        pass
