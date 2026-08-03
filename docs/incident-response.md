# Incident Response Notes

## Severity Levels

1. **Critical** — data breach, full service compromise, credential leak.
2. **High** — authentication bypass, unauthorized admin access, mass token leak.
3. **Medium** — rate-limit evasion, non-sensitive data exposure.
4. **Low** — missing headers, informational findings.

## Immediate Response

1. **Identify** — use correlation IDs in logs to trace the request chain.
2. **Contain** — rotate `SECRET_KEY`, revoke refresh tokens in Redis, disable affected users.
3. **Eradicate** — patch the vulnerability, update dependencies.
4. **Recover** — restore from encrypted backups if necessary.
5. **Review** — post-mortem and update this model.

## Useful Commands

```bash
# Revoke all refresh tokens for a user
redis-cli --scan --pattern "refresh_token:<user_id>:*" | xargs redis-cli del

# Rotate secrets
# 1. Generate new SECRET_KEY in your secret manager.
# 2. Redeploy services with the new key.
# 3. Existing access tokens will expire naturally; force re-login for affected users.
```
