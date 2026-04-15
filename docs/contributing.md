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

See [Installation](pathname:///automation-server/) for getting the full stack running locally.

For backend-only development:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

For frontend-only development:

```bash
cd frontend
npm install
npm run dev
```

## Questions

For questions or open-ended discussion, use [GitHub Discussions](https://github.com/odense-rpa/automation-server/discussions).
