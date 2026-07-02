# app.py
# This is the FastAPI web server backend for the InfoQuant application.
#
# Day 5 Change: Implemented a Python web server exposing InfoQuant endpoints
# and serving the frontend static web assets. Endpoints reuse existing logic:
#   - security_check (from security.py) to validate inputs
#   - SessionMemory (from memory.py) to manage session turns
#   - InMemoryRunner + Orchestrator (from orchestrator.py) to run agent workflow

from dotenv import load_dotenv
load_dotenv()  # Load environment variables first before importing any agents

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google.adk.runners import InMemoryRunner
from orchestrator import orchestrator_workflow
from memory import session_memory
from security import security_check


app = FastAPI(
    title="InfoQuant AI Backend",
    description="FastAPI REST API layer for the InfoQuant Multi-Agent Learning Assistant"
)

# Mount the static files directory to serve the frontend web page
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Schema for the incoming explanation requests
class ExplainRequest(BaseModel):
    query: str

# Schema for the incoming quiz requests
class QuizRequest(BaseModel):
    topic: str | None = None

from tutor import tutor_agent

# Initialize the InMemoryRunner with our orchestrator workflow
runner = InMemoryRunner(agent=orchestrator_workflow, app_name="infoquant_web")
# Initialize a separate runner for the Tutor Agent to run Quiz Mode directly
tutor_runner = InMemoryRunner(agent=tutor_agent, app_name="infoquant_tutor")

@app.get("/")
def read_root():
    """Serves the main frontend page."""
    return FileResponse("static/index.html")

@app.post("/explain")
async def explain(req: ExplainRequest):
    """Processes user queries by applying security check, context enrichment,

    invoking the ADK Orchestrator workflow, and saving results to memory.
    """
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    # 1. Apply Security Guardrails
    is_safe, alert_message = security_check(query)
    if not is_safe:
        return {"safe": False, "response": alert_message}
        
    # 2. Enrich context with conversation history to resolve follow-ups
    prompt = ""
    if len(session_memory.history) > 0:
        prompt += "Previous topics discussed in this session:\n"
        for turn in session_memory.history:
            prompt += f"- Topic: {turn['topic']} (Question: {turn['question']})\n"
        prompt += f"\nAnswer the following request in context of the previous topics if relevant: {query}"
    else:
        prompt = query

    try:
        # Use a turn-specific session ID to prevent closed session/TaskGroup reuse issues in ADK
        turn_session_id = f"infoquant_web_session_{len(session_memory.history) + 1}"
        events = await runner.run_debug(prompt, session_id=turn_session_id, quiet=True)
        
        tutor_response = ""
        research_notes = ""
        for event in events:
            if hasattr(event, "node_info") and event.node_info:
                if event.node_info.path == "research_agent" and event.content and event.content.parts:
                    notes_part = "".join(part.text for part in event.content.parts if part.text)
                    if notes_part:
                        research_notes += notes_part
            if event.is_final_response() and event.content and event.content.parts:
                tutor_response = "".join(part.text for part in event.content.parts if part.text)
                break
                
        if not tutor_response:
            raise HTTPException(status_code=500, detail="Tutor Agent did not produce an explanation.")
            
        # Save this turn to the local SessionMemory
        session_memory.add_turn(topic=query, question=query, response=tutor_response)
        if research_notes:
            session_memory.last_research_notes = research_notes
        
        return {"safe": True, "response": tutor_response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

@app.post("/quiz")
async def generate_quiz(req: QuizRequest):
    """Generates a 5-question multiple choice quiz on the active topic using Tutor Agent directly."""
    active_topic = session_memory.current_topic
    last_explanation = session_memory.last_tutor_response
    
    if not active_topic:
        raise HTTPException(
            status_code=400,
            detail="No active learning topic found. Please learn a topic first before generating a quiz!"
        )
        
    # If the quiz is already generated for the current topic, return the cached version immediately
    if session_memory.last_quiz:
        return {"response": session_memory.last_quiz}
        
    # Instruct the Tutor Agent to run in Quiz Mode for the active topic
    quiz_query = (
        f"You are now in Quiz Mode.\n"
        f"Generate a 5-question multiple-choice quiz about the active topic '{active_topic}' based on this explanation:\n\n"
        f"{last_explanation}\n\n"
        "Requirements:\n"
        "- 5 multiple-choice questions\n"
        "- 4 options per question (A, B, C, D)\n"
        "- Clear separating horizontal line (--------------------------------)\n"
        "- Answer Key section at the bottom containing correct answers and short explanations\n"
        "Keep it beginner-friendly."
    )
    
    try:
        turn_session_id = f"infoquant_web_quiz_{len(session_memory.history) + 1}"
        # Call the Tutor Agent runner directly, bypassing the Research Agent entirely
        events = await tutor_runner.run_debug(quiz_query, session_id=turn_session_id, quiet=True)
        
        quiz_response = ""
        for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                quiz_response = "".join(part.text for part in event.content.parts if part.text)
                break
                
        if not quiz_response:
            raise HTTPException(status_code=500, detail="Tutor Agent did not produce a quiz.")
            
        # Store in session memory
        session_memory.last_quiz = quiz_response
        return {"response": quiz_response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

@app.get("/history")
def get_history():
    """Retrieves session history and discussed topics."""
    return {"history": session_memory.history, "topics": session_memory.get_topics()}

@app.post("/history/clear")
def clear_history():
    """Clears the session history."""
    session_memory.clear()
    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    # Start the FastAPI server using Uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
