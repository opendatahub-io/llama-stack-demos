# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

import asyncio
import json
from typing import Dict, Any

import httpx
import requests

from llama_stack_client.lib.agents.client_tool import ClientTool


class BraveSearch:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def search(self, query: str) -> str:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "X-Subscription-Token": self.api_key,
            "Accept-Encoding": "gzip",
            "Accept": "application/json",
        }
        payload = {"q": query}
        response = requests.get(url=url, params=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return json.dumps(self._clean_brave_response(response.json()))

    def _clean_brave_response(self, search_response, top_k=3):
        query = None
        clean_response = []
        if "query" in search_response:
            if "original" in search_response["query"]:
                query = search_response["query"]["original"]
        if "mixed" in search_response:
            mixed_results = search_response["mixed"]
            for m in mixed_results["main"][:top_k]:
                r_type = m["type"]
                results = search_response[r_type]["results"]
                if r_type == "web":
                    # For web data - add a single output from the search
                    idx = m["index"]
                    selected_keys = [
                        "type",
                        "title",
                        "url",
                        "description",
                        "date",
                        "extra_snippets",
                    ]
                    cleaned = {
                        k: v for k, v in results[idx].items() if k in selected_keys
                    }
                elif r_type == "faq":
                    # For FAQ data - take a list of all the questions & answers
                    selected_keys = ["type", "question", "answer", "title", "url"]
                    cleaned = []
                    for q in results:
                        cleaned.append(
                            {k: v for k, v in q.items() if k in selected_keys}
                        )
                elif r_type == "infobox":
                    idx = m["index"]
                    selected_keys = [
                        "type",
                        "title",
                        "url",
                        "description",
                        "long_desc",
                    ]
                    cleaned = {
                        k: v for k, v in results[idx].items() if k in selected_keys
                    }
                elif r_type == "videos":
                    selected_keys = [
                        "type",
                        "url",
                        "title",
                        "description",
                        "date",
                    ]
                    cleaned = []
                    for q in results:
                        cleaned.append(
                            {k: v for k, v in q.items() if k in selected_keys}
                        )
                elif r_type == "locations":
                    # For location data - take a list of all the locations
                    selected_keys = [
                        "type",
                        "title",
                        "url",
                        "description",
                        "coordinates",
                        "postal_address",
                        "contact",
                        "rating",
                        "distance",
                        "zoom_level",
                    ]
                    cleaned = []
                    for q in results:
                        cleaned.append(
                            {k: v for k, v in q.items() if k in selected_keys}
                        )
                elif r_type == "news":
                    # For news data - take a list of all the news articles
                    selected_keys = [
                        "type",
                        "title",
                        "url",
                        "description",
                    ]
                    cleaned = []
                    for q in results:
                        cleaned.append(
                            {k: v for k, v in q.items() if k in selected_keys}
                        )
                else:
                    cleaned = []

                clean_response.append(cleaned)

        return {"query": query, "top_k": clean_response}


class TavilySearch:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def search(self, query: str) -> str:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running — safe to use asyncio.run()
            return asyncio.run(self.asearch(query))
        raise RuntimeError(
            "TavilySearch.search() cannot be called from within a running event loop. "
            "Use await TavilySearch.asearch() instead."
        )

    async def asearch(self, query: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={"api_key": self.api_key, "query": query},
            )
            response.raise_for_status()

        return json.dumps(self._cleanup_response(response.json()))

    def _cleanup_response(self, search_response, top_k=3):
        return {
            "query": search_response["query"],
            "top_k": search_response["results"][:top_k],
        }


class WebSearchTool(ClientTool):
    """Tool to search web for queries"""

    def __init__(self, engine: str, api_key: str):
        self.api_key = api_key
        assert engine in ["brave", "tavily"], (
            "Invalid engine, use one of brave or tavily"
        )
        if engine == "brave":
            self.engine = BraveSearch(api_key)
        else:
            self.engine = TavilySearch(api_key)

    def get_name(self) -> str:
        return "web_search"

    def get_description(self) -> str:
        return "Search the web for a given query"

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for",
                }
            },
            "required": ["query"],
        }

    def run_impl(self, query: str):
        return self.engine.search(query)

    async def async_run_impl(self, query: str):
        if hasattr(self.engine, "asearch"):
            return await self.engine.asearch(query)
        return self.engine.search(query)
