# orchestrator.py
# This module defines the Orchestrator for the InfoQuant system using Google ADK.
# The Orchestrator is set up as a sequential Workflow that manages the flow:
# START -> Research Agent -> Tutor Agent.

from google.adk import Workflow
from researcher import research_agent
from tutor import tutor_agent

# Define the multi-agent workflow
orchestrator_workflow = Workflow(
    name="orchestrator",
    description="Manages the sequential execution of research and educational transformation.",
    edges=[
        ("START", research_agent, tutor_agent)
    ]
)
