# test_tools.py — run this FIRST before touching the API
# python test_tools.py

import sys
import os

# Add backend to path so we can import pc_control
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

try:
    from pc_control import open_app, open_url, get_system_stats
    import time

    print("--- ANAY TOOL TESTER ---")
    
    print("\n1. Testing open_app('brave')...")
    result = open_app("brave")
    print(f"Result: {result}")

    time.sleep(2)

    print("\n2. Testing open_url('https://youtube.com')...")
    result = open_url("https://youtube.com")
    print(f"Result: {result}")

    time.sleep(1)

    print("\n3. Testing get_system_stats()...")
    stats = get_system_stats()
    print(f"CPU: {stats.get('cpu_percent')}%")
    print(f"RAM: {stats.get('ram_percent')}%")

    print("\n--- TEST DONE ---")
    print("If Brave and YouTube opened, pc_control.py is working perfectly.")
    print("Now you can start the backend: npm run dev")
    
except ImportError as e:
    print(f"Import Error: {e}")
    print("Make sure you are running this from the project root and requirements are installed.")
except Exception as e:
    print(f"Error during test: {e}")
