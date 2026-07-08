#!/usr/bin/env bash
# release.sh — interactive guided release script
# Usage: ./scripts/release.sh <new-version>
# Example: ./scripts/release.sh 0.3.0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Colours ───────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${GREEN}✔${RESET}  $*"; }
warn()    { echo -e "${YELLOW}⚠${RESET}  $*"; }
error()   { echo -e "${RED}✖${RESET}  $*" >&2; }
heading() { echo -e "\n${BOLD}$*${RESET}"; }

confirm() {
  local prompt="${1:-Continue?}"
  echo -e ""
  read -r -p "$(echo -e "${YELLOW}?${RESET}  $prompt [y/N] ")" response
  [[ "$response" =~ ^[Yy]$ ]]
}

abort() {
  echo -e "\n${RED}Aborted.${RESET}"
  exit 1
}

# ── Argument validation ────────────────────────────────────────────────────────

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <new-version>" >&2
  echo "Example: $0 0.3.0" >&2
  exit 1
fi

NEW_VERSION="$1"
TAG="v$NEW_VERSION"

if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  error "'$NEW_VERSION' is not a valid semver version (expected X.Y.Z)"
  exit 1
fi

echo -e "${BOLD}Release $TAG${RESET}"

# ── Step 1: Pre-flight checks ─────────────────────────────────────────────────

heading "Step 1: Pre-flight checks"

cd "$REPO_ROOT"

# Must be on main
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
  warn "Current branch is '$CURRENT_BRANCH' (expected main)"
  confirm "Continue anyway?" || abort
else
  info "Branch: $CURRENT_BRANCH"
fi

# Working tree must be clean
if ! git diff --quiet || ! git diff --cached --quiet; then
  error "Working tree is not clean. Commit or stash your changes first."
  git status --short
  exit 1
fi
info "Working tree is clean"

# Tag must not already exist
if git tag --list "$TAG" | grep -q .; then
  error "Tag $TAG already exists"
  exit 1
fi
info "Tag $TAG does not exist yet"

# Check if remote is ahead
git fetch --quiet origin 2>/dev/null || warn "Could not fetch from origin — continuing without remote check"
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "origin/$CURRENT_BRANCH" 2>/dev/null || echo "unknown")
if [[ "$REMOTE" != "unknown" && "$LOCAL" != "$REMOTE" ]]; then
  warn "Local branch is not in sync with origin/$CURRENT_BRANCH"
  confirm "Continue anyway?" || abort
else
  info "Up to date with origin/$CURRENT_BRANCH"
fi

# ── Step 2: Bump version ──────────────────────────────────────────────────────

heading "Step 2: Bump version to $NEW_VERSION"

confirm "Run bump-version.sh $NEW_VERSION?" || abort

"$SCRIPT_DIR/bump-version.sh" "$NEW_VERSION"

# ── Step 3: Review diff ───────────────────────────────────────────────────────

heading "Step 3: Review changes"

echo ""
git diff

confirm "Changes look good — proceed with commit?" || abort

# ── Step 4: Commit ────────────────────────────────────────────────────────────

heading "Step 4: Commit"

git add \
  backend/pyproject.toml \
  backend/uv.lock \
  worker/pyproject.toml \
  worker/uv.lock \
  frontend/package.json \
  backend/Dockerfile \
  frontend/Dockerfile \
  worker/Dockerfile \
  docker-compose.yml \
  worker/build-standard.sh \
  README.md

git commit -m "Release $TAG"
info "Committed: Release $TAG"

# ── Step 5: Tag ───────────────────────────────────────────────────────────────

heading "Step 5: Create annotated tag $TAG"

git tag -a "$TAG" -m "Release $TAG"
info "Created tag $TAG"

# ── Step 6: Push ─────────────────────────────────────────────────────────────

heading "Step 6: Push"

echo "  This will push the commit and tag to origin/$CURRENT_BRANCH."
echo "  Pushing the tag triggers the Docker image build CI workflow."
echo ""
confirm "Push commit + tag to origin?" || {
  warn "Not pushed. Run the following when ready:"
  echo "    git push origin $CURRENT_BRANCH"
  echo "    git push origin $TAG"
  exit 0
}

git push origin "$CURRENT_BRANCH"
git push origin "$TAG"

info "Pushed commit and tag $TAG to origin"
echo -e "\n${GREEN}${BOLD}Release $TAG complete.${RESET} CI is building Docker images."
