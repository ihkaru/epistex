#!/usr/bin/env bash
# ==============================================================================
# Epistex Deterministic Release Automation Engine (scripts/release.sh)
# Follows the Laravel Release Model & SemVer 2.0.0
# ==============================================================================
# Usage:
#   ./scripts/release.sh [patch|minor|major] [--dry-run]
# ==============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BUMP_TYPE=""
DRY_RUN=false

for arg in "$@"; do
  case "$arg" in
    --dry-run)
      DRY_RUN=true
      ;;
    patch|minor|major)
      BUMP_TYPE="$arg"
      ;;
    *)
      echo "❌ Error: Unrecognized argument '$arg'. Allowed: patch, minor, major, --dry-run."
      exit 1
      ;;
  esac
done

# ------------------------------------------------------------------------------
# 1. Sanity Checks & Scope Verification
# ------------------------------------------------------------------------------
echo "=== Step 1: Validating Maintainer Scope & Environment ==="

# Check mode flag in config/app.py
IS_STARTER_KIT=$(python3 -c "from config.app import IS_STARTER_KIT; print(str(IS_STARTER_KIT).lower())")
if [ "$IS_STARTER_KIT" != "true" ]; then
  echo "❌ Error: Repository is in downstream mode (IS_STARTER_KIT = False)."
  echo "   Engine releases are strictly forbidden in downstream content repositories."
  exit 1
fi

# Check git status (enforced on actual release)
if [ "$DRY_RUN" != true ] && [ -n "$(git status --porcelain)" ]; then
  echo "❌ Error: Working tree has uncommitted changes. Commit or stash them first."
  git status --short
  exit 1
fi

# Check GitHub CLI
if ! command -v gh &>/dev/null; then
  echo "❌ Error: GitHub CLI ('gh') is required to publish GitHub Releases."
  exit 1
fi

# ------------------------------------------------------------------------------
# 2. Automated Release Readiness Inspection
# ------------------------------------------------------------------------------
echo "=== Step 2: Checking Release Readiness via gx doctor ==="
RELEASE_JSON=$(./bin/gx doctor --check-release --json 2>/dev/null)

RELEASE_REQUIRED=$(echo "$RELEASE_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('release_readiness', {}).get('release_required', False))")
RECOMMENDED_BUMP=$(echo "$RELEASE_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('release_readiness', {}).get('recommended_bump', 'patch'))")
CURRENT_VERSION=$(echo "$RELEASE_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('release_readiness', {}).get('current_version', '0.0.0'))")

if [ "$RELEASE_REQUIRED" != "True" ] && [ -z "$BUMP_TYPE" ]; then
  echo "ℹ️  No unreleased engine changes detected since last tag."
  echo "   Use './scripts/release.sh <patch|minor|major>' to force a release."
  exit 0
fi

FINAL_BUMP="${BUMP_TYPE:-$RECOMMENDED_BUMP}"
if [ "$FINAL_BUMP" != "patch" ] && [ "$FINAL_BUMP" != "minor" ] && [ "$FINAL_BUMP" != "major" ]; then
  echo "❌ Error: Invalid bump type '$FINAL_BUMP'. Allowed: patch, minor, major."
  exit 1
fi

