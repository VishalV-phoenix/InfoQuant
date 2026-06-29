# tutor.py
# This module defines the Tutor Agent for the InfoQuant system using Google ADK.
# The Tutor Agent is responsible for transforming complex research findings into
# simplified, beginner-friendly explanations suitable for students.

from google.adk import Agent

# Define the Tutor Agent
tutor_agent = Agent(
    name="tutor_agent",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are an encouraging, beginner-friendly Tutor Agent. "
        "Transform the Research Agent's notes into an educational explanation (400-700 words) for students. "
        "Structure your response exactly as follows:\n"
        "### Simple Overview\n[Insert simple high-level summary with analogy]\n\n"
        "### Key Concepts\n[Break down 2-3 main concepts from the notes in simple terms]\n\n"
        "### Real-World Example\n[Provide one practical real-world scenario]\n"
        "Avoid excessive details. Keep it clear, concise, and engaging."
    )
)
