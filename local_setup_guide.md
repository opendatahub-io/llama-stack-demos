# Local Llama Stack Setup Guide

This guide will walk you through setting up and running a Llama Stack server with Ollama and Podman.

---

## **1. Prerequisites**
Ensure you have the following installed:
- **Podman** ([Install Podman](https://podman.io/docs/installation))
- **Python 3.10+**
- **pip** ([Install pip](https://pip.pypa.io/en/stable/installation/))
- **Ollama** ([Install Ollama](https://ollama.com/download))


Verify installation:
```bash
podman --version
python3 --version
pip --version
ollama --version
```

---

## **2. Start Ollama**
Before running Llama Stack, start the Ollama server with:
```bash
ollama run llama3.2:3b-instruct-fp16 --keepalive 60m
```
This ensures the model stays loaded in memory for 60 minutes.

---

## **3. Set Up Environment Variables**
Set up the required environment variables:
```bash
export INFERENCE_MODEL="meta-llama/Llama-3.2-3B-Instruct"
export LLAMA_STACK_PORT=8321
```

---

## **4. Run Llama Stack Server with Podman**
Pull the required image:
```bash
podman pull docker.io/llamastack/distribution-ollama
```
Before executing the next command, make sure to create a local directory to mount into the container’s file system.

```bash
mkdir -p ~/.llama
```

Now run the server using:
```bash
podman run -it \
  -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  -v ~/.llama:/root/.llama \
  --env INFERENCE_MODEL=$INFERENCE_MODEL \
  --env OLLAMA_URL=http://host.containers.internal:11434 \
  llamastack/distribution-ollama \
  --port $LLAMA_STACK_PORT
```
If needed, create and use a network:
```bash
podman network create llama-net
podman run --privileged --network llama-net -it \
  -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  llamastack/distribution-ollama \
  --port $LLAMA_STACK_PORT
```

Verify the container is running:
```bash
podman ps
```

---

## **5. Set Up Python Environment**
Create a virtual environment using `uv` and install required libraries:

```bash
pip install uv
uv sync
source .venv/bin/activate # macOS/Linux
# On Windows: llama-stack-demo\Scripts\activate
```
Verify installation:
```bash
pip list | grep llama-stack-client
```
---

## **6. Configure the Client**
Set up the client to connect to the Llama Stack server:
```bash
llama-stack-client configure --endpoint http://localhost:$LLAMA_STACK_PORT
```
List available models:
```bash
llama-stack-client models list
```

---

## **7. Quickly setting up your environment**

Now that your environemnt has gone through the initial set up, you can quickly return to a running ollama and llama stack server using the `setup_local` command available in the [Makefile](./Makefile).

```bash
make setup_local
```

---

## **8. Debugging Common Issues**
**Check if Podman is Running:**
```bash
podman ps
```

**Ensure the Virtual Environment is Activated:**
```bash
source llama-stack-demo/bin/activate
```

**Reinstall the Client if Necessary:**
```bash
pip uninstall llama-stack-client
pip install llama-stack-client
```

**Test Importing the Client in Python:**
```bash
python -c "from llama_stack_client import LlamaStackClient; print(LlamaStackClient)"
```

---
