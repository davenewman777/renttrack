---
title: RentTrack
description: Desktop rent tracking and payment receipt application
---

RentTrack is a desktop application for tracking rental properties, tenants,
leases, payments, and receipts.

## Email receipt configuration

Receipt delivery reads SMTP settings from `RENTTRACK_SMTP_*` environment
variables or `data/email_config.json`. The JSON file uses these keys:

```json
{
  "host": "smtp-relay.brevo.com",
  "port": 587,
  "username": "smtp-login",
  "password": "smtp-key",
  "from_address": "receipts@example.com",
  "use_tls": true,
  "sender_name": "Property Manager"
}
```

Keep `data/email_config.json` private because it contains SMTP credentials.

### Brevo unauthorized IP errors

Brevo can restrict SMTP access to authorized public IP addresses. If sending
fails with `525 5.7.1 Unauthorized IP address`, open the Brevo security
settings, authorize the computer's current public IP address, and retry.
Dynamic public IP addresses may need to be authorized again after they change.
