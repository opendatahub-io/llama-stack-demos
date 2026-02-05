"""
Demo: MCP Tools

Description:
This demo teaches how to set up and use Model Context Protocol (MCP) servers to expose tools to Llama Stack.

Learning Objectives:
- Start an MCP server with custom tools
- Register MCP endpoints as toolgroups with Llama Stack
- Invoke remote MCP tools through the tool runtime
- Manage toolgroup lifecycle (register, use, unregister)
"""

# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from __future__ import annotations

import fire
from termcolor import colored

from llama_stack_client import LlamaStackClient


def serve() -> None:
    """
    Start a local MCP server that exposes a simple add(a, b) tool.
    """
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception:  # pragma: no cover - optional dependency
        print(
            colored(
                "Missing dependency 'mcp'. Install with: pip install mcp",
                "red",
            )
        )
        return

    mcp = FastMCP("PlusServer")

    @mcp.tool()
    def add(a: int, b: int) -> int:
        """Return a + b."""
        return a + b

    print("Starting MCP server on http://localhost:8000/sse")
    mcp.run(transport="sse")


def _get_toolgroup_provider(client: LlamaStackClient, provider_id: str | None):
    providers = [p for p in client.providers.list() if p.api in ("tool_runtime")]
    if not providers:
        print(colored("No toolgroup providers found. Skipping registration.", "yellow"))
        return None
    if provider_id is None:
        for provider in providers:
            if provider.provider_id == "model-context-protocol":
                return provider
    for provider in providers:
        if provider.provider_id == provider_id:
            return provider
    available = [provider.provider_id for provider in providers]
    print(colored(f"Provider `{provider_id}` not found. Available: {available}", "red"))
    return None


def run(
    host: str,
    port: int,
    mcp_endpoint: str = "http://localhost:8000/sse",
    toolgroup_id: str = "plus-tools",
    provider_id: str | None = None,
    tool_name: str = "add",
    a: int = 1,
    b: int = 1,
) -> None:
    """
    Register an MCP toolgroup and invoke the add tool.
    """
    client = LlamaStackClient(base_url=f"http://{host}:{port}")
    provider = _get_toolgroup_provider(client, provider_id)
    if provider is not None:
        # Register the MCP server as a toolgroup with the Llama Stack server.
        client.toolgroups.register(
            provider_id=provider.provider_id,
            toolgroup_id=toolgroup_id,
            mcp_endpoint={"uri": mcp_endpoint},
        )
        print(f"Registered toolgroup '{toolgroup_id}' -> {mcp_endpoint}")
    else:
        print("Continuing without server-side toolgroup registration.")

    # List tools exposed by the MCP server.
    tools = client.tool_runtime.list_tools(mcp_endpoint={"uri": mcp_endpoint})
    tool_names = [tool.name for tool in tools]
    print(f"Available MCP tools: {tool_names}")

    if tool_name not in tool_names:
        print(colored(f"Tool '{tool_name}' not found in MCP tools.", "red"))
        print(
            colored(
                "Hint: your Llama Stack server may be ignoring the MCP endpoint and returning its own tools. "
                "Ensure the server is configured with an MCP-capable toolgroup provider, "
                "or point to a server that supports remote MCP endpoints.",
                "yellow",
            )
        )
        return

    # Invoke the MCP tool through the server-side runtime.
    result = client.tool_runtime.invoke_tool(
        tool_name=tool_name,
        kwargs={"a": a, "b": b},
    )
    print(f"{tool_name}({a}, {b}) -> {result}")

    # Unregister the MCP toolgroup from the Llama Stack server.
    client.toolgroups.unregister(toolgroup_id=toolgroup_id)
    print(f"Unregistered toolgroup '{toolgroup_id}'")


if __name__ == "__main__":
    fire.Fire({"serve": serve, "run": run})
