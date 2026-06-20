# cli.py
# This is the CLI entry point for the InfoQuant application.
# It handles loading environment variables, taking user input for a topic,
# running the orchestrator workflow via InMemoryRunner, and displaying the results.

import asyncio
import os
import sys
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from orchestrator import orchestrator_workflow

# Load environment variables (such as GEMINI_API_KEY) from .env file
load_dotenv()

async def main():
    # Verify that the Gemini API Key is available
    if not os.environ.get("GEMINI_API_KEY"):
        print("\n[Error] GEMINI_API_KEY environment variable is not set.")
        print("Please set it in your environment or create a '.env' file in this directory.")
        print("Example: GEMINI_API_KEY=AIzaSy...")
        sys.exit(1)

    print("=" * 60)
    print("                Welcome to InfoQuant AI (Day 1)                ")
    print("=" * 60)
    print("Explain technical concepts to students with ease.\n")

    topic = input("Enter a topic you want to research and learn: ").strip()
    if not topic:
        print("\nError: Topic cannot be empty.")
        sys.exit(1)

    print(f"\n[Info] Starting research and tutoring workflow for: '{topic}'...")
    print("[Info] Running agents... (this may take a few moments)\n")

    # Initialize the InMemoryRunner with our orchestrator workflow
    runner = InMemoryRunner(agent=orchestrator_workflow, app_name="infoquant")

    try:
        # Run the workflow
        result = await runner.run_debug(topic, quiet=True)
        
        # Extract only the final text response from the event list
        tutor_response = ""
        for event in result:
            if event.is_final_response() and event.content and event.content.parts:
                tutor_response = "".join(part.text for part in event.content.parts if part.text)
                break
        
        print("\nTUTOR'S EXPLANATION\n")
        print(tutor_response.strip())

    except Exception as e:
        print(f"\n[Error] An error occurred during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Info] Execution cancelled by user.")
        sys.exit(0)
