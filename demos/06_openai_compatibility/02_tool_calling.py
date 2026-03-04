"""
Demo: OpenAI-Compatible Tool Calling

Description:
This demo shows the standard OpenAI function-calling flow against a
Llama Stack server: define tools, let the model request a call, execute
locally, and send results back.

Learning Objectives:
- Define OpenAI-style function tools
- Parse tool_calls from the model response
- Execute a local function and return the result
- Complete the full 3-step tool-calling loop
"""

# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from __future__ import annotations

import json
import os
import sys

import fire
from openai import OpenAI
from termcolor import colored

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.utils import resolve_openai_model

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None


def _maybe_load_dotenv() -> None:
    if load_dotenv is not None:
        load_dotenv()


# -- Simulated local tool --------------------------------------------------

WEATHER_DATA = {
    "san francisco": {"temperature": "62°F", "condition": "Foggy"},
    "new york": {"temperature": "45°F", "condition": "Cloudy"},
    "london": {"temperature": "50°F", "condition": "Rainy"},
}


def get_weather(location: str) -> str:
    """Return simulated weather for a given location."""
    data = WEATHER_DATA.get(location.lower())
    if data is None:
        return json.dumps({"error": f"No weather data for {location}"})
    return json.dumps(data)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g. 'San Francisco'",
                    },
                },
                "required": ["location"],
            },
        },
    },
]

TOOL_MAP = {
    "get_weather": get_weather,
}


def main(
    host: str,
    port: int,
    model_id: str | None = None,
    prompt: str = "What is the weather like in San Francisco?",
    scheme: str = "http",
) -> None:
    _maybe_load_dotenv()

    if scheme not in {"http", "https"}:
        raise ValueError("scheme must be 'http' or 'https'")
    if host not in {"localhost", "127.0.0.1", "::1"} and scheme != "https":
        print(colored("Warning: using HTTP for a non-local host. Consider --scheme https.", "yellow"))

    client = OpenAI(
        base_url=f"{scheme}://{host}:{port}/v1",
        api_key=os.getenv("LLAMA_STACK_API_KEY", "fake"),
    )

    resolved_model = resolve_openai_model(client, model_id)
    if resolved_model is None:
        return
    print(f"Using model: {resolved_model}")

    # Step 1 — send the user message with tool definitions
    messages = [{"role": "user", "content": prompt}]
    print(colored(f"User> {prompt}", "blue"))

    response = client.chat.completions.create(
        model=resolved_model,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message

    # If the model replies directly without calling a tool, print and exit.
    if not assistant_message.tool_calls:
        print(colored(f"Assistant> {assistant_message.content}", "green"))
        return

    # Step 2 — execute each requested tool call locally
    messages.append(assistant_message)
    for tool_call in assistant_message.tool_calls:
        fn_name = tool_call.function.name
        try:
            fn_args = json.loads(tool_call.function.arguments or "{}")
            if not isinstance(fn_args, dict):
                raise ValueError("arguments must be a JSON object")
        except (json.JSONDecodeError, ValueError) as exc:
            result = json.dumps({"error": f"Invalid arguments for {fn_name}: {exc}"})
            print(colored(f"Tool result: {result}", "yellow"))
            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": result}
            )
            continue
        print(colored(f"Tool call: {fn_name}({fn_args})", "yellow"))

        fn = TOOL_MAP.get(fn_name)
        if fn is None:
            result = json.dumps({"error": f"Unknown function: {fn_name}"})
        else:
            try:
                result = fn(**fn_args)
            except TypeError as exc:
                result = json.dumps({"error": f"Invalid parameters for {fn_name}: {exc}"})
        print(colored(f"Tool result: {result}", "yellow"))

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
        )

    # Step 3 — send tool results back and get the final answer
    final = client.chat.completions.create(
        model=resolved_model,
        messages=messages,
        tools=TOOLS,
    )
    print(colored(f"Assistant> {final.choices[0].message.content}", "green"))


if __name__ == "__main__":
    fire.Fire(main)
