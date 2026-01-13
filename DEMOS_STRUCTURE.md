# Llama Stack Demos - Repository Structure

## Overview

This document outlines the comprehensive structure for the llama-stack-demos repository. The demos are organized as progressive "building blocks" that build upon one another, starting with basic operations and advancing to complex multi-agent systems and production-ready applications.

## Key Llama Stack APIs

**Based on the current codebase (January 2026), here are the actual APIs:**

### Core APIs
- **Agents API** - Routes at `/responses/*` for agent-like workflows (create, retrieve, list, delete responses)
- **Inference API** - Routes at `/chat/completions`, `/completions`, `/embeddings`, `/inference/rerank`
- **Tools API** - Tool and toolgroup registration, including MCP support
- **Vector IO API** - Vector database operations
- **Vector Stores API** - OpenAI-compatible vector store management
- **Safety API** - Content moderation and safety shields
- **Conversations API** - Conversation management
- **Prompts API** - Prompt template management
- **RAG Tool API** - Built-in RAG functionality

### Other APIs
- **Eval API** - Evaluation and scoring
- **Post-Training API** - Model fine-tuning
- **Files API** - File upload/management
- **Models API** - Model management
- **Batches/Benchmarks** - Batch processing and benchmarking
- **DatasetIO/Datasets** - Dataset management

**Important**: The Agents API routes are at `/responses/*`, not `/agents/*`. The client SDK includes helper classes that make working with these APIs easier.

## Design Principles

1. **Progressive Complexity**: Each phase builds on concepts from previous phases
2. **Self-Contained Examples**: Each demo can run independently while clearly documenting prerequisites
3. **Clear Documentation**: Every folder includes README files explaining concepts and learning objectives
4. **Shared Utilities**: Common code lives in `shared/` to avoid duplication across demos
5. **Production Ready**: Later phases demonstrate real-world patterns and best practices
6. **Hands-On Learning**: All examples are runnable Python scripts with optional notebooks

## Repository Structure

