# Communication Provider Integration Guide

## Email Providers

### Console

Default for local development. Logs emails to stdout.

```
EMAIL_PROVIDER=console
```

### Resend

```
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_...
```

### SendGrid

```
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG....
```

### Postmark

```
EMAIL_PROVIDER=postmark
POSTMARK_API_KEY=...
```

### Amazon SES

Currently a stub. Add `boto3` calls in `app/communications/providers/ses.py` to enable.

## Adding a Provider

1. Create `app/communications/providers/{name}.py`.
2. Subclass `EmailProvider` and implement `send` and `health`.
3. Register in `EmailProviderRegistry`.
4. Set `EMAIL_PROVIDER={name}`.

## Push / SMS

`PushProvider` and `SMSProvider` interfaces exist. Register implementations in the same registry pattern when adding FCM, APNs, Twilio, etc.
