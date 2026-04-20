
import asyncio
import logging
import os
from dotenv import load_dotenv

# Setup minimal logging
logging.basicConfig(level=logging.INFO)

# Load env
load_dotenv()

# Import
from automation.task_planner import TaskPlanner
from groq_llm import GroqLLM

async def test():
    print("--- Testing Planner ---")
    
    # Init LLM
    try:
        llm = GroqLLM()
        print(f"LLM Init: {llm.model_name}")
    except Exception as e:
        print(f"LLM Fail: {e}")
        return

    # Init Planner
    planner = TaskPlanner(llm_client=llm)
    
    # Test Prompt
    prompt = "Create a file in d drive as python.py and write two sum code in it and then open it in vs code"
    
    print(f"\nUser Prompt: {prompt}")
    
    # Run
    # We call _generate_plan directly to see output
    ctx = planner.ctx.get_context()
    print(f"\nContext: {ctx}")
    
    print("\n--- Generating Plan ---")
    plan = await planner._generate_plan(prompt, ctx)
    
    print("\n--- Result ---")
    print(plan)

if __name__ == "__main__":
    asyncio.run(test())
