# Math MCP Server for Kubernetes

A FastAPI-based HTTP server that provides mathematical operations with MCP-compatible endpoints for integration with Llama Stack.

## Architecture

```
┌─────────────────────┐
│   User / Client     │
└──────────┬──────────┘
           │
           │ kubectl / curl
           ▼
┌─────────────────────┐         ┌──────────────────┐
│   Llama Stack       │────────▶│   vLLM Server    │
│   (port 8321)       │  Calls  │   (port 8000)    │
└──────────┬──────────┘  Model  └──────────────────┘
           │
           │ Registered Toolgroup
           │ "math-tools"
           ▼
┌─────────────────────┐
│  Math MCP Server    │ ← ✅ Running and Healthy!
│   (port 8080)       │
│                     │
│  Endpoints:         │
│  • GET  /health     │
│  • GET  /mcp/tools  │
│  • POST /calculate  │
│                     │
│  Operations:        │
│  • add, subtract    │
│  • multiply, divide │
│  • power, sqrt      │
│  • abs, factorial   │
└─────────────────────┘
```

## Overview

This server demonstrates how to build and deploy LLM tool extensions as Kubernetes microservices. It provides 8 mathematical operations through a REST API and integrates with Llama Stack as a registered toolgroup.

### Features

- **8 Math Operations**: add, subtract, multiply, divide, power, sqrt, abs, factorial
- **HTTP API**: FastAPI server with health checks and MCP-compatible endpoints
- **Kubernetes Native**: Deployment with resource limits and service discovery
- **Llama Stack Integration**: Registered as toolgroup "math-tools"
- **Production Ready**: Error handling, validation, and comprehensive testing

## Prerequisites

- Kubernetes cluster (Kind, minikube, or cloud provider)
- Docker installed
- kubectl configured
- Llama Stack deployed (see parent README.md)

## Quick Start

### 1. Build and Deploy

```bash
# Navigate to the math-mcp directory
cd kubernetes/mcp-servers/math-mcp

# Build Docker image
docker build -t math-mcp-server:latest .

# Load into Kind cluster (if using Kind)
kind load docker-image math-mcp-server:latest --name llama-stack-test

# Deploy to Kubernetes
kubectl apply -f 00-math-mcp-deploy.yaml
kubectl apply -f 01-math-mcp-service.yaml

# Verify deployment
kubectl get pods -l app=math-mcp-server
kubectl logs -l app=math-mcp-server
```

### 2. Register with Llama Stack

```bash
# Ensure Llama Stack is accessible
kubectl port-forward svc/llamastack-vllm 8321:8321

# Register the math toolgroup
llama-stack-client --endpoint http://localhost:8321 toolgroups register \
  math-tools \
  --provider-id model-context-protocol \
  --mcp-endpoint http://math-mcp-server.default.svc.cluster.local:8080

# Verify registration
llama-stack-client --endpoint http://localhost:8321 toolgroups list
```

Expected output:
```
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ identifier ┃ provider_id            ┃ args ┃ mcp_endpoint    ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ math-tools │ model-context-protocol │ None │ McpEndpoint(... │
└────────────┴────────────────────────┴──────┴─────────────────┘
```

### 3. Test the Server

#### Option A: Python Demo (Recommended for Natural Language)

The Python demo shows how to use both direct tool invocation and natural language queries:

```bash
# Install dependencies
pip install llama-stack-client fire termcolor

# Run all tests (direct + natural language)
python demo_math_mcp.py all

# Or run specific tests:
python demo_math_mcp.py direct                    # Test direct tool invocation
python demo_math_mcp.py natural                   # Test with default query
python demo_math_mcp.py natural --query "What is the square root of 256?"
```

**Natural language examples:**
```bash
# Test different math operations
python demo_math_mcp.py natural --query "What is 25 times 48?"
python demo_math_mcp.py natural --query "Calculate the square root of 144"
python demo_math_mcp.py natural --query "What is 1000 divided by 25?"
python demo_math_mcp.py natural --query "What is 2 to the power of 10?"
```

The demo will:
- ✅ Register the math-tools toolgroup
- ✅ List available tools
- ✅ Send natural language query to LLM
- ✅ Show which tool the LLM chooses to call
- ✅ Execute the tool on the MCP server
- ✅ Display the final answer

#### Option B: Basic Integration Test (Curl)

Run the automated test script:

```bash
./test_with_curl.sh
```

