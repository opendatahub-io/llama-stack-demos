"""
Demo: OpenAI-Compatible Responses API

Description:
This demo uses the OpenAI SDK's Responses API (client.responses.create)
against a Llama Stack server, proving OpenResponses compatibility.

Learning Objectives:
- Call the Responses API via the OpenAI Python SDK
- Use both a plain string input and a structured message list
- See how Llama Stack implements the OpenAI Responses API
"""

# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from __future__ import annotations

import os
import sys

import fire
from openai import OpenAI
from termcolor import colored

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.utils import resolve_openai_model

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None


def _maybe_load_dotenv() -> None:
    if load_dotenv is not None:
        load_dotenv()


def main(
    host: str,
    port: int,
    model_id: str | None = None,
) -> None:
    _maybe_load_dotenv()

    client = OpenAI(
        base_url=f"http://{host}:{port}/v1",
        api_key=os.getenv("LLAMA_STACK_API_KEY", "fake"),
    )

    resolved_model = resolve_openai_model(client, model_id)
    if resolved_model is None:
        return
    print(f"Using model: {resolved_model}")

    # --- Example 1: plain string input ---
    print(colored("\n--- String input ---", "cyan"))
    response = client.responses.create(
        model=resolved_model,
        input="Give a one-sentence description of Llama Stack.",
    )
    print(response.output_text)

    # --- Example 2: structured message-list input ---
    print(colored("\n--- Structured message-list input ---", "cyan"))
    response = client.responses.create(
        model=resolved_model,
        input=[
            {
                "role": "user",
                "content": "List three benefits of running open-source LLMs locally.",
            },
        ],
    )
    print(response.output_text)


if __name__ == "__main__":
    fire.Fire(main)
