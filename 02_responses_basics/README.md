# Responses Basics

## Overview
This folder teaches the fundamentals of the Responses API, which provides a higher-level abstraction for generating text responses with instructions, tools, and structured outputs. These examples demonstrate different response patterns and capabilities.

## Learning Objectives
- Use the Responses API for text generation
- Configure response instructions to control behavior
- Implement tool calling through agents
- Manage multi-turn conversations with conversation IDs
- Stream responses in real-time
- Generate structured outputs with JSON mode and schemas

## Demos

### Demo 1: Simple Response
**File**: `01_simple_response.py`

**Concepts**: Responses API, instructions parameter, input messages, difference between Responses API and Chat Completions API

**Description**: Demonstrates the basic usage of the Responses API to generate text completions using instructions and user input. Shows how the Responses API differs from the Chat Completions API.

**Run**:
```bash
python -m 02_responses_basics.01_simple_response localhost 8321 --prompt "Hello"
```

### Demo 2: Tool Calling
**File**: `02_tool_calling.py`

**Concepts**: Agent tool calling, web search tool, function execution, tool choice

**Description**: Shows how to use the Responses API with an agent that can call tools like web search to retrieve real-time information and answer questions.

**Run**:
```bash
python -m 02_responses_basics.02_tool_calling localhost 8321 --prompt "Search the web for who was the 42nd president of the United States and answer with the name only."
```

### Demo 3: Conversation Turns
**File**: `03_conversation_turns.py`

**Concepts**: Conversation management, conversation IDs, multi-turn dialogue, stateful conversations, context preservation

**Description**: Demonstrates how to maintain context across multiple turns in a conversation using a shared conversation ID, enabling the model to remember previous interactions.

**Run**:
```bash
python -m 02_responses_basics.03_conversation_turns localhost 8321
```

### Demo 4: Streaming Responses
**File**: `04_streaming_responses.py`

**Concepts**: Response streaming, real-time output, event handling, progressive rendering, multi-turn conversations

**Description**: Shows how to stream responses in real-time across multiple conversation turns, allowing for progressive display of output as it's generated.

**Run**:
```bash
python -m 02_responses_basics.04_streaming_responses localhost 8321
```

### Demo 5: Response Formats
**File**: `05_response_formats.py`

**Concepts**: JSON mode, JSON schema validation, structured outputs, json_object format, json_schema format, schema enforcement

**Description**: Demonstrates how to generate structured outputs using JSON mode (for valid JSON) and JSON schema (for schema-validated outputs). Shows the difference between the two approaches.

**Run**:
```bash
python -m 02_responses_basics.05_response_formats localhost 8321
```
