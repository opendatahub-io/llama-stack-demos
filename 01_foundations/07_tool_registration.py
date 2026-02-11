"""
Demo: Tool Registration

Description:
This demo teaches how to register and use custom client-side tools with agents for function calling capabilities.

Learning Objectives:
- Register custom Python functions as agent tools
- Create agents with tool-calling capabilities
- Handle tool execution during agent conversations
- Differentiate between client-side and server-side tools
"""

# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from __future__ import annotations

import os

import fire
from termcolor import colored

from client_tools.ticker_data import get_ticker_data
from client_tools.web_search import WebSearchTool
from client_tools.calculator import calculator

from llama_stack_client import LlamaStackClient, Agent, AgentEventLogger

from shared.utils import can_model_chat, check_model_is_available, get_any_available_chat_model


def main(
    host: str,
    port: int,
    model_id: str | None = None,
    list_server_tools: bool = False,
):
    client = LlamaStackClient(base_url=f"http://{host}:{port}")

    api_key = ""
    engine = "tavily"
    if "TAVILY_SEARCH_API_KEY" in os.environ:
        api_key = os.getenv("TAVILY_SEARCH_API_KEY")
    elif "BRAVE_SEARCH_API_KEY" in os.environ:
        api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        engine = "brave"
    else:
        print(
            colored(
                "Warning: TAVILY_SEARCH_API_KEY or BRAVE_SEARCH_API_KEY is not set; Web search will not work",
                "yellow",
            )
        )

    if model_id is None:
        model_id = get_any_available_chat_model(client)
        if model_id is None:
            return
    else:
        if not check_model_is_available(client, model_id):
            return
        if not can_model_chat(client, model_id):
            print(
                colored(
                    f"Model `{model_id}` does not support chat. Choose a chat-capable model.",
                    "red",
                )
            )
            return

    # Register tools by passing them to the Agent constructor.
    # These tools are available to this agent instance during inference.
    tools = [
        calculator,
        get_ticker_data,
    ]
    if api_key:
        tools.append(WebSearchTool(engine, api_key))
    agent = Agent(
        client,
        model=model_id,
        instructions="You are a helpful assistant. Use tools when they are relevant.",
        tools=tools,
    )

    print("Registered tools for this agent:")
    for tool in tools:
        tool_name = getattr(tool, "name", None) or getattr(tool, "__name__", None) or str(tool)
        print(f"- {tool_name}")

    if list_server_tools:
        # Server-side tool registry (if enabled) is separate from client-side tools.
        # Client tools registered above will not appear in this list.
        try:
            tool_list = client.tools.list()
            print("Server-side tools:")
            for tool_def in tool_list:
                print(f"- {tool_def.name}")
        except Exception as exc:
            print(colored(f"Failed to list server tools: {exc}", "yellow"))

    session_id = agent.create_session("tool-registration-session")
    print(f"Created session_id={session_id}")

    user_prompts = [
        "What was the closing price of GOOG for 2023?",
        "Who was the 42nd president of the United States?",
        "What is 40+30?",
    ]
    for prompt in user_prompts:
        print(colored(f"User> {prompt}", "cyan"))
        response = agent.create_turn(
            messages=[{"role": "user", "content": prompt}],
            session_id=session_id,
        )

        for printable in AgentEventLogger().log(response):
            print(printable, end="", flush=True)


if __name__ == "__main__":
    fire.Fire(main)
