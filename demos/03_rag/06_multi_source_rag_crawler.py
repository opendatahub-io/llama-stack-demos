"""
Demo: Multi-Source RAG Crawler

Description:
This demo teaches how to build a cross-source document crawler that follows
links between different platforms (GitHub, web pages) and indexes all discovered
documents into a Llama Stack vector store for RAG queries.

Most RAG examples index documents from a single source. In practice, knowledge
is spread across platforms -- a GitHub README links to a design doc, which links
to an issue tracker, which references another repo. This demo shows how to
automatically discover and index that connected knowledge graph.

Learning Objectives:
- Detect and extract links to different platforms from document content
- Crawl documents breadth-first with configurable depth limits
- Track crawl provenance (which document linked to which)
- Index crawled documents into Llama Stack vector stores with metadata
- Query across all discovered documents with file_search
- Use incremental indexing with content hashing to avoid re-processing
"""

# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from __future__ import annotations

import hashlib
import re
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO
from typing import Callable
from uuid import uuid4

import fire
from llama_stack_client import LlamaStackClient
from termcolor import colored

from demos.shared.utils import (
    can_model_chat,
    check_model_is_available,
    get_any_available_chat_model,
    get_any_available_embedding_model,
    get_embedding_dimension,
)

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None

try:
    import requests as _requests
except ImportError:  # pragma: no cover - optional dependency
    _requests = None


def _maybe_load_dotenv() -> None:
    if load_dotenv is not None:
        load_dotenv()


# ---------------------------------------------------------------------------
# Link Detection
# ---------------------------------------------------------------------------


class LinkType(str, Enum):
    """Supported link/source types for crawling."""

    GITHUB = "github"
    WEB = "web"


@dataclass
class DetectedLink:
    """A link detected in document content."""

    link_type: LinkType
    identifier: str  # Source-specific ID (e.g. "owner/repo:path" for GitHub)
    url: str  # Original URL that matched


# Regex patterns for detecting links to different platforms.
# Extend this dict to support additional sources (GitLab, Confluence, Jira, etc.).
LINK_PATTERNS: dict[LinkType, re.Pattern] = {
    LinkType.GITHUB: re.compile(
        r"https?://github\.com/([^/\s]+/[^/\s]+)(?:/(?:blob|tree)/[^/\s]+/([^\s)\"<>]*))?",
        re.IGNORECASE,
    ),
    LinkType.WEB: re.compile(
        r"https?://[^\s)\"<>]+\.(?:md|txt|rst|html?)(?:\?[^\s)\"<>]*)?",
        re.IGNORECASE,
    ),
}


def detect_links(
    text: str, enabled_types: list[LinkType] | None = None
) -> list[DetectedLink]:
    """Scan text for links to supported platforms.

    Args:
        text: Content to scan for links.
        enabled_types: Limit detection to these types. ``None`` means all.

    Returns:
        Deduplicated list of detected links.
    """
    types = enabled_types or list(LinkType)
    seen: set[str] = set()
    links: list[DetectedLink] = []

    for link_type in types:
        pattern = LINK_PATTERNS.get(link_type)
        if pattern is None:
            continue

        for match in pattern.finditer(text):
            url = match.group(0)
            if url in seen:
                continue
            seen.add(url)

            if link_type == LinkType.GITHUB:
                repo = match.group(1)
                path = match.group(2)
                identifier = f"{repo}:{path}" if path else repo
            else:
                identifier = url

            links.append(DetectedLink(link_type=link_type, identifier=identifier, url=url))

    return links


# ---------------------------------------------------------------------------
# Crawl Models
# ---------------------------------------------------------------------------


@dataclass
class CrawlTrace:
    """Provenance information: how a document was discovered."""

    seed_url: str
    parent_url: str | None = None
    parent_title: str | None = None
    depth: int = 0
    path: list[str] = field(default_factory=list)

    def child(self, parent_url: str, parent_title: str | None = None) -> CrawlTrace:
        return CrawlTrace(
            seed_url=self.seed_url,
            parent_url=parent_url,
            parent_title=parent_title,
            depth=self.depth + 1,
            path=[*self.path, parent_url],
        )


