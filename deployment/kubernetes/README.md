# Kubernetes Deployment Guide for Llama Stack

This guide demonstrates how to deploy Llama Stack and vLLM servers in a Kubernetes cluster using Kind and the Llama Stack Kubernetes operator.

## Overview

This deployment uses:
- **vLLM**: OpenAI-compatible inference server for serving LLM models
- **Llama Stack**: Unified API for interacting with LLM models
- **Llama Stack Kubernetes Operator**: Manages Llama Stack deployments via custom resources

## Prerequisites

### 1. Create a Kind Cluster

```bash
kind create cluster --image kindest/node:v1.32.0 --name llama-stack-test
```

### 2. Set Up Hugging Face Token

Export your Hugging Face token as a base64-encoded environment variable:

```bash
export HF_TOKEN=$(echo -n "your-hugging-face-token" | base64)
```

This token is required for downloading models from Hugging Face.

Edit `vllm-serve/base/00-hf-token-secret.yaml` with your base64-encoded token.

## Deployment Steps

### Step 1: Deploy vLLM Server

Deploy the vLLM server using Kustomize. Choose the overlay matching your CPU architecture:

```bash
# For x86_64 (Intel/AMD)
kubectl apply -k vllm-serve/overlays/x86_64/

# For ARM64 (Apple Silicon, ARM servers)
kubectl apply -k vllm-serve/overlays/arm64/
```

The overlays use architecture-specific container images:
- x86_64: `public.ecr.aws/q9t5s3a7/vllm-cpu-release-repo:latest`
- ARM64: `public.ecr.aws/q9t5s3a7/vllm-arm64-cpu-release-repo:latest`

The vLLM server will:
- Serve an OpenAI-compatible API on port 8000
- Mount model cache at `/cache/huggingface`
- Use the HF token for authentication

### Step 2: Install Llama Stack Operator

Install the Llama Stack Kubernetes operator:

```bash
# Option 1: Apply from remote URL
kubectl apply -f https://raw.githubusercontent.com/llamastack/llama-stack-k8s-operator/main/release/operator.yaml
```

Verify the operator is running:

```bash
kubectl get pods -n llama-stack-k8s-operator-system
```

### Step 3: Deploy Llama Stack

Create a `LlamaStackDistribution` custom resource:

```bash
# Create Llama Stack distribution
kubectl apply -f llama-stack/00-lls-cr.yaml
```

This creates a Llama Stack deployment that:
- Uses the "starter" distribution
- Exposes port 8321
- Connects to the vLLM service at `http://vllm-server.default.svc.cluster.local:8000/v1`
- Allocates 20Gi of storage for Llama Stack data

### Step 4: Test the Deployment

Forward the Llama Stack port to your local machine:

```bash
kubectl port-forward svc/llamastack-vllm 8321:8321
```

Test the deployment using the Llama Stack client:

```bash
llama-stack-client --endpoint http://localhost:8321 inference chat-completion --message "hello, what model are you?"
```

## Configuration Files

The deployment consists of the following YAML files:

### vLLM Server (`vllm-serve/`)

```text
vllm-serve/
├── base/                           # Base Kubernetes resources
│   ├── kustomization.yaml
│   ├── 00-hf-token-secret.yaml    # Secret containing Hugging Face token
│   ├── 01-vllm-models-pvc.yaml    # PersistentVolumeClaim (50Gi) for model storage
│   ├── 02-vllm-server-deploy.yaml # vLLM server deployment
│   └── 03-vllm-server-service.yaml # ClusterIP service exposing vLLM on port 8000
└── overlays/                       # Architecture-specific overlays
    ├── x86_64/                     # Intel/AMD CPU variant
    │   └── kustomization.yaml
    └── arm64/                      # ARM64 CPU variant
        └── kustomization.yaml
```

### Llama Stack (`llama-stack/`)
- `00-lls-cr.yaml` - LlamaStackDistribution custom resource

## Troubleshooting

### vLLM Issues

Check pod status:
```bash
kubectl get pods -l app.kubernetes.io/name=vllm
kubectl logs -l app.kubernetes.io/name=vllm
```

Verify service connectivity from a debug pod:
```bash
kubectl run curl --rm -it --image=curlimages/curl -- /bin/sh
curl http://vllm-server.default.svc.cluster.local:8000/v1/models
```

### Llama Stack Issues

Inspect the custom resource:
```bash
kubectl describe llamastackdistribution llamastack-vllm
```

Check operator logs:
```bash
kubectl logs -n llama-stack-k8s-operator-system -l control-plane=controller-manager
```

Check Llama Stack pod:
```bash
kubectl get pods -l app.kubernetes.io/instance=llamastack-vllm
kubectl logs -l app.kubernetes.io/instance=llamastack-vllm
```

## Customization

### Using a Different Model

Edit `vllm-serve/base/02-vllm-server-deploy.yaml` and change the model in the args:

```yaml
args: ["serve", "your-model-name"]
```

### Custom Llama Stack Configuration

To use a custom `config.yaml`, create a ConfigMap and reference it in the `LlamaStackDistribution` resource. See the [LlamaStackDistribution API documentation](https://github.com/llamastack/llama-stack-k8s-operator) for details.

## Related Resources

- [Llama Stack Documentation](https://llamastack.io)
- [Llama Stack Kubernetes Operator](https://github.com/llamastack/llama-stack-k8s-operator)
- [vLLM Documentation](https://docs.vllm.ai)
- [LlamaStackDistribution API Reference](https://github.com/llamastack/llama-stack-k8s-operator/blob/main/docs/api-reference.md)

## Clean Up

To remove all resources:

```bash
# Delete Llama Stack deployment
kubectl delete -f llama-stack/00-lls-cr.yaml

# Delete vLLM resources (use the same overlay you deployed with)
kubectl delete -k vllm-serve/overlays/x86_64/  # or arm64

# Delete operator
kubectl delete -f https://raw.githubusercontent.com/llamastack/llama-stack-k8s-operator/main/release/operator.yaml

# Delete Kind cluster
kind delete cluster --name llama-stack-test
```
