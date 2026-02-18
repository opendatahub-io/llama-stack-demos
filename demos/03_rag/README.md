# RAG (Retrieval-Augmented Generation)

## Overview
This folder teaches Retrieval-Augmented Generation (RAG) techniques using Llama Stack's vector stores and search capabilities. These examples show how to ground model responses in retrieved documents, combine multiple data sources, and optimize retrieval strategies.

## Learning Objectives
- Build basic RAG systems with file_search tool
- Combine multiple vector stores for multi-source retrieval
- Filter search results using metadata attributes
- Optimize chunking strategies for different use cases
- Implement hybrid search combining local and web sources

## Demos

### Demo 1: Simple RAG
**File**: `01_simple_rag.py`

**Concepts**: RAG workflow (embed, store, retrieve, generate), file_search tool, vector store creation, document upload, context retrieval

**Description**: Demonstrates the basic RAG workflow by creating a vector store, uploading a document, and using the file_search tool to retrieve relevant context for answering questions.

**Run**:
```bash
python -m demos.03_rag.01_simple_rag localhost 8321
```

### Demo 2: Multi-Source RAG
**File**: `02_multi_source_rag.py`

**Concepts**: Multiple vector stores, cross-source retrieval, diverse knowledge bases, consolidated search

**Description**: Shows how to perform RAG across two separate vector stores using file_search, enabling retrieval from multiple knowledge sources simultaneously.

**Run**:
```bash
python -m demos.03_rag.02_multi_source_rag localhost 8321
```

### Demo 3: RAG with Metadata
**File**: `03_rag_with_metadata.py`

**Concepts**: Metadata filtering, document attributes, filtered search, metadata-based retrieval, source filtering

**Description**: Demonstrates how to filter file_search results by metadata attributes, allowing for more targeted retrieval based on document properties like source, date, or category.

**Run**:
```bash
python -m demos.03_rag.03_rag_with_metadata localhost 8321 --source doc_a
```

### Demo 4: Chunking Strategies
**File**: `04_chunking_strategies.py`

**Concepts**: Chunking strategies, chunk size optimization, chunk overlap, static chunking, retrieval quality optimization

**Description**: Compares different chunk sizes for the same document to demonstrate how chunking strategies affect retrieval quality and response accuracy.

**Run**:
```bash
python -m demos.03_rag.04_chunking_strategies localhost 8321
```

### Demo 5: Hybrid Search
**File**: `05_hybrid_search.py`

**Concepts**: Hybrid search, file_search + web_search combination, local and external knowledge, multi-source synthesis, context aggregation

**Description**: Combines file_search (for local vector store retrieval) with web_search (for real-time web data) in a single workflow, synthesizing information from both local documents and the web.

**Run**:
```bash
python -m demos.03_rag.05_hybrid_search localhost 8321
```
