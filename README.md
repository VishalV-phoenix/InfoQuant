# InfoQuant - Day 1 Implementation

InfoQuant is a multi-agent research and learning assistant that helps users understand technical topics. This Day 1 implementation contains the foundational multi-agent workflow powered by the Google Agent Development Kit (ADK).

## Purpose of Generated Files

1. **`researcher.py`**: Defines the `Research Agent`, responsible for gathering analytical and comprehensive details about the requested topic using model knowledge.
2. **`tutor.py`**: Defines the `Tutor Agent`, which translates the detailed research findings into beginner-friendly explanations suitable for students.
3. **`orchestrator.py`**: Establishes the `Orchestrator Workflow` which connects the `Research Agent` and `Tutor Agent` in a sequential multi-agent execution pipeline (`START` -> `Research Agent` -> `Tutor Agent`).
4. **`cli.py`**: The command-line interface entry point. It loads configuration, prompts the user for a topic, triggers the orchestration workflow via `InMemoryRunner`, and outputs the tutor's friendly explanation.
5. **`requirements.txt`**: Specifies the dependencies required for the project (`google-adk` and `python-dotenv`).

---

## Setup Instructions

### Prerequisites

* Python 3.10 or higher
* A Gemini API key (from Google AI Studio)

### Installation

1. Clone or navigate to the workspace directory.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the root of the project directory and add your Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## Running the Application

To run the CLI application and query a topic:
```bash
python cli.py
```
Follow the interactive prompt, enter a topic (e.g. `Quantum Computing` or `Neural Networks`), and watch the Orchestrator delegate research to the Research Agent and format it into a friendly lesson via the Tutor Agent.