@dataclass
class CrawledDocument:
    """A document fetched by the crawler."""

    url: str
    title: str
    content: str
    source_type: LinkType
    trace: CrawlTrace
    metadata: dict = field(default_factory=dict)

    @property
    def depth(self) -> int:
        return self.trace.depth

    @property
    def content_hash(self) -> str:
        """SHA-256 prefix for change detection."""
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()[:16]


@dataclass
class CrawlStats:
    """Aggregate statistics from a crawl run."""

    total_fetched: int = 0
    total_skipped: int = 0
    total_failed: int = 0
    by_source: dict[str, int] = field(default_factory=dict)
    by_depth: dict[int, int] = field(default_factory=dict)

    def record(self, doc: CrawledDocument) -> None:
        self.total_fetched += 1
        src = doc.source_type.value
        self.by_source[src] = self.by_source.get(src, 0) + 1
        self.by_depth[doc.depth] = self.by_depth.get(doc.depth, 0) + 1


# ---------------------------------------------------------------------------
# Crawler Service
# ---------------------------------------------------------------------------


@dataclass
class _QueueItem:
    link_type: LinkType
    identifier: str
    url: str
    trace: CrawlTrace


class MultiSourceCrawler:
    """Breadth-first crawler that follows links across platforms.

    Register fetcher functions for each :class:`LinkType`, then call
    :meth:`crawl` to discover and collect documents.

    Example::

        crawler = MultiSourceCrawler(max_depth=2)
        crawler.register_fetcher(LinkType.GITHUB, fetch_github_raw)
        crawler.add_seed("https://github.com/org/repo", LinkType.GITHUB, "org/repo")
        documents = crawler.crawl()
    """

    def __init__(
        self,
        max_depth: int = 2,
        max_docs: int = 50,
    ) -> None:
        self.max_depth = max_depth
        self.max_docs = max_docs
        self._queue: deque[_QueueItem] = deque()
        self._visited: set[str] = set()
        self._documents: list[CrawledDocument] = []
        self._stats = CrawlStats()
        self._fetchers: dict[LinkType, Callable[[str, str, CrawlTrace], CrawledDocument | None]] = {}
        self._seen_hashes: set[str] = set()

    def register_fetcher(
        self,
        link_type: LinkType,
        fetcher: Callable[[str, str, CrawlTrace], CrawledDocument | None],
    ) -> None:
        """Register a document fetcher for a link type.

        The fetcher signature is ``(identifier, url, trace) -> CrawledDocument | None``.
        """
        self._fetchers[link_type] = fetcher

    def add_seed(self, url: str, link_type: LinkType, identifier: str) -> None:
        """Add a seed URL to start crawling from."""
        trace = CrawlTrace(seed_url=url, depth=0)
        self._queue.append(_QueueItem(link_type=link_type, identifier=identifier, url=url, trace=trace))

    def crawl(self) -> list[CrawledDocument]:
        """Run the crawl. Returns all fetched documents."""
        while self._queue:
            if self._stats.total_fetched >= self.max_docs:
                print(colored(f"  Reached max documents limit ({self.max_docs})", "yellow"))
                break

            item = self._queue.popleft()

            if item.url in self._visited:
                continue
            if item.trace.depth > self.max_depth:
                self._stats.total_skipped += 1
                continue

            self._visited.add(item.url)

            fetcher = self._fetchers.get(item.link_type)
            if fetcher is None:
                continue

            try:
                doc = fetcher(item.identifier, item.url, item.trace)
            except Exception as exc:
                print(colored(f"  Failed to fetch {item.url}: {exc}", "red"))
                self._stats.total_failed += 1
                continue

            if doc is None:
                self._stats.total_failed += 1
                continue

            # Deduplicate by content hash (same content at different URLs)
            if doc.content_hash in self._seen_hashes:
                self._stats.total_skipped += 1
                continue
            self._seen_hashes.add(doc.content_hash)

            self._stats.record(doc)
            self._documents.append(doc)

            depth_indicator = "  " * doc.depth
            print(f"  {depth_indicator}[depth={doc.depth}] {doc.source_type.value}: {doc.title}")

            # Discover and queue child links
            if doc.depth < self.max_depth:
                child_trace = doc.trace.child(doc.url, doc.title)
                for link in detect_links(doc.content):
                    if link.url not in self._visited:
                        self._queue.append(
                            _QueueItem(
                                link_type=link.link_type,
                                identifier=link.identifier,
                                url=link.url,
                                trace=child_trace,
                            )
                        )

        return self._documents

    @property
    def stats(self) -> CrawlStats:
        return self._stats


