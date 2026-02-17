#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

"""
Demo: Agent Routing

Description:
This demo teaches how to coordinate multiple specialized agents to handle complex multi-step tasks through routing.

Learning Objectives:
- Create multiple specialized agents for different domains
- Implement task routing logic to select appropriate agents
- Coordinate agents to solve multi-faceted problems
- Synthesize results from multiple agent executions
"""

import os

import fire
from termcolor import colored

from demos.client_tools.calculator import calculator
from demos.client_tools.ticker_data import get_ticker_data
from demos.client_tools.web_search import WebSearchTool
from llama_stack_client import Agent, LlamaStackClient

from demos.shared.utils import can_model_chat, check_model_is_available, get_any_available_chat_model


def _resolve_web_tool():
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
                "Warning: TAVILY_SEARCH_API_KEY or BRAVE_SEARCH_API_KEY is not set; web tool disabled.",
                "yellow",
            )
        )
        return None
    return WebSearchTool(engine, api_key)


def _route_subtask(prompt: str, web_available: bool) -> str:
    lower_prompt = prompt.lower()
    if any(token in lower_prompt for token in ["update", "recent", "release", "news", "search", "find"]):
        return "research" if web_available else "general"
    if any(token in lower_prompt for token in ["stock", "ticker", "price", "market"]):
        return "finance"
    if any(token in lower_prompt for token in ["calculate", "sum", "math"]):
        return "math"
    if any(char.isdigit() for char in lower_prompt) and any(
        token in lower_prompt for token in ["+", "-", "*", "/"]
    ):
        return "math"
    if any(token in lower_prompt for token in ["latest", "who", "when"]):
        return "research" if web_available else "general"
    return "general"


def _extract_output(response) -> str:
    if isinstance(response, tuple):
        response = response[0]
    return response.output_text or str(response.output)


def main(host: str, port: int, model_id: str | None = None):
    client = LlamaStackClient(base_url=f"http://{host}:{port}")

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

    web_tool = _resolve_web_tool()
    web_available = web_tool is not None

    agents = {
        "general": Agent(
            client,
            model=model_id,
            instructions="You are a helpful assistant.",
        ),
        "research": Agent(
            client,
            model=model_id,
            instructions="You are a research assistant. Use web search when helpful.",
            tools=[web_tool] if web_tool is not None else [],
        ),
        "math": Agent(
            client,
            model=model_id,
            instructions="You are a math assistant. Use tools for calculations.",
            tools=[calculator],
        ),
        "finance": Agent(
            client,
            model=model_id,
            instructions="You are a finance assistant. Use tools for ticker data.",
            tools=[get_ticker_data],
        ),
    }
    sessions = {name: agent.create_session(f"coordination-{name}") for name, agent in agents.items()}

    task = (
        "Prepare a brief update for a product manager: "
        "1) Find a recent Llama Stack update. "
        "2) Compute 45 * 12 / 6. "
        "3) Get the closing price of GOOG for 2023."
    )
    subtasks = [
        "Find a recent Llama Stack update and summarize it in one sentence.",
        "Compute 45 * 12 / 6.",
        "What was the closing price of GOOG for 2023?",
    ]

    print(colored(f"[task] {task}", "cyan"))
    subtask_results: list[str] = []
    for subtask in subtasks:
        route = _route_subtask(subtask, web_available)
        agent = agents[route]
        session_id = sessions[route]
        print(colored(f"[coordination] {subtask} -> {route}", "blue"))
        response = agent.create_turn(
            messages=[{"role": "user", "content": subtask}],
            session_id=session_id,
            stream=False,
        )
        text_output = _extract_output(response)
        subtask_results.append(f"- {subtask}\n  Result: {text_output}")
        print(text_output)

    synthesis = (
        "Synthesize the following subtask results into a concise update:\n\n"
        + "\n\n".join(subtask_results)
    )
    coordinator = agents["general"]
    coordinator_session = sessions["general"]
    print(colored("[coordination] synthesizing final response", "green"))
    final_response = coordinator.create_turn(
        messages=[{"role": "user", "content": synthesis}],
        session_id=coordinator_session,
        stream=False,
    )
    print(_extract_output(final_response))


if __name__ == "__main__":
    fire.Fire(main)
