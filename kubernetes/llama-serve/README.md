# vLLM serve

This serves as a starting point to deploy the following models via vLLM:

- `granite-8b`
- `llama-3.1-70b`
- `llama-3.2-3b`
- `watt-8b`

## Requirements

A secret must be created to allow for the vLLM server to pull in a given model at startup time.

```
oc create secret generic huggingface-secret --from-literal=HF_TOKEN=hf_values
```

## Deploy model

run
```bash
oc apply --kustomize $GIT_ROOT/kubernetes/llama-server/[granite-8b|llama-3.1-70b|llama-3.2-3b|watt-8b]
```

You can find the deployment files for the different models in their respective directories:

- [llama3.1-70b](./llama3.1-70b)
    - [vllm-openai.yaml](./llama3.1-70b/vllm-openai.yaml)
- [watt-8b](./watt-8b)
    - [vllm-openai.yaml](./watt-8b/vllm-openai.yaml)

 Once you know which model you want to deploy, you can run the following:

```
oc expose deployment/vllm
```

## Using the vLLM server

The vLLM instance is running with a service, this service can be accessed by other namespaces in the cluster as well as outside the cluster by using port-forward.

To use port-forward run the following:

```
oc port-forward service/vllm 8000:8000
```

## Testing

To check if the model is running correctly, you can try the following `curl` command by replacing `model` with the name of the model you deployed:

```
 curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "prompt": "San Francisco is a",
        "max_tokens": 200,
        "temperature": 0
    }'
```
