#!/usr/bin/env bash
# bump-version.sh — update version strings across the repo
# Usage: ./scripts/bump-version.sh <new-version>
# Example: ./scripts/bump-version.sh 0.3.0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Argument validation ────────────────────────────────────────────────────────

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <new-version>" >&2
  echo "Example: $0 0.3.0" >&2
  exit 1
fi

NEW_VERSION="$1"

if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: '$NEW_VERSION' is not a valid semver version (expected X.Y.Z)" >&2
  exit 1
fi

# ── Read current version from canonical source ─────────────────────────────────

CURRENT_VERSION=$(grep -m1 '^version = ' "$REPO_ROOT/backend/pyproject.toml" | sed 's/version = "\(.*\)"/\1/')

if [[ -z "$CURRENT_VERSION" ]]; then
  echo "Error: could not read current version from backend/pyproject.toml" >&2
  exit 1
fi

echo "Bumping version: $CURRENT_VERSION → $NEW_VERSION"
echo ""

# ── Helper: sed in-place (cross-platform) ─────────────────────────────────────

sedi() {
  if sed --version 2>/dev/null | grep -q GNU; then
    sed -i "$@"
  else
    sed -i '' "$@"  # macOS
  fi
}

CHANGED_FILES=()

# ── pyproject.toml files ───────────────────────────────────────────────────────

sedi "s/^version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" "$REPO_ROOT/backend/pyproject.toml"
CHANGED_FILES+=("backend/pyproject.toml")

sedi "s/^version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" "$REPO_ROOT/worker/pyproject.toml"
CHANGED_FILES+=("worker/pyproject.toml")

# ── frontend/package.json ──────────────────────────────────────────────────────

sedi "s/\"version\": \"$CURRENT_VERSION\"/\"version\": \"$NEW_VERSION\"/" "$REPO_ROOT/frontend/package.json"
CHANGED_FILES+=("frontend/package.json")

# ── Dockerfiles ───────────────────────────────────────────────────────────────

sedi "s/version=\"$CURRENT_VERSION\"/version=\"$NEW_VERSION\"/g" "$REPO_ROOT/backend/Dockerfile"
CHANGED_FILES+=("backend/Dockerfile")

sedi "s/version=\"$CURRENT_VERSION\"/version=\"$NEW_VERSION\"/g" "$REPO_ROOT/frontend/Dockerfile"
CHANGED_FILES+=("frontend/Dockerfile")

sedi "s/version=\"$CURRENT_VERSION\"/version=\"$NEW_VERSION\"/g" "$REPO_ROOT/worker/Dockerfile"
CHANGED_FILES+=("worker/Dockerfile")

# ── docker-compose.yml image tags ─────────────────────────────────────────────

sedi "s/:v$CURRENT_VERSION/:v$NEW_VERSION/g" "$REPO_ROOT/docker-compose.yml"
CHANGED_FILES+=("docker-compose.yml")

# ── worker build scripts ───────────────────────────────────────────────────────

sedi "s/:$CURRENT_VERSION/:$NEW_VERSION/g" "$REPO_ROOT/worker/build-standard.sh"
CHANGED_FILES+=("worker/build-standard.sh")


# ── README.md badge ───────────────────────────────────────────────────────────

sedi "s/version-$CURRENT_VERSION-blue/version-$NEW_VERSION-blue/" "$REPO_ROOT/README.md"
CHANGED_FILES+=("README.md")

# ── Sync lock files ───────────────────────────────────────────────────────────

echo "Syncing backend lock file..."
(cd "$REPO_ROOT/backend" && uv lock)

echo "Syncing worker lock file..."
(cd "$REPO_ROOT/worker" && uv lock)

echo "Syncing frontend lock file..."
(cd "$REPO_ROOT/frontend" && npm install --package-lock-only --ignore-scripts)

# ── Summary ───────────────────────────────────────────────────────────────────

echo ""
echo "Done. Updated files:"
for f in "${CHANGED_FILES[@]}"; do
  echo "  $f"
done
echo "  backend/uv.lock"
echo "  worker/uv.lock"
echo "  frontend/package-lock.json"