# ---------------------------------------------------------------------------
# Built-in Fetchers
# ---------------------------------------------------------------------------


def fetch_github_raw(
    identifier: str, url: str, trace: CrawlTrace
) -> CrawledDocument | None:
    """Fetch a file from GitHub via the raw content URL.

    Works for public repositories without authentication.
    Set ``GITHUB_TOKEN`` to access private repos.
    """
    if _requests is None:
        print(colored("  requests library not installed, skipping GitHub fetch", "yellow"))
        return None

    # Build raw URL from github.com URL
    raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/").replace("/tree/", "/")
    if raw_url == url:
        # URL was just a repo root -- try fetching README
        parts = identifier.split(":")
        repo = parts[0]
        raw_url = f"https://raw.githubusercontent.com/{repo}/main/README.md"

    headers = {}
    token = __import__("os").environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    resp = _requests.get(raw_url, headers=headers, timeout=15)
    if resp.status_code != 200:
        return None

    content = resp.text[:15000]  # Limit content size
    repo = identifier.split(":")[0]
    path = identifier.split(":", 1)[1] if ":" in identifier else "README.md"
    title = f"{repo}/{path}"

    return CrawledDocument(
        url=url,
        title=title,
        content=content,
        source_type=LinkType.GITHUB,
        trace=trace,
        metadata={"repo": repo, "path": path},
    )


def fetch_web_page(
    identifier: str, url: str, trace: CrawlTrace
) -> CrawledDocument | None:
    """Fetch a plain-text or markdown web page."""
    if _requests is None:
        return None

    resp = _requests.get(url, timeout=15)
    if resp.status_code != 200:
        return None

    content = resp.text[:15000]
    # Use the last path segment as a rough title
    title = url.rsplit("/", 1)[-1] or url

    return CrawledDocument(
        url=url,
        title=title,
        content=content,
        source_type=LinkType.WEB,
        trace=trace,
    )


# ---------------------------------------------------------------------------
# Indexing helpers
# ---------------------------------------------------------------------------


