# Llama Stack Demos

This directory contains demo examples for getting started with Llama Stack.

## Setup

First, install [`uv`](https://docs.astral.sh/uv/getting-started/installation/), a fast Python package manager.

```bash
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

# 3.5️⃣ Install or upgrade the llama-stack-client SDK
#    - This is the Python client library for interacting with a Llama Stack server
#    - Provides high-level APIs for inference, agents, safety, and more
uv pip install -U llama-stack-client

# 4️⃣ Install additional dependencies required by the "starter" demo profile
#    - `llama stack list-deps starter` prints required packages (one per line)
#    - `xargs -L1 pip install` installs each dependency line-by-line
#    - Assumes the virtual environment is active
llama stack list-deps starter | xargs -L1 uv pip install

# 5️⃣ Run the "starter" demo using a local Ollama server
#    - OLLAMA_URL sets the endpoint for the Ollama model server
#    - This environment variable applies only to this command
#    - The starter demo connects to Ollama at localhost:11434
OLLAMA_URL=http://localhost:11434/v1 uv run llama stack run starter
```

## Available Demos

### 01_foundations
Foundation examples demonstrating core Llama Stack concepts and basic usage patterns.

### 02_responses_basic
Basic examples showing how to work with responses in Llama Stack.
