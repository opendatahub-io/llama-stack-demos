#!/usr/bin/env python3
"""
Math MCP Server - Simple HTTP version
A basic HTTP server that exposes math operations and MCP-compatible endpoints.
"""

import math
import logging
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Math MCP Server", version="1.0.0")


# Request/Response models
class MathOperation(BaseModel):
    operation: str
    a: float = None
    b: float = None
    value: float = None
    base: float = None
    exponent: float = None
    n: int = None


class MathResult(BaseModel):
    result: Any
    message: str


class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: Dict


# MCP Protocol Models
class MCPListToolsResponse(BaseModel):
    tools: List[MCPTool]


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "Math MCP Server",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "mcp_tools": "/mcp/tools",
            "calculate": "/calculate"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools (MCP protocol compatible)"""
    tools = [
        MCPTool(
            name="add",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        MCPTool(
            name="subtract",
            description="Subtract second number from first number",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number to subtract"},
                },
                "required": ["a", "b"],
            },
        ),
        MCPTool(
            name="multiply",
            description="Multiply two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        MCPTool(
            name="divide",
            description="Divide first number by second number",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Numerator"},
                    "b": {"type": "number", "description": "Denominator (cannot be zero)"},
                },
                "required": ["a", "b"],
            },
        ),
        MCPTool(
            name="power",
            description="Raise first number to the power of second number",
            inputSchema={
                "type": "object",
                "properties": {
                    "base": {"type": "number", "description": "Base number"},
                    "exponent": {"type": "number", "description": "Exponent"},
                },
                "required": ["base", "exponent"],
            },
        ),
        MCPTool(
            name="sqrt",
            description="Calculate square root of a number",
            inputSchema={
                "type": "object",
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "Number to calculate square root of (must be non-negative)",
                    },
                },
                "required": ["value"],
            },
        ),
        MCPTool(
            name="abs",
            description="Calculate absolute value of a number",
            inputSchema={
                "type": "object",
                "properties": {
                    "value": {"type": "number", "description": "Number to calculate absolute value of"},
                },
                "required": ["value"],
            },
        ),
        MCPTool(
            name="factorial",
            description="Calculate factorial of a non-negative integer",
            inputSchema={
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "Non-negative integer to calculate factorial of"},
                },
                "required": ["n"],
            },
        ),
    ]

    return MCPListToolsResponse(tools=tools)


@app.post("/calculate")
async def calculate(op: MathOperation) -> MathResult:
    """Execute a math operation"""
    try:
        operation = op.operation.lower()

        if operation == "add":
            if op.a is None or op.b is None:
                raise HTTPException(status_code=400, detail="Parameters 'a' and 'b' are required")
            result = op.a + op.b
            return MathResult(result=result, message=f"{op.a} + {op.b} = {result}")

        elif operation == "subtract":
            if op.a is None or op.b is None:
                raise HTTPException(status_code=400, detail="Parameters 'a' and 'b' are required")
            result = op.a - op.b
            return MathResult(result=result, message=f"{op.a} - {op.b} = {result}")

        elif operation == "multiply":
            if op.a is None or op.b is None:
                raise HTTPException(status_code=400, detail="Parameters 'a' and 'b' are required")
            result = op.a * op.b
            return MathResult(result=result, message=f"{op.a} × {op.b} = {result}")

        elif operation == "divide":
            if op.a is None or op.b is None:
                raise HTTPException(status_code=400, detail="Parameters 'a' and 'b' are required")
            if op.b == 0:
                raise HTTPException(status_code=400, detail="Division by zero is not allowed")
            result = op.a / op.b
            return MathResult(result=result, message=f"{op.a} ÷ {op.b} = {result}")

        elif operation == "power":
            if op.base is None or op.exponent is None:
                raise HTTPException(status_code=400, detail="Parameters 'base' and 'exponent' are required")
            result = op.base ** op.exponent
            return MathResult(result=result, message=f"{op.base} ^ {op.exponent} = {result}")

        elif operation == "sqrt":
            if op.value is None:
                raise HTTPException(status_code=400, detail="Parameter 'value' is required")
            if op.value < 0:
                raise HTTPException(status_code=400, detail="Cannot calculate square root of negative number")
            result = math.sqrt(op.value)
            return MathResult(result=result, message=f"√{op.value} = {result}")

        elif operation == "abs":
            if op.value is None:
                raise HTTPException(status_code=400, detail="Parameter 'value' is required")
            result = abs(op.value)
            return MathResult(result=result, message=f"|{op.value}| = {result}")

        elif operation == "factorial":
            if op.n is None:
                raise HTTPException(status_code=400, detail="Parameter 'n' is required")
            if op.n < 0:
                raise HTTPException(status_code=400, detail="Factorial is only defined for non-negative integers")
            result = math.factorial(op.n)
            return MathResult(result=result, message=f"{op.n}! = {result}")

        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {operation}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing {operation}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error executing operation: {str(e)}")


@app.get("/sse")
async def sse_endpoint():
    """SSE endpoint placeholder for MCP protocol"""
    return {
        "message": "MCP SSE transport not yet implemented",
        "alternative": "Use /mcp/tools to list tools and /calculate to execute operations"
    }


if __name__ == "__main__":
    logger.info("Starting Math MCP Server on port 8080")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