def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks at sentence boundaries."""
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if end < len(text):
            for sep in [". ", ".\n", "\n\n", "\n", " "]:
                last_sep = chunk.rfind(sep)
                if last_sep > chunk_size // 2:
                    chunk = chunk[: last_sep + len(sep)]
                    end = start + len(chunk)
                    break

        stripped = chunk.strip()
        if stripped:
            chunks.append(stripped)
        start = end - overlap

    return chunks


def _to_dict(value) -> dict | None:
    """Convert an SDK object to a dict if possible."""
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return None


def _print_retrieved_sources(response) -> None:
    """Extract and display file_search results from a Responses API response."""
    output_items = getattr(response, "output", None) or []
    if isinstance(output_items, dict):
        output_items = [output_items]
    if not isinstance(output_items, list):
        return

    for item in output_items:
        item_dict = _to_dict(item) or {}
        if item_dict.get("type") != "file_search_call":
            continue
        results = (
            item_dict.get("results")
            or item_dict.get("file_search_call", {}).get("results")
            or []
        )
        if not results:
            print(colored("[sources] file_search returned no results", "yellow"))
            return
        print(f"\n  Retrieved {len(results)} chunks:")
        for result in results[:5]:
            r = _to_dict(result) or {}
            filename = r.get("filename", "unknown")
            score = r.get("score", "n/a")
            content_parts = r.get("content") or []
            snippet = ""
            for chunk in content_parts:
                chunk_dict = _to_dict(chunk) or {}
                text = chunk_dict.get("text")
                if text:
                    snippet += text.strip() + " "
            snippet = snippet.strip()
            # Show the source URL if embedded in the chunk
            source_line = ""
            if snippet.startswith("Source:"):
                first_line = snippet.split("\n", 1)[0]
                source_line = f" | {first_line}"
            preview = snippet[:150] + "..." if len(snippet) > 150 else snippet
            print(f"  - {filename} (score={score}){source_line}")
        return

    print(colored("[sources] no file_search results in response", "yellow"))


def index_crawled_documents(
    client: LlamaStackClient,
    vector_store_id: str,
    documents: list[CrawledDocument],
    chunk_size: int = 512,
) -> int:
    """Index crawled documents into a Llama Stack vector store.

    Each document is chunked and uploaded as a file. Metadata (source URL,
    crawl depth, provenance path) is embedded in the content so the LLM
    can cite sources.

    Returns the number of chunks indexed.
    """
    indexed = 0
    for doc in documents:
        # Build a crawl-path breadcrumb for provenance
        provenance = " -> ".join(doc.trace.path + [doc.url]) if doc.trace.path else doc.url

        chunks = _chunk_text(doc.content, chunk_size)
        for i, chunk in enumerate(chunks):
            # Embed source metadata directly in the chunk content
            enriched = (
                f"Source: {doc.url}\n"
                f"Crawl path: {provenance}\n"
                f"Depth: {doc.depth}\n\n"
                f"{chunk}"
            )

            filename = f"{doc.source_type.value}_{doc.content_hash}_chunk{i}.txt"
            buf = BytesIO(enriched.encode("utf-8"))
            buf.name = filename

            try:
                uploaded = client.files.create(file=buf, purpose="assistants")
                client.vector_stores.files.create(
                    vector_store_id=vector_store_id,
                    file_id=uploaded.id,
                    chunking_strategy={
                        "type": "static",
                        "static": {"max_chunk_size_tokens": 512, "chunk_overlap_tokens": 64},
                    },
                )
                indexed += 1
            except Exception as exc:
                print(colored(f"  Failed to index chunk {i} of {doc.title}: {exc}", "red"))

    return indexed


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

# Default seed URLs for demonstration -- two public GitHub READMEs that
# cross-reference each other and link to external docs.
DEFAULT_SEEDS = [
    ("https://github.com/meta-llama/llama-stack", LinkType.GITHUB, "meta-llama/llama-stack"),
]


def main(
    host: str,
    port: int,
    model_id: str | None = None,
    embedding_model_id: str | None = None,
    max_depth: int = 1,
    max_docs: int = 10,
    seed_urls: list[str] | None = None,
    question: str = "What is Llama Stack and what APIs does it provide?",
    system_prompt: str | None = None,
) -> None:
    """Run the multi-source RAG crawler demo.

    Args:
        host: Llama Stack server hostname.
        port: Llama Stack server port.
        model_id: Chat model to use (auto-detected if omitted).
        embedding_model_id: Embedding model (auto-detected if omitted).
        max_depth: How many link-hops to follow from seed documents.
        max_docs: Maximum total documents to crawl.
        seed_urls: GitHub URLs to start crawling from. Defaults to llama-stack repo.
        question: Question to answer using the crawled knowledge base.
        system_prompt: Custom system prompt for the RAG query. If omitted, a
            default prompt that instructs the model to cite sources and crawl
            paths is used.
    """
    _maybe_load_dotenv()

    # -- Connect to Llama Stack -------------------------------------------------
    client = LlamaStackClient(base_url=f"http://{host}:{port}")

    resolved_model = model_id or __import__("os").environ.get("LLAMA_STACK_MODEL")
    if resolved_model is None:
        resolved_model = get_any_available_chat_model(client)
        if resolved_model is None:
            return
    else:
        if not check_model_is_available(client, resolved_model):
            return
        if not can_model_chat(client, resolved_model):
            print(colored(f"Model `{resolved_model}` does not support chat.", "red"))
            return

    embedding_model = embedding_model_id or get_any_available_embedding_model(client)
    if embedding_model is None:
        return

    embedding_dimension = get_embedding_dimension(client, embedding_model)
    if embedding_dimension is None:
        print(colored("Unable to determine embedding dimension.", "red"))
        return

    vector_providers = [p for p in client.providers.list() if p.api == "vector_io"]
    if not vector_providers:
        print(colored("No vector_io providers available.", "red"))
        return
    provider_id = vector_providers[0].provider_id

    # -- Phase 1: Crawl ---------------------------------------------------------
    print(colored("\n=== Phase 1: Crawling documents ===\n", "cyan"))
    print(f"  max_depth={max_depth}, max_docs={max_docs}")

    crawler = MultiSourceCrawler(max_depth=max_depth, max_docs=max_docs)
    crawler.register_fetcher(LinkType.GITHUB, fetch_github_raw)
    crawler.register_fetcher(LinkType.WEB, fetch_web_page)

    if seed_urls:
        for url in seed_urls:
            if "github.com" in url:
                repo = url.replace("https://github.com/", "").replace("http://github.com/", "").strip("/")
                crawler.add_seed(url, LinkType.GITHUB, repo)
            else:
                crawler.add_seed(url, LinkType.WEB, url)
    else:
        for url, link_type, identifier in DEFAULT_SEEDS:
            crawler.add_seed(url, link_type, identifier)

    documents = crawler.crawl()
    stats = crawler.stats

    print(colored(f"\n  Crawl complete: {stats.total_fetched} documents fetched", "green"))
    if stats.by_source:
        breakdown = ", ".join(f"{k}: {v}" for k, v in stats.by_source.items())
        print(f"  By source: {breakdown}")
    if stats.by_depth:
        breakdown = ", ".join(f"depth {k}: {v}" for k, v in sorted(stats.by_depth.items()))
        print(f"  By depth: {breakdown}")
    if stats.total_skipped:
        print(f"  Skipped (duplicates): {stats.total_skipped}")
    if stats.total_failed:
        print(f"  Failed: {stats.total_failed}")

    if not documents:
        print(colored("No documents were crawled. Check network access and seed URLs.", "red"))
        return

    # -- Phase 2: Index into vector store ----------------------------------------
    print(colored("\n=== Phase 2: Indexing into Llama Stack vector store ===\n", "cyan"))

    vector_store = None
    try:
        vector_store = client.vector_stores.create(
            name=f"crawler_demo_{uuid4()}",
            extra_body={
                "provider_id": provider_id,
                "embedding_model": embedding_model,
                "embedding_dimension": embedding_dimension,
            },
        )
        print(f"  Created vector store: {vector_store.id}")

        indexed = index_crawled_documents(client, vector_store.id, documents)
        print(colored(f"  Indexed {indexed} chunks from {len(documents)} documents", "green"))

        # -- Phase 3: Query with RAG ------------------------------------------------
        print(colored("\n=== Phase 3: Querying with RAG ===\n", "cyan"))
        print(f"  Question: {question}\n")

        default_instructions = (
            "Answer the question using the documents provided via file_search. "
            "Each document chunk includes a 'Source:' URL and a 'Crawl path:' showing "
            "how it was discovered (e.g. README -> linked doc -> linked issue). "
            "When referencing information, cite the source URL. "
            "If relevant, mention the crawl path to show how the information connects."
        )
        instructions = system_prompt or default_instructions
        print(f"  System prompt: {instructions[:100]}{'...' if len(instructions) > 100 else ''}\n")

        response = client.responses.create(
            model=resolved_model,
            instructions=instructions,
            input=[{"role": "user", "content": question}],
            tools=[{"type": "file_search", "vector_store_ids": [vector_store.id]}],
            tool_choice={"type": "file_search"},
            include=["file_search_call.results"],
            stream=False,
        )

        # Show which sources were retrieved (with scores and provenance)
        _print_retrieved_sources(response)

        print(colored("\n[response]", "green"), response.output_text or response.output)

    finally:
        if vector_store is not None:
            try:
                client.vector_stores.delete(vector_store_id=vector_store.id)
            except Exception as e:
                print(colored(f"Warning: Failed to delete vector store: {e}", "yellow"))


if __name__ == "__main__":
    fire.Fire(main)
