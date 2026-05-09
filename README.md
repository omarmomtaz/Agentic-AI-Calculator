# Agentic AI Calculator

A simple command-line AI agent that uses a local LLM (via Ollama) to answer math questions by automatically calling a calculator tool when needed.

## Features

- Connects to any Ollama model (llama3.2, mistral, phi3, etc.)
- Agentic loop: the AI decides when to use the calculator tool
- Handles multiple calculation steps per query
- Comes with built‑in example questions
- Fully offline (once the model is pulled)

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com/) installed and running
- A pulled model (e.g., `ollama pull llama3.2`)

## Installation

1. Clone the repository or download `main.py`.
2. Install the only dependency:
   ```bash
   pip install requests