```
llama-stack-demos/
├── README.md                           # Overview & quick start guide
├── DEMOS_STRUCTURE.md                  # This document
├── .env.example                        # Environment variables template
├── pyproject.toml                      # Project dependencies
├── uv.lock                             # Lock file for dependencies
│
├── docs/
│   ├── setup.md                        # Common setup instructions
│   ├── troubleshooting.md             # Common issues & solutions
│   ├── architecture.md                 # Architecture diagrams & explanations
│   └── api_reference.md               # Llama Stack API quick reference
│
├── demos/
│   │
│   ├── 01-foundations/                 # Phase 1: Basic Building Blocks
│   │   ├── README.md                   # Overview of foundation concepts
│   │   ├── 01_client_setup.py         # Connect to Llama Stack server
│   │   ├── 02_chat_completion.py      # Basic inference with chat completions
│   │   ├── 03_streaming_chat.py       # Streaming responses
│   │   ├── 04_system_prompts.py       # Using system messages
│   │   ├── 05_vector_db_basics.py     # Register & use vector DB
│   │   ├── 06_insert_documents.py     # Insert documents into vector store
│   │   ├── 07_query_vectors.py        # Query vector store
│   │   ├── 08_tool_registration.py    # Register custom tools
│   │   └── 09_mcp_tools.py            # Register & use MCP tools
│   │
│   ├── 02-responses-basics/            # Phase 2: Responses API
│   │   ├── README.md                   # Responses API overview (OpenAI-compatible)
│   │   ├── 01_simple_response.py      # Basic Responses API usage
│   │   ├── 02_tool_calling.py         # Tool calling with Responses API
│   │   ├── 03_conversation_turns.py   # Multi-turn conversations
│   │   ├── 04_streaming_responses.py  # Streaming responses and tool calls
│   │   └── 05_response_formats.py     # Structured outputs & JSON mode
│   │
│   ├── 03-rag/                         # Phase 3: RAG Patterns
│   │   ├── README.md                   # RAG concepts & patterns
│   │   ├── 01_simple_rag.py           # Basic RAG with file_search tool
│   │   ├── 02_multi_source_rag.py     # RAG with multiple vector DBs
│   │   ├── 03_rag_with_metadata.py    # Metadata filtering
│   │   ├── 04_chunking_strategies.py  # Different chunking approaches
│   │   └── 05_hybrid_search.py        # Vector search + web search
│   │
│   ├── 04-advanced-tools/              # Phase 4: Advanced Tool Use
│   │   ├── README.md                   # Advanced tool patterns
│   │   ├── 01_multi_tool_workflows.py # RAG + custom tools + MCP tools
│   │   ├── 02_multi_step_reasoning.py # Complex tool chaining
│   │   ├── 03_error_handling.py       # Robust error handling patterns
│   │   ├── 04_parallel_tools.py       # Parallel tool execution
│   │   └── 05_safety_integration.py   # Input/output safety shields
│   │
│   ├── 05-multi-agent/                 # Phase 5: Multi-Agent Patterns
│   │   ├── README.md                   # Multi-agent architectures
│   │   ├── 01_agent_roles.py          # Specialized response instances
│   │   ├── 02_task_delegation.py      # Route tasks to specialized agents
│   │   ├── 03_agent_coordination.py   # Coordinate multiple agents
│   │   ├── 04_agent_fleet/            # Full multi-agent system
│   │   │   ├── README.md
│   │   │   ├── fleet.py
│   │   │   ├── task_manager.py
│   │   │   └── agents/
│   │   │       ├── planner/
│   │   │       ├── executor/
│   │   │       └── composer/
│   │   └── 05_hierarchical_orchestration.py  # Planner + executor pattern
│   │
│   ├── 06-production-patterns/         # Phase 6: Production-Ready Patterns
│   │   ├── README.md                   # Production best practices
│   │   ├── 01_logging_monitoring.py   # Logging & observability
│   │   ├── 02_rate_limiting.py        # Rate limits & retries
│   │   ├── 03_caching_strategies.py   # Response & embedding caching
│   │   ├── 04_async_patterns.py       # Async processing
│   │   ├── 05_batch_processing.py     # Batch operations
│   │   └── 06_testing_agents.py       # Testing & evaluation
│   │
│   └── 07-end-to-end-apps/            # Phase 7: Complete Applications
│       ├── README.md                   # Full app examples
│       ├── knowledge_assistant/        # RAG-based Q&A system
│       │   ├── README.md
│       │   ├── app.py
│       │   ├── frontend/
│       │   │   ├── build/
│       │   │   └── src/
│       │   └── notebooks/
│       ├── code_assistant/             # Code analysis & generation
│       │   ├── README.md
│       │   ├── app.py
│       │   └── tools/
│       ├── ops_automation/             # OCP/K8s automation agent
│       │   ├── README.md
│       │   ├── app.py
│       │   └── mcp_tools/
│       └── data_analysis/              # Multi-agent data pipeline
│           ├── README.md
│           ├── app.py
│           └── agents/
│
├── kubernetes/                          # K8s/OpenShift deployment manifests
│   ├── README.md
│   ├── llama-stack/                    # Llama Stack server deployment
│   ├── llama-serve/                    # vLLM model servers
│   ├── mcp-servers/                    # MCP tool servers
│   │   ├── ansible-mcp/
│   │   ├── openshift-mcp/
│   │   ├── slack-mcp/
│   │   └── llamastack/
│   ├── safety-model/                   # Safety shield deployment
│   ├── observability/                  # Monitoring & logging
│   └── kustomize/                      # Kustomize overlays
│
├── shared/                              # Shared utilities across demos
│   ├── __init__.py
│   ├── client.py                       # Common client setup & configuration
│   ├── logging_config.py               # Logging utilities
│   ├── env_loader.py                   # Environment management
│   ├── test_helpers.py                 # Testing utilities
│   └── utils.py                        # General utilities
│
├── tests/                               # Integration & evaluation tests
│   ├── integration/                    # Integration tests
│   ├── eval/                           # Agent evaluation tests
│   └── fixtures/                       # Test fixtures & data
│
└── distribution/                        # Custom distributions
    └── remote-vllm-granite-embedding/
```

