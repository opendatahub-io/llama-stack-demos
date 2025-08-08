# Deploy GitHub MCP Server on OpenShift Container Platform

This document provides instructions for deploying the GitHub MCP server on the OpenShift Container Platform. You can find the official GitHub MCP server repository here: [GitHub MCP Server](https://github.com/modelcontextprotocol-archived/servers-archived/tree/main/src/github).

Additionally, this guide includes steps to test the integration of the GitHub MCP server with the Llama Stack agent.

## 🛠️ Prerequisites
You will need the following installed on your local machine:

- `podman`
- `oc`

## Step 1: Building the Containerfile

You will need to first build a container image using the `Containerfile` and can do this by using `podman`. To build the container image from the current directory:
```
cd mcp-containerfile
podman build -t github-mcp-server:latest -f Containerfile
```
If running on a Mac:
```
podman build -t github-mcp-server:latest --platform="linux/amd64" -f Containerfile .
```

## Step 2: Pushing the container image to Quay

Next, you will need to push your container image to a public image repository like [quay.io](https://quay.io/). Make sure you create an account on quay.io, if you don't have one already. Once you have an account, you will need to login:

```
podman login -u=<user_name> -p=<pass_word> quay.io
```

Once you're logged in successfully, you can now push your image by first tagging your local image:

```
podman tag localhost/github-mcp-server:latest quay.io/<username>/github-mcp-server:latest
```

Then you can push to your quay registry:

```
podman push quay.io/<username>/github-mcp-server:latest
```

## Step 3: Deploying on OpenShift
1. **Log in to OpenShift**:
     - Log in to the OpenShift web UI, click on your user ID in the top-right corner, and select "Copy Login Command."
     - ![Click Copy Login Command](./images/copy_login_command.png)
     - Paste the copied command into your terminal to log in to OpenShift via CLI:
       ```bash
       oc login --token=... --server=https://your.openshift.cluster.url
       ```

2. **Create or Use an Existing Project**:
     - Create a new project or navigate to an existing one:
       ```bash
       oc project project_name
       ```
       here we navigate to our project `oc project llama-serve`

3. **Modify YAML Files**:
     - Update the provided YAML files to deploy the GitHub MCP server using the `oc` command.
     - **Steps to Modify**:
       1. Change the project name and MCP server name to your desired values.
            Example:
            - Project name: `llama-serve`
            - MCP server name: `github-mcp-server`
       2. Since the deployment uses community MCP servers published on GitHub, create a `secret.yaml` file to store your personal GitHub token for accessing the MCP server Docker image.

          > **Note:** Create a Personal Access Token in GitHub by navigating to **Settings > Developer settings > Personal access tokens**, assigning required scopes, and copying it securely into `secret.yaml`. Do not share it publicly.

       3. Ensure the secret name in `secret.yaml` matches the one in `deployment.yaml`.
       5. Double-check all YAML files to ensure they are correctly configured.

4. **Deploy the MCP Server**:
     - Apply the secrets:
       ```bash
       oc apply -f ../../kubernetes/mcp-servers/github-mcp/github-secret.yaml
       ```
     - Deploy the application:
       ```bash
       oc apply -f ../../kubernetes/mcp-servers/github-mcp/github-deployment.yaml
       ```

5. **Verify Deployment**:
     - Check the OpenShift web console to confirm that the `github-mcp-server1` pod is up and running.


## Test if the GitHub MCP Server is Correctly Configured

1. Navigate to `0_simple_agent.py` and
     - copy MCP endpoint and add it to "REMOTE_MCP_URL" environment. REMOTE_MCP_URL="http://ip:port/sse"
          > **Note:** how to find mcp ip and port? go to openshift web console ![ip Image](./images/ipaddress.png)
     - register the GitHub MCP tools:
       ```
       if "mcp::github" not in registered_toolgroups:
               # Register MCP tools
               client.toolgroups.register(
                     toolgroup_id="mcp::github",
                     provider_id="model-context-protocol",
                     mcp_endpoint={"uri": mcp_url},
               )
               logger.info(f"Successfully registered MCP tool group: mcp::github")
       mcp_tools = [t.identifier for t in client.tools.list(toolgroup_id="mcp::github")]
       ```

     - Confirm that the Llama Stack agent has the GitHub MCP tools configured with `tools=["mcp::github"]`.

     - Example user prompt:
       ```
       Describe https://github.com/modelcontextprotocol-archived/servers-archived/tree/main/src/github repository
       ```

2. Verify the output:
     - run modified simple agent script `python app/src/0_simple_agent.py -r -s -a`
     - Example output:
       ![Deployment Image](./images/test.png)

### How to Unregister MCP Tool Groups

To unregister MCP tool groups, use the following code snippet:
```
client.toolgroups.unregister(toolgroup_id="mcp::github")
```
