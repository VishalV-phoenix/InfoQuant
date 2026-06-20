# researcher.py
# This module defines the Research Agent for the InfoQuant system using Google ADK.
# The Research Agent is responsible for gathering detailed information about a given topic
# using only the underlying LLM's model knowledge for Day 1.

from google.adk import Agent

# Define the Research Agent
research_agent = Agent(
    name="research_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a Research Agent for InfoQuant. "
        "Your task is to gather information on the requested topic and return ONLY concise, structured notes. "
        "Do not exceed a maximum of 300 words. "
        "Ensure your notes include:\n"
        "- What it is\n"
        "- Key concepts\n"
        "- Real-world applications\n"
        "Use model knowledge only."
    )
)