## Phase-by-Phase Breakdown

### Phase 1: Foundations (01-foundations/)

**Learning Objectives**: Master the basic building blocks of Llama Stack

**Demos**:
1. **Client Setup** - Connect to a Llama Stack server, check health
2. **Chat Completion** - Basic inference using chat completions
3. **Streaming Chat** - Stream responses for better UX
4. **System Prompts** - Configure behavior with system messages
5. **Vector DB Basics** - Register and configure a vector database
6. **Insert Documents** - Add documents to vector stores with embeddings
7. **Query Vectors** - Perform similarity searches
8. **Tool Registration** - Register custom tools and toolgroups
9. **MCP Tools** - Connect to Model Context Protocol servers

**APIs Used**: Inference, Vector IO, Tools
**Prerequisites**: None - start here!

### Phase 2: Responses API Basics (02-responses-basics/)

**Learning Objectives**: Use the Responses API for agent-like workflows

**Demos**:
1. **Simple Response** - Basic Responses API call with OpenAI-compatible interface
2. **Tool Calling** - Single tool call with automatic execution
3. **Conversation Turns** - Multi-turn conversations with context
4. **Streaming Responses** - Stream responses and tool calls
5. **Response Formats** - Structured outputs and JSON mode

**APIs Used**: Responses (via /v1 endpoint), Tools
**Prerequisites**: Phase 1 (01-04)

### Phase 3: RAG (03-rag/)

**Learning Objectives**: Implement Retrieval-Augmented Generation patterns

**Demos**:
1. **Simple RAG** - Using file_search tool with Responses API
2. **Multi-Source RAG** - Query multiple vector databases
3. **RAG with Metadata** - Filter results by metadata
4. **Chunking Strategies** - Different document chunking approaches
5. **Hybrid Search** - Combine vector search with web search tools

**APIs Used**: Responses, Vector IO, Tools
**Prerequisites**: Phase 1 (05-07) and Phase 2 (01-02)

### Phase 4: Advanced Tool Use (04-advanced-tools/)

**Learning Objectives**: Build complex workflows with multiple tools

**Demos**:
1. **Multi-Tool Workflows** - Combine RAG, custom tools, and MCP tools
2. **Multi-Step Reasoning** - Complex problems with tool chaining
3. **Error Handling** - Robust error handling and tool retries
4. **Parallel Tool Calls** - Execute multiple tools concurrently
5. **Safety Integration** - Add input/output shields for content filtering

**APIs Used**: Responses, Tools, Safety, Vector IO
**Prerequisites**: Phases 2 and 3

### Phase 5: Multi-Agent Patterns (05-multi-agent/)

**Learning Objectives**: Design systems with multiple specialized agents

**Demos**:
1. **Agent Roles** - Multiple Response instances with specialized instructions
2. **Task Delegation** - Route tasks to appropriate specialized agents
3. **Agent Coordination** - Coordinate multiple agents for complex workflows
4. **Agent Fleet** - Full multi-agent system with task management
5. **Hierarchical Orchestration** - Planner/executor coordination patterns

**APIs Used**: Responses, Tools, Conversations, Vector IO
**Prerequisites**: Phases 2, 3, and 4

### Phase 6: Production Patterns (06-production-patterns/)

**Learning Objectives**: Production-ready patterns and best practices

