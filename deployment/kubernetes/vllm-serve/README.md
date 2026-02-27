# VLLM Server Deployment

This directory contains Kubernetes manifests for deploying VLLM server with Kustomize support for different architectures.

## Directory Structure

```
vllm-serve/
├── base/                           # Base Kubernetes resources
│   ├── kustomization.yaml
│   ├── 00-hf-token-secret.yaml    # HuggingFace token secret
│   ├── 01-vllm-models-pvc.yaml    # Persistent volume claim for models
│   ├── 02-vllm-server-deploy.yaml # VLLM server deployment
│   └── 03-vllm-server-service.yaml # VLLM server service
└── overlays/                       # Architecture-specific overlays
    ├── x86_64/                     # x86_64 CPU variant
    │   └── kustomization.yaml
    └── arm64/                      # ARM64 CPU variant
        └── kustomization.yaml
```

## Usage

### Deploy for x86_64 architecture:

```bash
kubectl apply -k overlays/x86_64/
```

This uses the image: `public.ecr.aws/q9t5s3a7/vllm-cpu-release-repo:latest`

### Deploy for ARM64 architecture:

```bash
kubectl apply -k overlays/arm64/
```

This uses the image: `public.ecr.aws/q9t5s3a7/vllm-arm64-cpu-release-repo:latest`

### Preview the manifests without applying:

```bash
# For x86_64
kubectl kustomize overlays/x86_64/

# For ARM64
kubectl kustomize overlays/arm64/
```

### Delete deployment:

```bash
# For x86_64
kubectl delete -k overlays/x86_64/

# For ARM64
kubectl delete -k overlays/arm64/
```

## Customization

To modify the deployment:

1. Edit the base manifests in the `base/` directory for changes that apply to all architectures
2. Edit the overlay-specific `kustomization.yaml` files for architecture-specific changes

## Prerequisites

- Create the HuggingFace token secret before deploying:
  ```bash
  kubectl create secret generic hf-token-secret --from-literal=token=YOUR_HF_TOKEN
  ```
  Or edit `base/00-hf-token-secret.yaml` with your base64-encoded token.
