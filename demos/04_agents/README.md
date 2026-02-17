# Agents

## Overview
This folder teaches how to build conversational agents using the Llama Stack Agent API. These examples demonstrate different agent capabilities including chat, multimodal processing, document grounding, custom tools, RAG integration, reasoning patterns, and multi-agent coordination.

## Learning Objectives
- Create and configure conversational agents
- Implement multimodal agents that process images
- Build agents that reference and retrieve from documents
- Integrate custom tools with agents
- Combine RAG with agent workflows
- Implement ReACT (Reasoning and Acting) patterns
- Coordinate multiple specialized agents

## Demos

### Demo 1: Simple Agent Chat
**File**: `01_simple_agent_chat.py`

**Concepts**: Agent API, agent sessions, web search integration, safety shields, stateful conversations, tool-enabled agents

**Description**: Creates a basic conversational agent with web search capabilities and safety shields. Shows how to set up agent sessions for multi-turn conversations and configure safety features.

**Run**:
```bash
python -m demos.04_agents.01_simple_agent_chat --host localhost --port 8321 --model_id meta-llama/Llama-3.3-70B-Instruct
```

### Demo 2: Multimodal Chat
**File**: `02_chat_multimodal.py`

**Concepts**: Multimodal agents, image processing, vision capabilities, image-text interactions, multimodal messages

**Description**: Demonstrates how to create an agent with multimodal capabilities that can process and understand both text and images in conversations.

**Run**:
```bash
python -m demos.04_agents.02_chat_multimodal --host localhost --port 8321 --model_id meta-llama/Llama-3.3-70B-Instruct
```

### Demo 3: Chat with Documents
**File**: `03_chat_with_documents.py`

**Concepts**: Document-grounded agents, document attachment, file_search tool, agent-level RAG, context-aware responses

**Description**: Shows how to create an agent that can reference and retrieve information from attached documents using the file_search tool for document-grounded conversations.

**Run**:
```bash
python -m demos.04_agents.03_chat_with_documents --host localhost --port 8321 --model_id meta-llama/Llama-3.3-70B-Instruct
```

### Demo 4: Agent with Tools
**File**: `04_agent_with_tools.py`

**Concepts**: Custom tool integration, calculator tool, stock ticker tool, web search tool, function calling, tool registration

**Description**: Demonstrates how to integrate custom tools (calculator, stock ticker data, search capabilities) with an agent, enabling it to perform specialized tasks beyond text generation.

**Run**:
```bash
python -m demos.04_agents.04_agent_with_tools --host localhost --port 8321 --model_id meta-llama/Llama-3.3-70B-Instruct
```

### Demo 5: RAG Agent
**File**: `05_rag_agent.py`

**Concepts**: RAG-enabled agents, vector database integration, document retrieval, knowledge-grounded generation, agent-RAG patterns

**Description**: Implements a RAG agent that uses vector databases for efficient information retrieval from document collections, combining conversational abilities with document search.

**Run**:
```bash
python -m demos.04_agents.05_rag_agent --host localhost --port 8321 --model_id meta-llama/Llama-3.3-70B-Instruct
```

### Demo 6: ReACT Agent
**File**: `06_react_agent.py`

**Concepts**: ReACT pattern (Reasoning and Acting), multi-step reasoning, action planning, iterative problem solving, thought-action-observation cycles

**Description**: Implements a ReACT (Reasoning and Acting) agent that performs multi-step reasoning and takes actions based on those reasoning steps, demonstrating iterative problem-solving.

**Run**:
```bash
python -m demos.04_agents.06_react_agent --host localhost --port 8321 --model_id meta-llama/Llama-3.3-70B-Instruct
```

### Demo 7: Agent Routing
**File**: `07_agent_routing.py`

**Concepts**: Multi-agent systems, agent coordination, specialized agents, output synthesis, agent orchestration, task delegation

**Description**: Coordinates multiple specialized agents and synthesizes their outputs, demonstrating how to build multi-agent systems where different agents handle different aspects of a task.

**Run**:
```bash
python -m demos.04_agents.07_agent_routing --host localhost --port 8321 --model_id meta-llama/Llama-3.3-70B-Instruct
```

## Usage Tips

- All scripts accept `--host` and `--port` parameters to specify the Llama Stack server connection
- You can specify a particular model using the `--model_id` parameter (as shown in the examples above)
- If no model is specified, the scripts will automatically select an available model
- Look at `01_simple_agent_chat` for an example of how to automatically pick an available safety shield for the agent

For more information on the Llama Stack framework, refer to the [official documentation](https://github.com/meta-llama/llama-stack).
