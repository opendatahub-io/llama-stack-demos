# Llama Stack Demos on OpenDataHub

This repository contains practical examples and demos designed to get you started quickly building AI apps with [Llama Stack](https://github.com/meta-llama/llama-stack) on Kubernetes or OpenShift. Whether you're a cluster admin looking to deploy the right GenAI infrastructure or a developer eager to innovate with AI Agents, the content in this repo should help you get started.

## 🛠️ Get Started

### Requirements

To run these demos, ensure your environment meets the following:

* OpenShift Cluster 4.17+
* 2 GPUs with a minimum of 40GB VRAM each.

### Deployment Instructions

Next, follow these simple steps to deploy the core components:

1.  Create a dedicated OpenShift project:
    ```bash
    oc new-project llama-serve
    ```
2.  Apply the Kubernetes manifests:
    ```bash
    oc apply -k kubernetes/kustomize/overlay/all-models
    ```
    This will deploy the foundational Llama Stack services, vLLM model servers, and MCP tool servers.


### Setting Up Your Development Environment

We use `uv` for managing Python dependencies, ensuring a consistent and efficient development experience. Here's how to get your environment ready:

1.  Install `uv`:
    ```bash
    pip install uv
    ```
2.  Synchronize your environment:
    ```bash
    uv sync
    ```
3.  Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```
4.  (macOS only) Install SSL certificates to avoid certificate verification errors (adjust the Python version in the path to match your installed version):
    ```bash
    /Applications/Python\ 3.12/Install\ Certificates.command
    ```

Now you're all set to run any Python scripts or Jupyter notebooks within the `demos/rag_agentic` directory!

## 💡 Demo Architecture
The below diagram is an example architecture for a secure Llama Stack based application deployed on OpenShift (OCP) using both MCP tools and a [Milvus](https://milvus.io/) vectorDB for its agentic and RAG based workflows. This is the same architecture that has been implemented in the [RAG/Agentic](./demos/rag_agentic/) demos.

![Architecture Diagram](./images/architecture-diagram.jpg)

---

We're excited to see what you build with Llama Stack! If you have any questions or feedback, please don't hesitate to open an [issue](https://github.com/opendatahub-io/llama-stack-demos/issues). Happy building! 🎉
