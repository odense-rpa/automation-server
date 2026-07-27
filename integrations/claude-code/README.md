# Claude Code integrations

Optional [Claude Code](https://claude.com/claude-code) skills for people who **deploy or operate**
Automation Server. These are shipped with the product but are **not** installed automatically —
they intentionally live outside `.claude/skills/`, so checking out this repo does not change the
behavior of Claude Code for contributors working on the codebase itself.

If you want to use one, install it into your own Claude Code skills directory:

```bash
# user-level (available in every Claude Code session on your machine)
ln -s "$(pwd)/integrations/claude-code/<skill-name>" ~/.claude/skills/<skill-name>

# or, project-scoped to wherever you manage your deployment (e.g. an ops/IaC repo)
ln -s "$(pwd)/integrations/claude-code/<skill-name>" /path/to/that/repo/.claude/skills/<skill-name>
```

A symlink (rather than a copy) means `git pull` here keeps your installed skill up to date.

## Available skills

- **[`automation-server`](automation-server/)** — administer a running Automation Server instance
  over its REST API (processes, workqueues, sessions, incidents, audit logs). Excludes credentials
  and access-token management by design. See its `README.md` for setup.
