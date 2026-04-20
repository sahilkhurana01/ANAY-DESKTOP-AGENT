"""
Command Router Module
Handles system commands and task execution
"""
import os
import logging
import subprocess
import platform
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class CommandRouter:
    """Routes user intents to system commands or LLM responses."""
    
    def __init__(self, llm_client=None):
        """Initialize command router with automation planner."""
        self.system = platform.system()
        logger.info(f"Command router initialized (OS: {self.system})")
        
        # Initialize the new TaskPlanner
        try:
            from automation.task_planner import TaskPlanner
            self.planner = TaskPlanner(llm_client)
            self.has_automation = True
        except ImportError as e:
            logger.error(f"Failed to load automation modules: {e}")
            self.has_automation = False
        
        # Keywords that strongly suggest a command task
        self.task_keywords = [
            'open', 'launch', 'start', 'close', 'shut down', 'restart',
            'type', 'click', 'scroll', 'press',
            'search', 'browse', 'go to',
            'create file', 'delete', 'read', 'write', 'folder'
        ]
    
            'create file', 'delete', 'read', 'write', 'folder'
        ]
    
    async def route(self, user_input: str) -> Tuple[bool, Optional[str]]:
        """
        Determine if input is a command and execute it via TaskPlanner.
        
        Args:
            user_input: User's input text
            
        Returns:
            Tuple of (is_command, response_message)
        """
        try:
            if not self.has_automation:
                return False, "Automation modules are not active."

            user_input_lower = user_input.lower().strip()
            
            # Heuristic check: is this a command?
            is_likely_command = any(user_input_lower.startswith(k) for k in self.task_keywords)
            
            if is_likely_command:
                logger.info(f"Routing to TaskPlanner: {user_input}")
                
                # Check for simple commands (synchronous)
                if self.planner._is_simple_command(user_input):
                    result = self.planner._execute_simple(user_input)
                    return True, result
                
                # Execute complex plan (async)
                result = await self.planner.execute_plan(user_input)
                return True, result

            return False, None
            
        except Exception as e:
            logger.error(f"Command routing error: {e}")
            return True, f"Command execution failed: {str(e)}"


if __name__ == "__main__":
    # Test command router
    logging.basicConfig(level=logging.INFO)
    
    router = CommandRouter()
    
    test_inputs = [
        "Open Chrome",
        "Launch calculator",
        "Open Downloads folder",
        "Tell me a joke",
        "Shutdown computer",
    ]
    
    for test_input in test_inputs:
        is_command, response = router.route(test_input)
        print(f"Input: {test_input}")
        print(f"Is Command: {is_command}")
        print(f"Response: {response}\n")
