# llama-stack-demos distribution

This directory contains the necessary files to build the llama stack distribution container image.

## Prerequisites

- Clone the repository: `git clone ...`
- Install `uv`: instructions [here](https://docs.astral.sh/uv/getting-started/installation/)
- Install the dependencies: `uv sync`
- Make sure either `podman` or `docker` is installed.

## Build the image

```bash
uv run llama stack build --config build.yaml
```

By default, docker is used to build the image. If you want to use podman, export
`export CONTAINER_BINARY=podman` before running the build.

## Run the llama stack server

```bash
podman run --rm \
    -v ./providers.d:/app/providers.d \
    -e VLLM_URL=http://localhost/v1 \ # Tweak to the actual URL to the vllm server
    -p 8321:8321 \
    --name llama-stack-server \
    localhost/llama-stack-demos:0.2.17 # Tweak to the actual tag of the llama stack
```

The `run.yaml` file is baked into the container image.
Note: the tag will change based on the version of llama stack.
