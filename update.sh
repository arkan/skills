#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"

trap 'rm -rf "$TMP"' EXIT

sync_skill() {
  local repo="$1"
  local ref="$2"
  local source_path="$3"
  local dest_path="$4"

  local checkout="$TMP/repo"

  rm -rf "$checkout"

  git clone \
    --depth 1 \
    --filter=blob:none \
    --sparse \
    --branch "$ref" \
    "$repo" \
    "$checkout"

  git -C "$checkout" sparse-checkout set "$source_path"

  mkdir -p "$ROOT/$dest_path"

  rsync -a --delete \
    --exclude '.git' \
    "$checkout/$source_path/" \
    "$ROOT/$dest_path/"
}

sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/grill-with-docs" "skills/grill-with-docs"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/improve-codebase-architecture" "skills/improve-codebase-architecture"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/prototype" "skills/prototype"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/tdd" "skills/tdd"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/to-issues" "skills/to-issues"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/to-prd" "skills/to-prd"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/diagnose" "skills/diagnose"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/triage" "skills/triage"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/zoom-out" "skills/zoom-out"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/productivity/grill-me" "skills/grill-me"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/productivity/handoff" "skills/handoff"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/productivity/write-a-skill" "skills/write-a-skill"
sync_skill "git@github.com:199-biotechnologies/claude-deep-research-skill.git" "main" "." "skills/deep-research"

