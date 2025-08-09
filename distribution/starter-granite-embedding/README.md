# Building a starter Llama Stack image with Milvus inline and Granite Embedding Model.
### Clone the Llama Stack repo
```
git clone https://github.com/meta-llama/llama-stack.git

cd llama-stack
```

### Make alterations to the starter build file
```
# Copy the provided build.yaml file and replace the build.yaml file in the starter template folder.
cp $GIT_ROOT/distribution/starter-granite-embedding/build.yaml llama_stack/templates/starter/build.yaml
```

### Make alterations to the starter template run.yaml file
Replace the vector_io provider with milvus in llama_stack/templates/starter/run.yaml:
```
vector_io:
  - provider_id: milvus
    provider_type: inline::milvus
    config:
      db_path: ${env.MILVUS_DB_PATH}
```
Replace the embedding model with `ibm-granite/granite-embedding-125m-english`
```
models:
...
- metadata:
    embedding_dimension: 768
  model_id: ibm-granite/granite-embedding-125m-english
  provider_id: sentence-transformers
  model_type: embedding
```
### Build the image
By default, docker is used to build the image. If you want to use podman, export
`export CONTAINER_BINARY=podman` before running the build.

To build the image:
```
CONTAINER_BINARY=podman BUILD_PLATFORM=linux/amd64 USE_COPY_NOT_MOUNT=true LLAMA_STACK_DIR=. llama stack build --template starter --image-type container
```
### Run the image
```bash
podman run --rm \
    -e VLLM_URL=http://localhost/v1 \ # Tweak to the actual URL to the vllm server
    -p 8321:8321 \
    --name llama-stack-server \
    localhost/distribution-starter:dev \
    --env MILVUS_DB_PATH=/.llama/distributions/starter/milvus.db \
    --env INFERENCE_MODEL=llama3.2:3b
```

### Install llama stack client to run server without building image

```bash
pip install -U llama_stack pymilvus
export INFERENCE_MODEL=meta-llama/llama3.2:3b # Or set to other model
llama stack run $GIT_ROOT/distribution/starter-granite-embedding/run.yaml
```
