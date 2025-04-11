# Llama Stack Demos
## Overview
This document provides an overview of the architecture and deployment process for the Llama Stack on OpenShift (OCP). It demonstrates how the Llama Stack agentic framework, vLLM agents, and multiple MCP servers are interconnected and deployed within an OpenShift cluster. The architecture diagram below illustrates the logical flow and integration of these components.

![Architecture Diagram](./images/architecture-diagram.jpg)

## Requirements
The following scenario requires at minimum the following:

* OpenShift Cluster 4.17+
* 2 GPUs available to host Granite and Llama models

The following operators must be installed:
* Red Hat OpenShift AI
* Node Feature Discovery Operator
* NVIDIA GPU Operator
* Red Hat build of OpenTelemetry

Optionally, if you are wanting to use the Ansible MCP server Ansible Automation Platform must be deployed.

The installation of these components exists within product documentation please refer to those assets to identify how to properly configure the Operators.

## Deploy
A `kustomization.yaml` file exists to launch all required Kubernetes objects for the scenarios defined in the repository. To create run the following.

```
oc new-project llama-serve
oc apply -k kubernetes
```

## Required secrets
To use the Ansible and/or the GitHub MCP server secrets must be provided to connect to the services.

### GitHub PAT
A GitHub personal access token is required to allow for the MCP server to access GitHub. Follow the steps here to aquire a [PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token)

Next encrypt the PAT to be injected into the secret.

```
echo "gh_mysecretpatthathasaccesstoeverything" | base64 -w0
Z2hfbXlzZWNyZXRwYXR0aGF0aGFzYWNjZXNzdG9ldmVyeXRoaW5nCg==
```

Inject the output of the `echo` command into the secret `kubernetes/mcp-servers/github-mcp/github-secret.yaml`.
```
vi kubernetes/mcp-servers/github-mcp/github-secret.yaml
  # Add your PAT here
  token: "Z2hfbXlzZWNyZXRwYXR0aGF0aGFzYWNjZXNzdG9ldmVyeXRoaW5nCg=="
```

Apply the secret to the cluster
```
oc create -n llama-serve -f kubernetes/mcp-servers/github-mcp/github-secret.yaml
```

This will allow for the GitHub MCP server to start now that it has the required credentials.

### Ansible Automation Platform credentials
To use the Ansible Automation Platform MCP server a token and URL must be defined as it relates to the deployed AAP server. Follow the directions to generate a [token](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/access_management_and_authentication/gw-token-based-authentication#assembly-controller-applications)

Next encrypt the token and the URL

```
echo "MYTOKEN" | base64 -w0
Z2hfbXlzZWNyZXRwYXR0aGF0aGFzYWNjZXNzdG9ldmVyeXRoaW5nCg==
echo "https://mycluster.pssk.p1.openshiftapps.com/api/v2" | base64 -w0
aAfdfbXlzZWNyZXRwYXR0aGF0aGFzYWNjZXNzdG9ldmVyeXRoaW5nCg==
```

Inject the output of the `echo` command into the secret `kubernetes/mcp-servers/ansible-mcp/ansible-aap-secret.yaml`.
```
vi kubernetes/mcp-servers/ansible-mcp/ansible-aap-secret.yaml
stringData:
  token: Z2hfbXlzZWNyZXRwYXR0aGF0aGFzYWNjZXNzdG9ldmVyeXRoaW5nCg==
  url: aAfdfbXlzZWNyZXRwYXR0aGF0aGFzYWNjZXNzdG9ldmVyeXRoaW5nCg==
```

Apply the secret to the cluster
```
oc create -n llama-serve -f kubernetes/mcp-servers/ansible-mcp/ansible-aap-secret.yaml
```


## Running Demos and Notebooks

This project uses `uv` as its package manager for the python based notebooks and demo scripts. You can quickly set up your working environment by following these steps:

1) `pip install uv`
2)  `uv sync`
3) `source .venv/bin/activate`

Once you are using the virtual environment, you should be good to run any of the scripts or notebooks in `demos/`.
