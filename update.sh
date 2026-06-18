#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"

trap 'rm -rf "$TMP"' EXIT

checkout_path() {
  local repo="$1"
  local ref="$2"
  local key="${repo}_${ref}"

  key="${key//[^A-Za-z0-9._-]/_}"

  printf '%s/%s' "$TMP" "$key"
}

ensure_checkout() {
  local repo="$1"
  local ref="$2"
  local checkout

  checkout="$(checkout_path "$repo" "$ref")"

  if [[ ! -d "$checkout/.git" ]]; then
    git clone \
      --depth 1 \
      --filter=blob:none \
      --sparse \
      --branch "$ref" \
      "$repo" \
      "$checkout"
  fi

  printf '%s' "$checkout"
}

sync_skill() {
  local repo="$1"
  local ref="$2"
  local source_path="$3"
  local dest_path="$4"
  local checkout

  checkout="$(ensure_checkout "$repo" "$ref")"

  git -C "$checkout" sparse-checkout add "$source_path"

  mkdir -p "$ROOT/$dest_path"

  rsync -a --delete \
    --exclude '.git' \
    "$checkout/$source_path/" \
    "$ROOT/$dest_path/"
}

# Mattpocock 
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/grill-with-docs" "skills/grill-with-docs"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/improve-codebase-architecture" "skills/improve-codebase-architecture"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/prototype" "skills/prototype"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/tdd" "skills/tdd"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/to-issues" "skills/to-issues"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/to-prd" "skills/to-prd"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/codebase-design" "skills/codebase-design"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/diagnosing-bugs" "skills/diagnosing-bugs"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/domain-modeling" "skills/domain-modeling"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/implement" "skills/implement"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/resolving-merge-conflicts" "skills/resolving-merge-conflicts"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/engineering/triage" "skills/triage"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/productivity/grill-me" "skills/grill-me"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/productivity/grilling" "skills/grilling"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/productivity/handoff" "skills/handoff"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/productivity/writing-great-skills" "skills/writing-great-skills"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/productivity/teach" "skills/teach"
sync_skill "git@github.com:mattpocock/skills.git" "main" "skills/personal/edit-article" "skills/edit-article"

# Deep Research 
sync_skill "git@github.com:199-biotechnologies/claude-deep-research-skill.git" "main" "." "skills/deep-research"

# Opencode Sinmplify
sync_skill "git@github.com:AbdoKnbGit/opencode-simplify.git" "main" "simplify" "skills/simplify"

# Plannotator 
sync_skill "git@github.com:plannotator/effective-html.git" "main" "skills/html-diagram" "skills/html-diagram"
sync_skill "git@github.com:plannotator/effective-html.git" "main" "skills/html-plan" "skills/html-plan"
sync_skill "git@github.com:plannotator/effective-html.git" "main" "skills/html" "skills/html"

mkdir -p skills/pencil-design
curl -Lsf -o  skills/pencil-design/SKILL.md https://unpkg.com/@pencil.dev/cli@latest/SKILL.md 
