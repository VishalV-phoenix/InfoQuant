# security.py
# This module implements lightweight security guardrails for InfoQuant.
# It protects the system from prompt injection and system prompt exposure attempts
# before requests reach the agents, returning a friendly explanation if blocked.

import re
from typing import Tuple, List

# A list of common prompt injection patterns and instructions to detect case-insensitively
BLOCKED_PHRASES: List[str] = [
    "ignore previous instructions",
    "ignore all instructions",
    "ignore the instructions",
    "reveal your system prompt",
    "reveal system prompt",
    "show your system prompt",
    "show system prompt",
    "show hidden instructions",
    "reveal hidden instructions",
    "forget your role",
    "forget your instruction",
    "developer instructions",
    "you are now a",
    "start acting as",
    "bypass constraints"
]

def security_check(user_input: str) -> Tuple[bool, str]:
    """Inspects user input for prompt injection and system prompt leakage attempts.
    
    This function performs simple, educational, and high-performance pattern matching 
    against a configurable list of blocked phrases. It intercepts malicious requests
    before they reach the Orchestrator to save tokens and prevent agent misalignment.

    Args:
        user_input: The raw query string input from the user.
        
    Returns:
        A tuple of (is_safe, message).
        If is_safe is False, message explains why the request was blocked.
    """
    normalized_input = user_input.lower().strip()
    
    # Case-insensitive checks for prompt injection phrases
    for phrase in BLOCKED_PHRASES:
        if phrase in normalized_input:
            # We return a friendly educational explanation for the block
            return False, (
                f"Security Check: Your request was blocked because it contains a pattern "
                f"associated with prompt manipulation ('{phrase}').\n"
                "To protect the agent's behavior and constraints, requests that attempt to "
                "override instructions, reveal hidden prompts, or force the agent to forget its role "
                "are intercepted. Please enter a valid educational topic."
            )
            
    return True, ""
