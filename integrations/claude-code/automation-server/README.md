# automation-server Claude Code skill

Lets [Claude Code](https://claude.com/claude-code) administer a running Automation Server instance
over its REST API — list/trigger processes, manage workqueues and workitems, inspect sessions,
triage incidents, and read audit logs. Credentials and access-token endpoints are hard-blocked by
design; this skill never handles secrets or mints auth material.

This skill is **not auto-loaded** just by checking out this repo. Install it explicitly:

```bash
ln -s "$(pwd)/integrations/claude-code/automation-server" ~/.claude/skills/automation-server
```

(A symlink keeps it in sync with this repo. A plain `cp -r` works too if you'd rather have a
frozen local copy.)

## Configure

Point it at the instance you want to administer:

```bash
export ATS_BASE_URL=https://your-automation-server-host/api
export ATS_TOKEN=<a bearer token minted via the Automation Server UI>
```

`ATS_TOKEN` should be a real access token — never a shared/default credential — and should not be
committed anywhere. See the main [`README.md`](../../../README.md) / [`docs/`](../../../docs) for
how to deploy an instance and mint access tokens.

## What's in here

- `SKILL.md` — the skill definition Claude Code reads (setup, safety rules, recipes).
- `scripts/ats` — the underlying HTTP client (Python 3 stdlib, no dependencies).
- `references/endpoints.md` — full REST API reference for the endpoints this skill uses.

For the full endpoint catalog and behavior, read `SKILL.md`.
