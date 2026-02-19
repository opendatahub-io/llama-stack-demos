"""
Demo: Tool Runtime API

Description:
This demo teaches how to use the Llama Stack tool runtime APIs to register, list, and invoke tools directly
without using agents or MCP servers.

Learning Objectives:
- Register toolgroups using built-in providers
- List available tools using tool_runtime.list_tools()
- Invoke tools directly using tool_runtime.invoke_tool()
- Understand the difference between tool runtime API and agent-based tool usage
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


def main(
    host: str,
    port: int,
):
    """
    Demonstrate tool runtime APIs: toolgroups.register, tool_runtime.list_tools, and tool_runtime.invoke_tool
    """
    client = LlamaStackClient(base_url=f"http://{host}:{port}")

    print(colored("\n=== Step 1: Check Available Tool Runtime Providers ===", "green"))
    # List providers that support tool_runtime API
    providers = [p for p in client.providers.list() if p.api == "tool_runtime"]
    if providers:
        print("Available tool runtime providers:")
        for provider in providers:
            print(f"  - {provider.provider_id} (API: {provider.api})")
    else:
        print(colored("No tool runtime providers found.", "yellow"))

    print(colored("\n=== Step 2: List Registered Tools (tools.list()) ===", "green"))
    print("API: client.tools.list() - Lists tools registered on the server via toolgroups.register()")
    print("Use case: Check what toolgroups are registered, get toolgroup IDs for agent configuration")
    # Check if there are any existing toolgroups
    try:
        registered_tools = client.tools.list()
        if registered_tools:
            toolgroups = set(t.toolgroup_id for t in registered_tools if t.toolgroup_id)
            print(f"\nRegistered toolgroups: {toolgroups if toolgroups else 'None'}")
            print(f"Registered tools ({len(registered_tools)}):")
            for tool in registered_tools:
                print(f"  - {tool.name} (toolgroup: {tool.toolgroup_id})")
        else:
            print("No tools currently registered.")
    except Exception as exc:
        print(colored(f"Failed to list tools: {exc}", "yellow"))

    print(colored("\n=== Step 3: List Runtime Tools (tool_runtime.list_tools()) ===", "green"))
    print("API: client.tool_runtime.list_tools() - Lists tools available in the runtime")
    print("Use case: Get detailed tool info for invocation, can query MCP endpoints without registration")
    print("Key difference: Can pass mcp_endpoint parameter to query external endpoints directly!")
    # Use tool_runtime API to list tools
    try:
        tools = client.tool_runtime.list_tools()
        print(f"\nTools available via tool_runtime ({len(tools)}):")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description or 'No description'}")
            if hasattr(tool, 'parameters') and tool.parameters:
                print(f"    Parameters: {tool.parameters}")
    except Exception as exc:
        print(colored(f"Failed to list tools via tool_runtime: {exc}", "yellow"))
        tools = []

    print(colored("\n=== Step 4: Invoke a Tool Using tool_runtime.invoke_tool() ===", "green"))
    # Demonstrate direct tool invocation if any tools are available
    if tools:
        # Try to find a simple tool to invoke
        # Common built-in tools: web_search, knowledge_search, insert_into_memory, code_interpreter
        invokable_tools = [
            ("web_search", {"query": "What is Llama Stack?"}),
            ("knowledge_search", {"query": "Llama Stack"}),
            ("code_interpreter", {"code": "print(2 + 2)"}),
            ("brave_search", {"query": "Llama Stack"}),
            ("wolfram_alpha", {"query": "2+2"}),
        ]

        tool_invoked = False
        for tool_name, test_kwargs in invokable_tools:
            matching_tools = [t for t in tools if tool_name == t.name or tool_name in t.name.lower()]
            if matching_tools:
                tool = matching_tools[0]
                print(f"\nInvoking tool: {tool.name}")
                print(f"  Description: {tool.description or 'No description'}")
                print(f"  Parameters: {test_kwargs}")
                try:
                    result = client.tool_runtime.invoke_tool(
                        tool_name=tool.name,
                        kwargs=test_kwargs,
                    )
                    print(colored(f"  ✓ Success! Result:", "green"))
                    # Pretty print result (truncate if too long)
                    result_str = str(result)
                    if len(result_str) > 500:
                        print(colored(f"    {result_str[:500]}...", "cyan"))
                    else:
                        print(colored(f"    {result_str}", "cyan"))
                    tool_invoked = True
                    break
                except Exception as exc:
                    print(colored(f"  ✗ Failed to invoke {tool.name}: {exc}", "yellow"))

        if not tool_invoked:
            print(colored(
                "\nNo invokable tools found or all invocations failed.",
                "yellow"
            ))
            print(colored(
                "To see tool invocation in action, you can:",
                "yellow"
            ))
            print(colored(
                "  1. Configure your Llama Stack server with built-in tools (e.g., code_interpreter, web_search)",
                "yellow"
            ))
            print(colored(
                "  2. Or see demo 08_mcp_tools.py for MCP-based tool registration and invocation",
                "yellow"
            ))
    else:
        print(colored("No tools available to invoke.", "yellow"))
        print(colored(
            "\nNote: This demo shows the tool runtime API structure.",
            "yellow"
        ))
        print(colored(
            "For a working example with actual tool invocation, see demo 08_mcp_tools.py",
            "yellow"
        ))

    print(colored("\n=== Step 5: Register a Toolgroup (Example) ===", "green"))
    print("To register a toolgroup, you typically need a provider.")
    print("Example with inline provider:")
    print(colored("""
    # For built-in tools (requires appropriate provider):
    client.toolgroups.register(
        toolgroup_id="my-custom-tools",
        provider_id="inline",  # or another supported provider
        # provider-specific configuration here
    )

    # For more advanced examples, see:
    # - demo 08_mcp_tools.py for MCP-based registration
    # - Your Llama Stack server configuration for available providers
    """, "cyan"))

    print(colored("\n=== Summary ===", "green"))
    print("Key APIs demonstrated:")
    print("  1. client.providers.list() - Find available tool runtime providers")
    print("  2. client.tools.list() - List registered tools and toolgroups (server registry)")
    print("  3. client.tool_runtime.list_tools() - List runtime tools (can query external endpoints)")
    print("  4. client.tool_runtime.invoke_tool() - Directly invoke tools")
    print("  5. client.toolgroups.register() - Register new toolgroups (requires provider)")

    print(colored("\nKey Difference Between tools.list() and tool_runtime.list_tools():", "yellow"))
    print("  • tools.list():")
    print("    - Lists tools registered on the server via toolgroups.register()")
    print("    - Returns toolgroup metadata (toolgroup_id, identifier)")
    print("    - Used for: checking registration status, configuring agents")
    print("  • tool_runtime.list_tools():")
    print("    - Lists tools available in the runtime for execution")
    print("    - Can query external MCP endpoints WITHOUT registration: list_tools(mcp_endpoint={...})")
    print("    - Returns detailed tool info (name, description, parameters)")
    print("    - Used for: tool invocation, discovering tool parameters, querying remote endpoints")


if __name__ == "__main__":
    fire.Fire(main)
