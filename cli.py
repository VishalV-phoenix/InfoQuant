# cli.py
# This is the CLI entry point for the InfoQuant application.
#
# Day 3 Change: Added support for multi-turn sessions using InMemoryRunner's
# session state, lightweight local tracking in SessionMemory, and a quiz skill
# that can be triggered after lessons or on-demand.

import asyncio
import os
import sys
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from orchestrator import orchestrator_workflow
from memory import session_memory
from security import security_check

from tutor import tutor_agent

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
    print("                Welcome to InfoQuant AI (Day 4)                ")
    print("=" * 60)
    print("Explain technical concepts to students with ease, track history,")
    print("and generate quizzes based on your session context.\n")
    print("Commands:")
    print("  - Type 'quiz' at any time to generate a quiz on your session history.")
    print("  - Type 'history' to view the local session history summary.")
    print("  - Type 'exit' or 'quit' to end the session.\n")

    # Initialize the InMemoryRunner with our orchestrator workflow
    runner = InMemoryRunner(agent=orchestrator_workflow, app_name="infoquant")
    # Initialize a separate runner for the Tutor Agent to run Quiz Mode directly
    tutor_runner = InMemoryRunner(agent=tutor_agent, app_name="infoquant_tutor")
    session_id = "infoquant_active_session"
    current_topic = None

    while True:
        try:
            user_input = input("\nEnter a topic or question: ").strip()
        except KeyboardInterrupt:
            print("\n[Info] Execution cancelled by user.")
            break

        if not user_input:
            continue

        # Day 4 Security Check
        is_safe, alert_message = security_check(user_input)
        if not is_safe:
            print("\n" + "=" * 60)
            print("                 SECURITY ALERT                                ")
            print("=" * 60)
            print(alert_message)
            print("=" * 60)
            continue


        lower_input = user_input.lower()
        if lower_input in ["exit", "quit"]:
            print("\nGoodbye!")
            break

        if lower_input == "history":
            print("\n=== Session History Summary ===")
            topics = session_memory.get_topics()
            if not topics:
                print("No topics discussed yet in this session.")
            else:
                print(f"Topics discussed: {', '.join(topics)}")
                print(session_memory.to_json())
            continue

        # Check if the user is asking for a quiz directly
        is_quiz_request = "quiz" in lower_input

        # If it's a quiz request, formulate a detailed prompt to instruct the Tutor Agent
        if is_quiz_request:
            active_topic = session_memory.current_topic
            last_explanation = session_memory.last_tutor_response
            
            if not active_topic:
                print("\n[Warning] No active learning topic found. Let's learn a topic first!")
                continue
            
            query = (
                f"You are now in Quiz Mode.\n"
                f"Generate a 5-question multiple-choice quiz about the active topic '{active_topic}' based on this explanation:\n\n"
                f"{last_explanation}\n\n"
                "Requirements:\n"
                "- 5 multiple-choice questions\n"
                "- 4 options per question (A, B, C, D)\n"
                "- Mark the correct answer clearly\n"
                "- Provide a short explanation for the correct answer\n"
                "Keep it beginner-friendly."
            )
            print(f"\n[Info] Generating quiz on '{active_topic}' using session memory...")
        else:
            # It's a normal topic or follow-up question
            current_topic = user_input
            query = user_input
            print(f"\n[Info] Processing request: '{query}'...")

        print("[Info] Running agents... (this may take a few moments)\n")

        try:
            if is_quiz_request:
                # Call the Tutor Agent runner directly (bypassing Research Agent)
                turn_session_id = f"infoquant_quiz_{len(session_memory.history) + 1}"
                result = await tutor_runner.run_debug(query, session_id=turn_session_id, quiet=True)
            else:
                # Run the workflow for explaining topics
                turn_session_id = f"infoquant_session_{len(session_memory.history) + 1}"
                result = await runner.run_debug(query, session_id=turn_session_id, quiet=True)
            
            # Extract only the final text response from the event list
            tutor_response = ""
            for event in result:
                if event.is_final_response() and event.content and event.content.parts:
                    tutor_response = "".join(part.text for part in event.content.parts if part.text)
                    break
            
            if is_quiz_request:
                print("=" * 60)
                print("                     STUDENT QUIZ                              ")
                print("=" * 60)
                print(tutor_response.strip())
                print("=" * 60)
            else:
                print("=" * 60)
                print("                 TUTOR'S EXPLANATION                           ")
                print("=" * 60)
                print(tutor_response.strip())
                print("=" * 60)
                
                # Save this turn in our local SessionMemory
                session_memory.add_turn(topic=current_topic, question=query, response=tutor_response)

                # Prompt the user if they want to generate a quiz now
                try:
                    quiz_prompt = input("\nWould you like to take a 5-question quiz on this topic? (y/n): ").strip().lower()
                    if quiz_prompt in ["y", "yes"]:
                        print(f"\n[Info] Generating quiz on '{current_topic}'...")
                        quiz_query = (
                            f"You are now in Quiz Mode.\n"
                            f"Generate a 5-question multiple-choice quiz about the active topic '{current_topic}' based on this explanation:\n\n"
                            f"{tutor_response}\n\n"
                            "Requirements:\n"
                            "- 5 multiple-choice questions\n"
                            "- 4 options per question (A, B, C, D)\n"
                            "- Mark the correct answer clearly\n"
                            "- Provide a short explanation for the correct answer\n"
                            "Keep it beginner-friendly."
                        )
                        quiz_session_id = f"infoquant_quiz_{len(session_memory.history) + 1}"
                        # Call the Tutor Agent runner directly (bypassing Research Agent)
                        quiz_result = await tutor_runner.run_debug(quiz_query, session_id=quiz_session_id, quiet=True)
                        quiz_response = ""
                        for event in quiz_result:
                            if event.is_final_response() and event.content and event.content.parts:
                                quiz_response = "".join(part.text for part in event.content.parts if part.text)
                                break
                        print("=" * 60)
                        print("                     STUDENT QUIZ                              ")
                        print("=" * 60)
                        print(quiz_response.strip())
                        print("=" * 60)
                except KeyboardInterrupt:
                    print("\n[Info] Quiz cancelled by user.")

        except Exception as e:
            print(f"\n[Error] An error occurred during execution: {e}")

if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Info] Execution cancelled by user.")
        sys.exit(0)
