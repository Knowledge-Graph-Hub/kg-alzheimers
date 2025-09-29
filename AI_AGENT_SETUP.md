# AI Agent Setup Instructions

This repository has been configured with a GitHub Actions workflow for AI agent integration using the Dragon AI Agent.

## Files Created

1. **`.github/workflows/ai-agent.yml`** - GitHub Actions workflow that triggers the AI agent on issue/PR mentions
2. **`.config/goose/config.yaml`** - Configuration for the goose AI agent
3. **`.goosehints`** - Symlink to CLAUDE.md containing project-specific instructions

## Required Repository Secrets

To complete the setup, you need to configure the following secrets in your GitHub repository settings:

**Navigate to:** `https://github.com/YOUR_USERNAME/kg-alzheimers/settings/secrets/actions`

### Required Secrets:

1. **`ANTHROPIC_API_KEY`**
   - Your Anthropic API key for Claude access
   - Get from: https://console.anthropic.com/

2. **`CBORG_API_KEY`** 
   - API key for the CBORG LiteLLM proxy
   - This enables access to multiple AI models through a unified interface

3. **`PAT_FOR_PR`**
   - Personal Access Token for GitHub operations
   - Needs permissions: `contents:write`, `pull-requests:write`, `issues:write`
   - Generate at: https://github.com/settings/tokens

## How It Works

- When someone mentions `@alzassistant` in issues, PRs, or comments, the workflow triggers
- The AI agent can read the context, understand requests, and create pull requests with changes
- The agent uses the instructions in `.goosehints` (linked to CLAUDE.md) to understand the project
- Fallback controller is set to `jtr4v` for permissions management

## Testing

Once secrets are configured, test by:
1. Creating an issue
2. Commenting with `@alzassistant help me with X`
3. The agent should respond with a PR addressing the request

## Configuration Notes

- Uses `anthropic/claude-sonnet` model via CBORG proxy
- Agent name: "alzassistant"
- Branch prefix: "alzassistant"
- Robot version: v1.9.7