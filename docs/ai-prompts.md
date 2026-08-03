# Prompt Authoring Guide

## Prompt Model

- `Prompt` — named template with variables and active flag.
- `PromptVersion` — versioned `system` message and `user_template`.
- `default_version_id` — which version is used when `version` is not specified.

## Variable Interpolation

Use Python `string.Template` syntax: `$name` or `${name}`.

Example user template:

```text
You are an expert in $domain. Answer: $question
```

Pass `prompt_variables: {"domain": "kubernetes", "question": "..."}` to `/ai/chat`.

## API

- `POST /api/v1/ai/prompts` — create a prompt and its first version.
- `GET /api/v1/ai/prompts` — list prompts.
- `POST /api/v1/ai/chat` with `prompt: "name"` and `prompt_variables` — render and run.

## Best Practices

- Version every material change; do not edit in place.
- Keep the system message stable and put dynamic content in `user_template`.
- Use `is_active` to deprecate old prompts.
