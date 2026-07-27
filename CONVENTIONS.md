# General

- Keep your answers terse and compact
- Assume your user is an expert developer with intimate knowledge of the codebase

# Coding Conventions for Python
- Use type hints for all function parameters and returns
- Prefer async/await for I/O operations
- Follow PEP 8 for Python code, 88 character line length
- Format with `uv run ruff format .`; lint with `uv run ruff check .`

## Database access
- New endpoints are `async def`; repositories take an `AsyncSession`
- Never use the sync engine in application code — it exists only for Alembic migrations

## Testing
- New features and bugfixes include pytest coverage
- Run the test suite before opening a PR: `cd backend && uv run pytest`

# Coding Conventions for Javascript

- Use Prettier defaults for JavaScript

# Writing code

When writing code, you MUST follow these principles:

- Code should be easy to read and understand.
- Keep the code as simple as possible. Avoid unnecessary complexity.
- Use meaningful names for variables, functions, etc. Names should reveal intent.
- Functions should be small and do one thing well. They should not exceed a few lines.
- Function names should describe the action being performed.
- Prefer fewer arguments in functions. Ideally, aim for no more than two or three.
- Only use comments when necessary, as they can become outdated. Instead, strive to make the code  self-explanatory.
- When comments are used, they should add useful information that is not readily apparent from the code itself.
- Properly handle errors and exceptions to ensure the software's robustness.
- Use exceptions rather than error codes for handling errors.
- Consider security implications of the code. Implement security best practices to protect against vulnerabilities and attacks.