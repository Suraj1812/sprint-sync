# Integration Developer Guide

## Connector Interface

```python
class IntegrationConnector(ABC):
    async def execute(self, config: dict) -> Any
    async def health(self) -> dict
```

## Adding a Connector

1. Implement `IntegrationConnector` in `app/automation/connectors/{provider}.py`.
2. Register in `ConnectorRegistry`.
3. Use it in a workflow step with `action: "connector.<provider>"`.

## Built-in Connectors

- `slack` (stub)
- `github` (stub)

## Integration Connections

`IntegrationConnection` stores OAuth tokens for user-installed apps. Use this for Slack, GitHub, Google, etc.

## SDKs

OpenAPI schema is exposed at `/api/v1/openapi.json`. Generate SDKs with:

```bash
openapi-generator-cli generate -i openapi.json -g typescript-angular -o sdk/ts
openapi-generator-cli generate -i openapi.json -g python -o sdk/python
```

## Developer Portal

Admin pages provide:
- API key management
- OAuth app registration
- Webhook configuration
- Workflow explorer
