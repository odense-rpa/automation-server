---
title: Contributing
sidebar_position: 99
description: How to contribute to Automation Server.
---

Contributions are welcome. Here's how to get involved.

## Reporting Issues

Check the [existing issues](https://github.com/odense-rpa/automation-server/issues) first to see if your bug or idea is already tracked. If not, open a new issue with as much detail as possible.

## Suggesting Features

Open an issue to discuss your idea before building it. This avoids wasted effort and makes sure the feature fits the project's direction.

## Submitting Code

1. Fork the repository and create a feature branch from `development`
2. Make your changes and add tests
3. Run the test suite: `cd backend && uv run pytest`
4. Submit a pull request against the `development` branch

## Development Setup

Clone the repository and set up your environment:

```bash
git clone https://github.com/odense-rpa/automation-server.git
cd automation-server
cp .env.example .env
```

Start the stack using `docker compose up` — without specifying a compose file, Docker Compose automatically merges `docker-compose.override.yml` on top of the base, giving you local builds and hot-reloading for all services:

```bash
docker compose up --build
```

A VS Code workspace file is included. Open it to get the full multi-folder setup with recommended extensions and settings:

```bash
code ats.code-workspace
```

## Questions

For questions or open-ended discussion, use [GitHub Discussions](https://github.com/odense-rpa/automation-server/discussions).