Or with a custom natural language query:

```bash
./test_with_curl.sh "What is 156 times 234?"
```

This script will:
- ✅ Verify Llama Stack is accessible
- ✅ List all registered toolgroups
- ✅ Show math-tools toolgroup details
- ✅ Test Math MCP Server connectivity
- ✅ Execute direct calculation tests
- ✅ Process natural language queries (if provided)

Expected output:
```
========================================
Math MCP Server + Llama Stack Integration Test
========================================

1. Verify Llama Stack is accessible:
"sentence-transformers/nomic-ai/nomic-embed-text-v1.5"

2. List registered toolgroups:
  - builtin::websearch (tavily-search)
  - builtin::rag (rag-runtime)
  - math-tools (model-context-protocol)

3. Get math-tools toolgroup details:
{
  "identifier": "math-tools",
  "provider_id": "model-context-protocol",
  ...
}

4. Test Math MCP Server directly (from within cluster):
Available tools: 8

5. Direct calculation test (156 × 234):
Result: 36504.0

6. Natural Language Query Test:
Query: 'What is 156 times 234?'
Using model: vllm/meta-llama/Llama-3.2-1B-Instruct
✅ Tool call detected!
Tool called: multiply
Arguments: {"a": 156, "b": 234}
MCP Server Result: 36504.0
✅ Natural language query successfully routed through MCP server!

Summary:
  ✅ Llama Stack is running
  ✅ Math toolgroup is registered
  ✅ Math MCP Server is operational
```

## API Reference

### Endpoints

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

#### GET /mcp/tools
List all available math tools in MCP-compatible format.

**Response:**
```json
{
  "tools": [
    {
      "name": "add",
      "description": "Add two numbers together",
      "inputSchema": {
        "type": "object",
        "properties": {
          "a": {"type": "number"},
          "b": {"type": "number"}
        },
        "required": ["a", "b"]
      }
    }
    // ... more tools
  ]
}
```

#### POST /calculate
Execute a math operation.

**Request:**
```json
{
  "operation": "multiply",
  "a": 156,
  "b": 234
}
```

**Response:**
```json
{
  "result": 36504.0,
  "message": "156.0 × 234.0 = 36504.0"
}
```

### Available Operations

| Operation | Parameters | Example |
|-----------|-----------|---------|
| add | `a`, `b` | `{"operation":"add","a":10,"b":5}` |
| subtract | `a`, `b` | `{"operation":"subtract","a":10,"b":5}` |
| multiply | `a`, `b` | `{"operation":"multiply","a":10,"b":5}` |
| divide | `a`, `b` | `{"operation":"divide","a":10,"b":5}` |
| power | `base`, `exponent` | `{"operation":"power","base":2,"exponent":8}` |
| sqrt | `value` | `{"operation":"sqrt","value":144}` |
| abs | `value` | `{"operation":"abs","value":-42}` |
| factorial | `n` | `{"operation":"factorial","n":5}` |

## Manual Testing Examples

### Test from Within Cluster

```bash
# Health check
kubectl run curl-test --rm -i --restart=Never --image=curlimages/curl -- \
  curl -s http://math-mcp-server.default.svc.cluster.local:8080/health

# List tools
kubectl run curl-test --rm -i --restart=Never --image=curlimages/curl -- \
  curl -s http://math-mcp-server.default.svc.cluster.local:8080/mcp/tools

# Test addition: 100 + 50
kubectl run curl-test --rm -i --restart=Never --image=curlimages/curl -- \
  curl -s -X POST http://math-mcp-server.default.svc.cluster.local:8080/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation":"add","a":100,"b":50}'

# Test square root: √625
kubectl run curl-test --rm -i --restart=Never --image=curlimages/curl -- \
  curl -s -X POST http://math-mcp-server.default.svc.cluster.local:8080/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation":"sqrt","value":625}'

# Test factorial: 10!
kubectl run curl-test --rm -i --restart=Never --image=curlimages/curl -- \
  curl -s -X POST http://math-mcp-server.default.svc.cluster.local:8080/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation":"factorial","n":10}'
```

#### Which Test Should I Use?

| Test Method | Use Case | Tool Calling |
|-------------|----------|--------------|
| **Python demo_math_mcp.py** | Full natural language + agentic behavior | ✅ Yes - LLM chooses tools |
| **Bash test_with_curl.sh** | Quick infrastructure validation | ⚠️ Partial - depends on model |
| **Manual curl commands** | Direct API testing, debugging | ❌ No - direct invocation |

