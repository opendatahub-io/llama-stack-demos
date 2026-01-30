# Creating Model Context Protocol (MCP) Server for Slack on OpenShift Container Platform (OCP)

This document is a quick walkthrough of how to deploy the slack MCP server on OCP from:

* https://github.com/modelcontextprotocol/servers-archived/

## Supported Slack Tools

1. `slack_list_channels`
   - List public channels in the workspace
   - Optional inputs:
     - `limit` (number, default: 100, max: 200): Maximum number of channels to return
     - `cursor` (string): Pagination cursor for next page
   - Returns: List of channels with their IDs and information

2. `slack_post_message`
   - Post a new message to a Slack channel
   - Required inputs:
     - `channel_id` (string): The ID of the channel to post to
     - `text` (string): The message text to post
   - Returns: Message posting confirmation and timestamp

3. `slack_reply_to_thread`
   - Reply to a specific message thread
   - Required inputs:
     - `channel_id` (string): The channel containing the thread
     - `thread_ts` (string): Timestamp of the parent message
     - `text` (string): The reply text
   - Returns: Reply confirmation and timestamp

4. `slack_add_reaction`
   - Add an emoji reaction to a message
   - Required inputs:
     - `channel_id` (string): The channel containing the message
     - `timestamp` (string): Message timestamp to react to
     - `reaction` (string): Emoji name without colons
   - Returns: Reaction confirmation

5. `slack_get_channel_history`
   - Get recent messages from a channel
   - Required inputs:
     - `channel_id` (string): The channel ID
   - Optional inputs:
     - `limit` (number, default: 10): Number of messages to retrieve
   - Returns: List of messages with their content and metadata

6. `slack_get_thread_replies`
   - Get all replies in a message thread
   - Required inputs:
     - `channel_id` (string): The channel containing the thread
     - `thread_ts` (string): Timestamp of the parent message
   - Returns: List of replies with their content and metadata


7. `slack_get_users`
   - Get list of workspace users with basic profile information
   - Optional inputs:
     - `cursor` (string): Pagination cursor for next page
     - `limit` (number, default: 100, max: 200): Maximum users to return
   - Returns: List of users with their basic profiles

8. `slack_get_user_profile`
   - Get detailed profile information for a specific user
   - Required inputs:
     - `user_id` (string): The user's ID
   - Returns: Detailed user profile information

## Setup

### Setting up the Slack bot

Please follow the steps to create and config your slack bot. You will need access to a Slack workspace where you can configure a slack app/bot in order to interact with the MCP server.
1. Create a Slack App:
   - Visit the [Slack Apps page](https://api.slack.com/apps)
   - Click "Create New App"
   - Choose "From scratch"
   - Name your app and select your workspace

2. Configure Bot Token Scopes:
   Navigate to "OAuth & Permissions" and add these scopes:
   - `channels:history` - View messages and other content in public channels
   - `channels:read` - View basic channel information
   - `chat:write` - Send messages as the app
   - `reactions:write` - Add emoji reactions to messages
   - `users:read` - View users and their basic information

4. Install App to Workspace:
   - Click "Install to Workspace" and authorize the app
   - Save the "Bot User OAuth Token" that starts with `xoxb-`

5. Get your Team ID (starts with a `T`) by following [this guidance](https://slack.com/help/articles/221769328-Locate-your-Slack-URL-or-ID#find-your-workspace-or-org-id)

### Setting up on OCP
#### Usage with Quay and Podman

You will first need to build an image for the Slack MCP server from the `Containerfile`. Follow the steps below to create and image with Podman and host it on `Quay.io`.
1. Navigate to quay.io and login through SSO.
2. Create a repository on quay, make sure to select to **public** to your images.
3. Build and push your image through podman. (If you don't have podman installed, you can download from here: https://podman-desktop.io/Download).

Build your image with:

```
cd mcp-containerfile
podman build -t slack-mcp-server:latest --platform="linux/amd64" -f Containerfile .
```

Push your image with:

`podman push <image id> quay.io/<your quay id>/<image_name>:latest`

If the build is successful you should see:

`Writing manifest to image destination`

#### OCP Deployment
1. Select or create the proper namespace/project for your deployment and proceed with creation.
2. Specify the pod managements and application workload. Make sure to select proper quay.io image.
3. After deployment, you should be able to see your deployment status on OCP.

### Troubleshooting

If you encounter permission errors, verify that:
1. All required scopes are added to your Slack app
2. The app is properly installed to your workspace
3. The tokens and workspace ID are correctly copied to your configuration
4. The app has been added to the channels it needs to access
