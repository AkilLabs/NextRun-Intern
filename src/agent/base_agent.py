from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self):
        self.name = ""
        self.description = ""
        self.capabilities: List[str] = []
        self.llm: Optional[BaseChatModel] = None
        self.state: Dict = {}

    @abstractmethod
    async def execute_task(self, task: str) -> Dict:
        """Execute a given task"""
        pass

    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.capabilities

    def get_state(self) -> Dict:
        """Get current agent state"""
        return self.state

    def update_state(self, new_state: Dict) -> None:
        """Update agent state"""
        self.state.update(new_state)
