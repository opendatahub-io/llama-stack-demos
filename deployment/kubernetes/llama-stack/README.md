# Llama Stack Deployment

This directory contains Kubernetes manifests for deploying Llama Stack with Kustomize support for different vLLM architectures.

## Directory Structure

```
llama-stack/
├── base/                           # Base Kubernetes resources
│   ├── kustomization.yaml
│   └── 00-lls-cr.yaml             # LlamaStackDistribution custom resource
└── overlays/                       # Architecture-specific overlays
    ├── x86_64/                     # x86_64 CPU variant
    │   └── kustomization.yaml
    └── arm64/                      # ARM64 CPU variant
        └── kustomization.yaml
```

## Usage

The Llama Stack deployment must be used with the corresponding vLLM deployment architecture.

### Deploy for x86_64 architecture:

```bash
kubectl apply -k overlays/x86_64/
```

This configures the VLLM_URL to: `http://x86-64-vllm-server.default.svc.cluster.local:8000/v1`

### Deploy for ARM64 architecture:

```bash
kubectl apply -k overlays/arm64/
```

This configures the VLLM_URL to: `http://arm64-vllm-server.default.svc.cluster.local:8000/v1`

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

## Prerequisites

1. **Llama Stack Kubernetes Operator** must be installed:
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/llamastack/llama-stack-k8s-operator/main/release/operator.yaml
   ```

2. **vLLM Server** must be deployed with the matching architecture overlay from `../vllm-serve/`

## Customization

To modify the deployment:

1. Edit the base manifest in `base/00-lls-cr.yaml` for changes that apply to all architectures
2. Edit the overlay-specific `kustomization.yaml` files to adjust architecture-specific patches

### Example: Change the VLLM_MAX_TOKENS value

Add a patch to the overlay's `kustomization.yaml`:

```yaml
patches:
  - target:
      kind: LlamaStackDistribution
      name: llamastack-vllm
    patch: |-
      - op: replace
        path: /spec/server/containerSpec/env/1/value
        value: "8192"
```

## Troubleshooting

Check the LlamaStackDistribution status:
```bash
kubectl describe llamastackdistribution llamastack-vllm
```

Check pod logs:
```bash
kubectl get pods -l app.kubernetes.io/instance=llamastack-vllm
kubectl logs -l app.kubernetes.io/instance=llamastack-vllm
```

Check operator logs:
```bash
kubectl logs -n llama-stack-k8s-operator-system -l control-plane=controller-manager
```