**Recommendation**: Use the Python demo (`demo_math_mcp.py`) to see true natural language → MCP server integration with proper tool calling.

## Project Structure

```
math-mcp/
├── server.py                    # FastAPI server implementation
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container image definition
├── 00-math-mcp-deploy.yaml     # Kubernetes deployment manifest
├── 01-math-mcp-service.yaml    # Kubernetes service manifest
├── test_with_curl.sh            # Automated integration test (bash)
├── demo_math_mcp.py             # Natural language demo (Python)
└── README.md                    # This file
```

## Development

### Local Testing

Before deploying to Kubernetes, you can test the server locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run server locally
python server.py

# Test locally (in another terminal)
curl http://localhost:8080/health
curl http://localhost:8080/mcp/tools
curl -X POST http://localhost:8080/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation":"add","a":10,"b":5}'
```

### Rebuilding After Changes

```bash
# Rebuild image
docker build -t math-mcp-server:latest .

# Reload into Kind
kind load docker-image math-mcp-server:latest --name llama-stack-test

# Restart deployment
kubectl rollout restart deployment/math-mcp-server

# Check status
kubectl rollout status deployment/math-mcp-server
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl get pods -l app=math-mcp-server

# View logs
kubectl logs -l app=math-mcp-server

# Describe pod for events
kubectl describe pod -l app=math-mcp-server
```

**Common issues:**
- **ImagePullBackOff**: Image not loaded into Kind - run `kind load docker-image`
- **CrashLoopBackOff**: Check logs for Python errors

### Service Not Reachable

```bash
# Check service
kubectl get svc math-mcp-server

# Test connectivity from debug pod
kubectl run curl-test --rm -i --restart=Never --image=curlimages/curl -- \
  curl -v http://math-mcp-server.default.svc.cluster.local:8080/health
```

### Toolgroup Registration Issues

```bash
# Verify Llama Stack is accessible
curl http://localhost:8321/v1/models

# Check registered toolgroups
curl http://localhost:8321/v1/toolgroups | jq .

# Re-register if needed
llama-stack-client --endpoint http://localhost:8321 toolgroups register \
  math-tools \
  --provider-id model-context-protocol \
  --mcp-endpoint http://math-mcp-server.default.svc.cluster.local:8080
```

## Configuration

### Resource Limits

Edit `00-math-mcp-deploy.yaml` to adjust resource limits:

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
```

### Scaling

Increase replicas for high availability:

```bash
kubectl scale deployment math-mcp-server --replicas=3
```

### Adding New Operations

Edit `server.py` to add new math functions:

1. Add operation handler in the `calculate()` function
2. Rebuild and redeploy
3. Test the new operation

## Implementation Details

### Why FastAPI Instead of MCP SDK?

The current MCP Python SDK (v1.26.0) is designed primarily for stdio (local) transport. HTTP/SSE transport support is still evolving. This implementation uses FastAPI to:

1. **Provide HTTP endpoints** - Works reliably in Kubernetes
2. **MCP-compatible tool listings** - `/mcp/tools` endpoint follows MCP schema
3. **Simple testing** - Easy to test with curl or any HTTP client
4. **Production-ready** - Built on mature FastAPI/Uvicorn stack

### Security Considerations

For production use, consider adding:
- Authentication/authorization (API keys, OAuth)
- Rate limiting
- Network policies to restrict access
- TLS/HTTPS termination
- Input validation (already implemented for edge cases)

## Use as a Template

This Math MCP Server demonstrates the complete pattern for building LLM tool servers. Use it as a template for:

- **Weather API integration** - Connect to weather services
- **Database query tools** - Execute SQL queries safely
- **File system operations** - Read/write files with permissions
- **Custom business logic** - Implement domain-specific tools
- **External service integration** - Connect to any HTTP API

The architecture is proven and production-ready.

## Clean Up

```bash
# Delete Kubernetes resources
kubectl delete -f 01-math-mcp-service.yaml
kubectl delete -f 00-math-mcp-deploy.yaml

# Remove Docker image
docker rmi math-mcp-server:latest
```

## Related Documentation

- [Main Kubernetes Deployment Guide](../../README.md) - Llama Stack and vLLM setup
- [Llama Stack Documentation](https://llamastack.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Model Context Protocol](https://modelcontextprotocol.io)
