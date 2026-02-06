# Foundations

## Overview
This folder teaches the fundamental building blocks of Llama Stack, including client setup, chat completions, vector databases, and tool integration. These examples cover the core APIs and concepts needed to build AI applications.

## Learning Objectives
- Initialize and connect to a Llama Stack server
- Perform chat completions with streaming support
- Customize model behavior with system prompts
- Create and manage vector stores for semantic search
- Register and use custom tools with agents
- Integrate MCP (Model Context Protocol) tools

## Demos

### Demo 1: Client Setup
**File**: `01_client_setup.py`

**Concepts**: LlamaStackClient initialization, server health checks, connection management

**Description**: Validates your connection to a Llama Stack server by performing a health check. This is the foundational step for all subsequent examples.

**Run**:
```bash
python -m 01_foundations.01_client_setup localhost 8321
```

### Demo 2: Chat Completion
**File**: `02_chat_completion.py`

**Concepts**: Chat completions API, model selection, streaming vs non-streaming responses, message formatting

**Description**: Demonstrates basic inference using the chat completions API. Shows how to send user messages to a model and receive responses, with support for both streaming and non-streaming modes.

**Run**:
```bash
# Basic chat completion
python -m 01_foundations.02_chat_completion localhost 8321 --prompt "Hello"

# Stream tokens as they arrive
python -m 01_foundations.02_chat_completion localhost 8321 --prompt "Hello" --stream
```

### Demo 3: System Prompts
**File**: `03_system_prompts.py`

**Concepts**: System prompts, instruction customization, model behavior control, single-turn conversations

**Description**: Shows how to customize the system prompt to control model behavior and personality for single-turn chat interactions.

**Run**:
```bash
# Use default system prompt
python -m 01_foundations.03_system_prompts localhost 8321 --prompt "Hello"

# Override with custom system prompt
python -m 01_foundations.03_system_prompts localhost 8321 --system_prompt "You are concise." --prompt "Hello"
```

### Demo 4: Vector DB Basics
**File**: `04_vector_db_basics.py`

**Concepts**: Vector store creation, document embedding, vector search, semantic similarity

**Description**: Introduces vector databases by creating a vector store, adding a document, and running a semantic search query.

**Run**:
```bash
# Use default text and query
python -m 01_foundations.04_vector_db_basics localhost 8321

# Provide custom text and query
python -m 01_foundations.04_vector_db_basics localhost 8321 --text "Llama Stack unifies AI services." --query "What does Llama Stack do?"
```

### Demo 5: Insert Documents
**File**: `05_insert_documents.py`

**Concepts**: Document ingestion, file uploads, URL-based insertion, vector store persistence, chunking strategies

**Description**: Demonstrates how to create or reuse a vector store and populate it with documents from URLs or local directories.

**Run**:
```bash
# Insert documents from URLs
python -m 01_foundations.05_insert_documents localhost 8321

# Insert files from a local directory
python -m 01_foundations.05_insert_documents localhost 8321 --file_dir ./docs

# Insert into an existing vector store
python -m 01_foundations.05_insert_documents localhost 8321 --vector_store_id <vector-store-id>
```

### Demo 6: Search Vectors
**File**: `06_search_vectors.py`

**Concepts**: Vector search queries, similarity scoring, result ranking, chunk retrieval

**Description**: Inserts documents into a vector store and demonstrates how to run vector search queries to retrieve relevant content.

**Run**:
```bash
python -m 01_foundations.06_search_vectors localhost 8321 --query "What does Llama Stack do?"
```

### Demo 7: Tool Registration
**File**: `07_tool_registration.py`

**Concepts**: Client-side tool registration, function calling, custom tool implementation, agent tool integration

**Description**: Shows how to register custom Python functions (calculator, stock ticker, web search) as tools that agents can call during conversations.

**Run**:
```bash
export TAVILY_SEARCH_API_KEY=your_key_here
python -m 01_foundations.07_tool_registration localhost 8321
```

### Demo 8: MCP Tools
**File**: `08_mcp_tools.py`

**Concepts**: Model Context Protocol (MCP), MCP servers, tool groups, remote tool registration

**Description**: Demonstrates how to start a local MCP server and register its tools with Llama Stack for use in agent workflows.

**Run**:
```bash
# Terminal 1: start the MCP server (requires: pip install mcp)
python -m 01_foundations.08_mcp_tools serve

# Terminal 2: register the MCP toolgroup with Llama Stack (Optional)
llama-stack-client toolgroups register plus-tools \
  --provider-id model-context-protocol \
  --mcp-endpoint "http://localhost:8000/sse"

# Terminal 2: invoke the add tool through the runtime
python -m 01_foundations.08_mcp_tools run localhost 8321 --mcp_endpoint http://localhost:8000/sse --tool_name add --a 1 --b 1
```