**Demos**:
1. **Logging & Monitoring** - Observability for agent systems
2. **Rate Limiting** - Handle rate limits, retries, and backoff
3. **Caching Strategies** - Cache responses and embeddings efficiently
4. **Async Patterns** - Asynchronous processing and event handling
5. **Batch Processing** - Process multiple requests efficiently
6. **Testing Agents** - Testing strategies and evaluation frameworks

**Prerequisites**: Any earlier phase, but especially useful after Phase 4-5

### Phase 7: End-to-End Apps (07-end-to-end-apps/)

**Learning Objectives**: Build complete, production-ready applications

**Applications**:

1. **Knowledge Assistant**
   - RAG-based Q&A system with web interface
   - Document upload and processing
   - Multi-source knowledge retrieval
   - Uses: Phases 1, 2, 3, 6

2. **Code Assistant**
   - Code analysis and generation agent
   - Integration with development tools
   - Code review and suggestions
   - Uses: Phases 2, 3, 4, 6

3. **Ops Automation**
   - OpenShift/Kubernetes automation agent
   - MCP tools for cluster management
   - Multi-step operational workflows
   - Uses: Phases 1, 2, 4, 5, 6

4. **Data Analysis**
   - Multi-agent data processing pipeline
   - Specialized agents for different analysis tasks
   - Coordinated data workflows
   - Uses: Phases 2, 4, 5, 6

