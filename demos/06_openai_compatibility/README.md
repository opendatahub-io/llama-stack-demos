# OpenAI Compatibility Demos

Llama Stack implements OpenAI-compatible APIs (`/v1/chat/completions`, `/v1/responses`). These demos prove that **existing OpenAI code works against a Llama Stack server** with only a `base_url` change — no SDK swap required.

## Key Differences from Native Llama Stack Client

| | Native `LlamaStackClient` | `openai.OpenAI` |
|---|---|---|
| **base_url** | `http://host:port` | `http://host:port/v1` (needs `/v1` suffix) |
| **api_key** | Not required | Required by SDK; use `"fake"` or set `LLAMA_STACK_API_KEY` |
| **Shared utils** | Can import `demos.shared.utils` | Not compatible — model resolution is inlined |

## Demos

### 01_chat_completion.py
Non-streaming and streaming chat completions using `openai.OpenAI`.

```bash
# Non-streaming
python -m demos.06_openai_compatibility.01_chat_completion localhost 8321

# Streaming
python -m demos.06_openai_compatibility.01_chat_completion localhost 8321 --stream
```

### 02_tool_calling.py
Standard OpenAI function-calling flow: define tools, parse `tool_calls`, execute locally, send results back.

```bash
python -m demos.06_openai_compatibility.02_tool_calling localhost 8321
```

### 03_responses_api.py
Uses `client.responses.create()` from the OpenAI SDK against Llama Stack, with both string and structured message-list inputs.

```bash
python -m demos.06_openai_compatibility.03_responses_api localhost 8321
```

## Prerequisites

- A running Llama Stack server (e.g. `llama stack run starter`)
- The `openai` Python package (`pip install openai>=1.75.0`)
