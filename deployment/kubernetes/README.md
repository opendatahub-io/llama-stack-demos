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

### 2. Obtain a Hugging Face Token

You'll need a Hugging Face token for downloading models. Get one from [Hugging Face](https://huggingface.co/settings/tokens). You'll configure this in Step 1 of the deployment.

## Deployment Steps

### Step 1: Configure Hugging Face Token

Edit the secret file with your Hugging Face token:

```bash
# Edit the secret and replace 'your-base64-encoded-token-here' with your actual base64-encoded token
# To encode your token: echo -n "your-hugging-face-token" | base64
nano vllm-serve/base/00-hf-token-secret.yaml
```

Alternatively, create the secret directly with kubectl:

```bash
kubectl create secret generic hf-token-secret --from-literal=token=YOUR_HF_TOKEN
```

Note: The PVC and other resources will be created automatically in the next step via Kustomize.

### Step 2: Deploy vLLM Server

Deploy the vLLM server using Kustomize. Choose the appropriate overlay based on your architecture.

**Preview the manifests first (optional but recommended):**
```bash
# For x86_64
kubectl kustomize vllm-serve/overlays/x86_64/

# For ARM64
kubectl kustomize vllm-serve/overlays/arm64/
```

**Deploy for x86_64 (Intel/AMD) systems:**
```bash
kubectl apply -k vllm-serve/overlays/x86_64/
```

**Deploy for ARM64 (Apple Silicon, ARM servers) systems:**
```bash
kubectl apply -k vllm-serve/overlays/arm64/
```

The vLLM server will:
- Serve an OpenAI-compatible API on port 8000
- Mount model cache at `/cache/huggingface`
- Use the HF token for authentication
- Use architecture-specific container images:
  - x86_64: `public.ecr.aws/q9t5s3a7/vllm-cpu-release-repo:latest`
  - ARM64: `public.ecr.aws/q9t5s3a7/vllm-arm64-cpu-release-repo:latest`

### Step 3: Install Llama Stack Operator

Install the Llama Stack Kubernetes operator:

```bash
kubectl apply -f https://raw.githubusercontent.com/llamastack/llama-stack-k8s-operator/main/release/operator.yaml
```

Verify the operator is running:

```bash
kubectl get pods -n llama-stack-k8s-operator-system
```

### Step 4: Deploy Llama Stack

Deploy Llama Stack using the same architecture overlay you used for vLLM:

**For x86_64 deployment:**
```bash
kubectl apply -k llama-stack/overlays/x86_64/
```

**For ARM64 deployment:**
```bash
kubectl apply -k llama-stack/overlays/arm64/
```

The Kustomize overlay automatically configures the VLLM_URL to match the vLLM service deployed in Step 2.

This creates a Llama Stack deployment that:
- Uses the "starter" distribution
- Exposes port 8321
- Automatically connects to the correct vLLM service based on architecture
- Allocates 20Gi of storage for Llama Stack data

### Step 5: Test the Deployment

Forward the Llama Stack port to your local machine:

```bash
kubectl port-forward svc/llamastack-vllm 8321:8321
```

Test the deployment using the Llama Stack client:

```bash
llama-stack-client --endpoint http://localhost:8321 inference chat-completion --message "hello, what model are you?"
```

## Configuration Files

The deployment uses a Kustomize structure for easy customization:

### vLLM Server (`vllm-serve/`)
The vLLM deployment uses Kustomize with architecture-specific overlays:

```
vllm-serve/
├── base/                           # Base Kubernetes resources
│   ├── kustomization.yaml          # Base Kustomize configuration
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

See `vllm-serve/README.md` for detailed usage instructions.

### Llama Stack (`llama-stack/`)
The Llama Stack deployment also uses Kustomize with architecture-specific overlays:

```
llama-stack/
├── base/                           # Base Kubernetes resources
│   ├── kustomization.yaml          # Base Kustomize configuration
│   └── 00-lls-cr.yaml             # LlamaStackDistribution custom resource
└── overlays/                       # Architecture-specific overlays
    ├── x86_64/                     # x86_64 variant (patches VLLM_URL)
    │   └── kustomization.yaml
    └── arm64/                      # ARM64 variant (patches VLLM_URL)
        └── kustomization.yaml
```

The overlays automatically configure the correct vLLM service URL based on the architecture.

## Troubleshooting

### vLLM Issues

Check pod status (the name prefix depends on which overlay you deployed):
```bash
# For x86_64 deployment
kubectl get pods -l app.kubernetes.io/name=vllm
kubectl logs -l app.kubernetes.io/name=vllm

# Or list all pods to see the prefixed names
kubectl get pods
```

Verify service connectivity from a debug pod:
```bash
kubectl run curl --rm -it --image=curlimages/curl -- /bin/sh

# For x86_64 deployment
curl http://x86-64-vllm-server.default.svc.cluster.local:8000/v1/models

# For ARM64 deployment
curl http://arm64-vllm-server.default.svc.cluster.local:8000/v1/models
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
args:
- vllm serve your-model-name --served-model-name your-model-name --max-model-len 8192 --dtype float32
```

Then deploy using the appropriate overlay:
```bash
kubectl apply -k vllm-serve/overlays/x86_64/  # or arm64
```

### Creating Custom Overlays

You can create additional overlays for different environments (dev, staging, prod) or configurations. For example, to create a production overlay with different resource limits:

```bash
mkdir -p vllm-serve/overlays/production
# Create a kustomization.yaml with your customizations
```

See the [Kustomize documentation](https://kubectl.docs.kubernetes.io/references/kustomize/) for more details.

### Custom Llama Stack Configuration

To use a custom `config.yaml`, create a ConfigMap and reference it in the `LlamaStackDistribution` resource. See the [LlamaStackDistribution API documentation](https://github.com/llamastack/llama-stack-k8s-operator) for details.

## Related Resources

- [Llama Stack Documentation](https://llamastack.io)
- [Llama Stack Kubernetes Operator](https://github.com/llamastack/llama-stack-k8s-operator)
- [vLLM Documentation](https://docs.vllm.ai)
- [LlamaStackDistribution API Reference](https://github.com/llamastack/llama-stack-k8s-operator/blob/main/docs/api-reference.md)

## Clean Up

To remove all resources (use the same architecture overlay you deployed):

```bash
# For x86_64 deployment:
kubectl delete -k llama-stack/overlays/x86_64/
kubectl delete -k vllm-serve/overlays/x86_64/

# OR for ARM64 deployment:
kubectl delete -k llama-stack/overlays/arm64/
kubectl delete -k vllm-serve/overlays/arm64/

# Delete operator
kubectl delete -f https://raw.githubusercontent.com/llamastack/llama-stack-k8s-operator/main/release/operator.yaml

# Delete Kind cluster
kind delete cluster --name llama-stack-test
```