**Prerequisites**: Multiple earlier phases (see each app's README)

## Phase Progression

**Foundations** → **Responses API** → **RAG** → **Advanced Tools** → **Multi-Agent** → **Production** → **Full Apps**

Each phase builds on previous concepts:
- Phase 1 introduces basic Llama Stack operations (inference, vectors, tools)
- Phase 2 introduces the Responses API for agent-like behavior
- Phase 3 combines Responses API with RAG
- Phase 4 demonstrates complex multi-tool workflows
- Phase 5 shows multi-agent orchestration patterns
- Phase 6 covers production best practices
- Phase 7 provides complete end-to-end applications

## Demo Naming Convention

- **Numbered Prefixes** (01, 02...): Indicate recommended learning order within each phase
- **Descriptive Names**: Clearly state what concept or pattern is demonstrated
- **Standalone Files**: Each `.py` file is independently runnable
- **Optional Notebooks**: Some demos may include Jupyter notebooks for interactive exploration

## Common Patterns Across Demos

### Standard Demo Structure

Each demo follows this pattern:

```python
#!/usr/bin/env python3
"""
Demo: [Name]
Phase: [Number]
Prerequisites: [List of prerequisite demos]

Description:
[What this demo teaches]

Learning Objectives:
- [Objective 1]
- [Objective 2]
"""

# Standard imports
from llama_stack_client import LlamaStackClient
from shared.client import setup_client, load_config
from shared.logging_config import setup_logging
import argparse

# Demo-specific imports
...

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-r", "--remote", action="store_true",
                       help="Use remote server")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    args = parser.parse_args()

    # Setup
    logger = setup_logging(verbose=args.verbose)
    client = setup_client(remote=args.remote)

    # Demo logic
    ...

if __name__ == "__main__":
    main()
```

### Environment Configuration

All demos use a common `.env` file:

```bash
# Llama Stack Server
LOCAL_BASE_URL=http://localhost:8321
REMOTE_BASE_URL=https://your-server.example.com

# MCP Servers
LOCAL_MCP_URL=http://host.containers.internal:8000/sse
REMOTE_MCP_URL=https://your-mcp-server.example.com/sse

# Vector Database
REMOTE_VDB_PROVIDER=milvus
LOCAL_VDB_PROVIDER=faiss

# Models
DEFAULT_MODEL=meta-llama/Llama-3.2-3B-Instruct
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Optional: API Keys for external services
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

## Documentation Standards

### Phase README Structure

Each phase folder includes a comprehensive README:

```markdown
# Phase [N]: [Name]

## Overview
[What this phase teaches]

## Learning Objectives
- [Objective 1]
- [Objective 2]

## Prerequisites
- [Required prior knowledge]
- [Links to prerequisite demos]

## Demos

### Demo 1: [Name]
**File**: `01_name.py`
**Concepts**: [List key concepts]
**Description**: [What it does]

### Demo 2: [Name]
...

## Key Concepts

### [Concept 1]
[Explanation]

### [Concept 2]
[Explanation]

## Common Pitfalls
- [Pitfall 1 and solution]
- [Pitfall 2 and solution]

## Next Steps
[Where to go after completing this phase]
```

### Individual Demo Comments

Each demo file includes:
- Docstring with description and learning objectives
- Inline comments explaining key concepts
- Links to relevant documentation
- Example output when helpful

## Testing Strategy

### Unit Tests
- Located in `tests/integration/`
- Test individual components and patterns
- Run with: `pytest tests/integration/`

### Evaluation Tests
- Located in `tests/eval/`
- Evaluate agent quality and performance
- Test tool calling accuracy
- Run with: `pytest tests/eval/`

### Integration Tests
- Test complete workflows
- Verify demos work end-to-end
- Run with: `make test-demos`

## Migration Path from Current Structure

To migrate the existing demos:

1. **Preserve existing complex demos**:
   - Move `demos/rag_agentic/` → `demos/07-end-to-end-apps/knowledge_assistant/`
   - Move `demos/a2a_llama_stack/` → `demos/05-multi-agent/04_agent_fleet/`

2. **Extract building blocks**:
   - Extract concepts from `tests/scripts/0_simple_agent.py` → Phase 2 demos
   - Extract concepts from `tests/scripts/1_simple_agent_with_RAG.py` → Phase 3 demos

3. **Create new foundational demos**:
   - Build Phase 1 from scratch (basic operations)
   - Create intermediate demos in Phases 4 and 6

4. **Update documentation**:
   - Create phase READMEs
   - Update main README with new structure
   - Add cross-references between demos

## Maintenance Guidelines

### Adding New Demos

1. Identify the appropriate phase
2. Follow naming convention (numbered prefix)
3. Use standard demo structure
4. Update phase README
5. Add tests if applicable
6. Update cross-references

### Updating Existing Demos

1. Maintain backward compatibility when possible
2. Update version comments if API changes
3. Test all demos in the phase
4. Update documentation

### Deprecating Demos

1. Mark as deprecated in comments
2. Add redirect to replacement demo
3. Keep for one release cycle
4. Remove and update references

## Success Metrics

A successful demo should:
- ✅ Run without errors on a fresh setup
- ✅ Have clear learning objectives
- ✅ Take 5-15 minutes to understand and run
- ✅ Include helpful comments and documentation
- ✅ Demonstrate one focused concept
- ✅ Build on previous concepts logically

## Resources

### Internal Documentation
- [Setup Guide](docs/setup.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Architecture Overview](docs/architecture.md)

### External Documentation
- [Llama Stack Documentation](https://llamastack.github.io/docs)
- [Llama Stack GitHub](https://github.com/llamastack/llama-stack)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Your agent, your rules: A deep dive into the Responses API with Llama Stack](https://developers.redhat.com/articles/2025/08/20/your-agent-your-rules-deep-dive-responses-api-llama-stack)
- [Your AI agents, evolved: Modernize Llama Stack agents by migrating to the Responses API](https://developers.redhat.com/articles/2025/12/09/your-ai-agents-evolved-modernize-llama-stack-agents-migrating-responses-api)
- [OpenAI API Compatibility](https://llama-stack.readthedocs.io/en/latest/openai/index.html)

## Contributing

See the main README for contribution guidelines. When adding new demos:

1. Follow the structure outlined in this document
2. Ensure demos are tested and documented
3. Update relevant README files
4. Submit PR with clear description

## Questions?

Open an issue in the [repository](https://github.com/opendatahub-io/llama-stack-demos/issues) with questions or suggestions for improving this structure.
