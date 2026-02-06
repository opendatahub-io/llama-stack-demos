"""
Demo: Client Setup

Description:
This demo teaches the fundamentals of setting up and connecting to a Llama Stack server using the LlamaStackClient.

Learning Objectives:
- Initialize a LlamaStackClient with a specific host and port
- Perform a health check to verify server connectivity
- Handle connection failures gracefully
"""

# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from __future__ import annotations

import fire
from llama_stack_client import LlamaStackClient

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None


def _maybe_load_dotenv() -> None:
    if load_dotenv is not None:
        load_dotenv()


def main(host: str, port: int) -> None:
    _maybe_load_dotenv()

    client = LlamaStackClient(base_url=f"http://{host}:{port}")
    try:
        health = client.inspect.health()
    except Exception as exc:
        print(f"Health check failed: {exc}")
        return
    if hasattr(health, "model_dump"):
        print(health.model_dump())
    else:
        print(health)


if __name__ == "__main__":
    fire.Fire(main)
