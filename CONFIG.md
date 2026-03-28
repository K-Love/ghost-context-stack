# CONFIG.md - Local Configuration Notes

## Telegram Channel
- enabled: true
- dmPolicy: allowlist
- allowFrom: ["6051494477"]  # K-Love (user's Telegram user ID)
- groupPolicy: allowlist
- streaming: partial
- botToken: stored in ~/.openclaw/openclaw.json (redacted in status outputs)
- Gateway restart applied after changes (see logs under /tmp/openclaw/)

## Validation Steps (for future reference)
1. From the allowlisted account (ID 6051494477), send a DM to the bot → should be delivered.
2. From a non-allowlisted account, send a DM → should be ignored/blocked by policy.

## File/Service Pointers
- Config file: ~/.openclaw/openclaw.json
- Gateway service: LaunchAgent ai.openclaw.gateway
- Dashboard: http://127.0.0.1:18789/
- Logs: /tmp/openclaw/openclaw-YYYY-MM-DD.log