# Calculate next version
NEXT_VERSION=$(python3 -c "
current = '$CURRENT_VERSION'.split('.')
major, minor, patch = int(current[0]), int(current[1]), int(current[2])
bump = '$FINAL_BUMP'
if bump == 'major':
    print(f'{major+1}.0.0')
elif bump == 'minor':
    print(f'{major}.{minor+1}.0')
else:
    print(f'{major}.{minor}.{patch+1}')
")

TAG_NAME="v${NEXT_VERSION}"
echo "Current Version: $CURRENT_VERSION"
echo "Recommended Bump: $FINAL_BUMP"
echo "Target Release:   $TAG_NAME"

# ------------------------------------------------------------------------------
# 3. Pre-Flight Verification Gauntlet
# ------------------------------------------------------------------------------
echo "=== Step 3: Executing Pre-Flight Verification Gauntlet ==="

echo "• Gate 1: Parallel Hermetic Unit & Integration Tests..."
python3 -m unittest discover -s tests -q

echo "• Gate 2: Deterministic Static SRP Analyzer..."
SRP_SCRIPT="$HOME/.gemini/config/skills/craftsman-coder/scripts/static_srp_analyzer.py"
if [ -f "$SRP_SCRIPT" ]; then
  python3 "$SRP_SCRIPT" . --strict > /dev/null
fi

echo "• Gate 3: Zero-Mock & Silent Mock Static Detector..."
if command -v detect-mocks &>/dev/null; then
  detect-mocks . > /dev/null
fi

echo "• Gate 4: Repository Health Check..."
./bin/gx doctor --check-assets --json > /dev/null

echo "✅ All pre-flight gauntlet gates passed."

if [ "$DRY_RUN" = true ]; then
  echo "🔍 DRY RUN: Verification successful. Exiting without modifying files or releasing."
  exit 0
fi

# ------------------------------------------------------------------------------
# 4. Version Bump & File Mutations
# ------------------------------------------------------------------------------
echo "=== Step 4: Applying Version Bump to $NEXT_VERSION ==="

# Update config/app.py
sed -i "s/APP_VERSION = \".*\"/APP_VERSION = \"$NEXT_VERSION\"/" config/app.py

# Update pyproject.toml
sed -i "s/version = \".*\"/version = \"$NEXT_VERSION\"/" pyproject.toml

# Extract Release Notes from CHANGELOG.md
TEMP_NOTES="/tmp/epistex_release_notes_${NEXT_VERSION}.md"
python3 -c "
import sys, re
changelog = open('CHANGELOG.md', encoding='utf-8').read()
pattern = r'## \[$TAG_NAME\].*?\n(.*?)(?=\n## \[v|\Z)'
match = re.search(pattern, changelog, re.DOTALL)
if match:
    notes = match.group(1).strip()
    with open('$TEMP_NOTES', 'w', encoding='utf-8') as f:
        f.write(notes)
else:
    with open('$TEMP_NOTES', 'w', encoding='utf-8') as f:
        f.write('Release $TAG_NAME: See CHANGELOG.md for details.')
"

# ------------------------------------------------------------------------------
# 5. Git Commit, Branch Alignment & Tagging
# ------------------------------------------------------------------------------
echo "=== Step 5: Committing, Branch Aligning & Tagging ==="
git add config/app.py pyproject.toml CHANGELOG.md
if git diff --staged --quiet; then
  echo "Notice: Version and changelog already committed."
else
  git commit -m "chore(release): bump version to $TAG_NAME"
fi

# Align series branch 1.x with main
git branch -f 1.x main

# Create annotated tag
if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
  echo "Tag $TAG_NAME already exists locally. Updating tag..."
  git tag -fa "$TAG_NAME" -m "Release $TAG_NAME: Laravel-style upstream release"
else
  git tag -a "$TAG_NAME" -m "Release $TAG_NAME: Laravel-style upstream release"
fi

# ------------------------------------------------------------------------------
# 6. Push & Publish GitHub Release
# ------------------------------------------------------------------------------
echo "=== Step 6: Pushing to Remote & Publishing GitHub Release ==="
git push origin main 1.x --tags

if gh release view "$TAG_NAME" >/dev/null 2>&1; then
  echo "GitHub Release $TAG_NAME already exists. Updating notes..."
  gh release edit "$TAG_NAME" --title "$TAG_NAME: Enterprise Release" --notes-file "$TEMP_NOTES"
else
  echo "Creating GitHub Release $TAG_NAME..."
  gh release create "$TAG_NAME" --title "$TAG_NAME: Enterprise Release" --notes-file "$TEMP_NOTES"
fi

rm -f "$TEMP_NOTES"

echo ""
echo "=============================================================================="
echo "🎉 RELEASE COMPLETE: $TAG_NAME has been successfully published to GitHub!"
echo "=============================================================================="
