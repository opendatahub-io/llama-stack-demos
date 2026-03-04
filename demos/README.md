# Llama Stack Demos

This directory contains demo examples for getting started with Llama Stack.

## Setup

First, install [`uv`](https://docs.astral.sh/uv/getting-started/installation/), a fast Python package manager.

```bash
# 0️⃣ Install Ollama (if using local inference)
#    - Download and install from https://ollama.com/download
#    - Or use your package manager (recommended for security):
#      - macOS: brew install ollama
#      - Linux: Follow instructions at https://ollama.com/download/linux
#      - Windows: Download installer from https://ollama.com/download/windows

#    - Pull a model (required for inference). Use smaller models for CPU-only systems:
ollama pull llama3.2:1b    # 1B model - fast on CPU
# OR
ollama pull llama3.2:3b    # 3B model - default, slower on CPU

#    - Verify Ollama is running (should return JSON with model list):
curl http://localhost:11434/api/tags

# 1️⃣ Create a virtual environment in the current directory (.venv)
#    - Use Python 3.12 explicitly
#    - --seed ensures pip and core packaging tools are installed in the venv
uv venv --python 3.12 --seed

# 2️⃣ Activate the virtual environment
#    - Updates PATH so `python` and `pip` now point to .venv/bin/
#    - Sets VIRTUAL_ENV for the current shell session
source .venv/bin/activate

# 3️⃣ Install or upgrade the llama_stack package inside the active venv
#    - -U (or --upgrade) ensures the latest version is installed
#    - This installs the CLI (`llama`) and required core dependencies
uv pip install -U llama_stack

# 4️⃣ Install or upgrade the llama-stack-client SDK
#    - This is the Python client library for interacting with a Llama Stack server
#    - Provides high-level APIs for inference, agents, safety, and more
uv pip install -U llama-stack-client

# 5️⃣ Install additional dependencies required by the "starter" demo profile
#    - `llama stack list-deps starter` prints required packages (one per line)
#    - `xargs -L1 pip install` installs each dependency line-by-line
#    - Assumes the virtual environment is active
llama stack list-deps starter | xargs -L1 uv pip install

# 6️⃣ Run the "starter" Llama Stack server
#    - This starts a LOCAL server on port 8321 (default for starter distribution)
#    - The server connects to Ollama at localhost:11434 for inference
#    - IMPORTANT: Keep this terminal open - the server runs in foreground
#    - The server must stay running for demos to work
OLLAMA_URL=http://localhost:11434/v1 uv run llama stack run starter

# 7️⃣ Verify the server is running (in a NEW terminal - server must be running!)
#    - Open a SECOND terminal window
#    - Navigate to the repository directory and activate the virtual environment
cd <repo-root>  # Navigate to where you cloned the repo
source .venv/bin/activate

# 8️⃣ Test the connection
#    - Run the client setup demo to verify server is running
python -m demos.01_foundations.01_client_setup localhost 8321  # Note: port 8321 for local starter server
```

### Troubleshooting

**Port already in use (8321):**
```bash
# Find and kill the process using port 8321
lsof -i :8321
kill <PID>
```

**Server not starting:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check if a model is pulled
ollama list
```

**Version compatibility errors:**
```bash
# Reinstall all packages with matching versions
pip uninstall -y llama-stack llama-stack-api llama-stack-client
uv pip install -U llama-stack llama-stack-client
```

## Available Demos

### 01_foundations
Foundation examples demonstrating core Llama Stack concepts and basic usage patterns.

### 02_responses_basic
Basic examples showing how to work with responses in Llama Stack.

### 03_rag
RAG (Retrieval-Augmented Generation) examples showing how to ground model responses in retrieved documents using Llama Stack's vector stores and search capabilities.

### 04_agents
Agent examples demonstrating how to build conversational agents with various capabilities including chat, multimodal processing, document grounding, custom tools, and multi-agent coordination.

### 06_openai_compatibility
Demos showing that existing OpenAI Python SDK code works against a Llama Stack server with only a `base_url` change, covering chat completions, tool calling, and the Responses API.
