#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
MATT_REPO="https://github.com/mattpocock/skills.git"
MATT_REF="v1.3.1"
MATT_COMMIT="24fe0ef7737efae15c87225755e9f6f5965e4888"
MATT_ONLY=false
DRY_RUN=false

for option in "$@"; do
  case "$option" in
    --matt-only) MATT_ONLY=true ;;
    --dry-run) DRY_RUN=true ;;
    --help)
      printf 'Usage: %s [--matt-only] [--dry-run]\n' "$0"
      printf '  --matt-only  Update only the pinned Matt Pocock collection.\n'
      printf '  --dry-run    Show file changes without modifying the repository.\n'
      exit 0
      ;;
    *) printf 'Unknown option: %s\n' "$option" >&2; exit 1 ;;
  esac
done

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
      --branch "$ref" \
      "$repo" \
      "$checkout" >&2
  fi

  printf '%s' "$checkout"
}

sync_directory() {
  local source="$1"
  local destination="$2"
  local options=(-a --exclude '.git')

  if [[ "${3:-true}" == true ]]; then
    options+=(--delete)
  fi

  if "$DRY_RUN"; then
    options+=(--dry-run --itemize-changes)
  else
    mkdir -p "$destination"
  fi

  rsync "${options[@]}" "$source/" "$destination/"
}

sync_skill() {
  local repo="$1"
  local ref="$2"
  local source_path="$3"
  local dest_path="$4"
  local checkout

  checkout="$(ensure_checkout "$repo" "$ref")"

  sync_directory "$checkout/$source_path" "$ROOT/$dest_path"
}

# Validate the entire Matt collection before changing any destination.
MATT_SKILLS=(
  skills/engineering/grill-with-docs
  skills/engineering/improve-codebase-architecture
  skills/engineering/prototype
  skills/engineering/tdd
  skills/engineering/to-tickets
  skills/engineering/to-spec
  skills/engineering/codebase-design
  skills/engineering/diagnosing-bugs
  skills/engineering/domain-modeling
  skills/engineering/implement
  skills/engineering/triage
  skills/productivity/grill-me
  skills/productivity/grilling
  skills/productivity/handoff
  skills/productivity/writing-for-agents
  skills/productivity/teach
  skills/engineering/setup-matt-pocock-skills
  skills/engineering/code-review
  skills/engineering/pr
  skills/engineering/retro
)

matt_checkout="$(ensure_checkout "$MATT_REPO" "$MATT_REF")"
if [[ "$(git -C "$matt_checkout" rev-parse HEAD)" != "$MATT_COMMIT" ]]; then
  printf 'Matt Pocock ref %s does not match the pinned commit %s.\n' "$MATT_REF" "$MATT_COMMIT" >&2
  exit 1
fi

for source_path in "${MATT_SKILLS[@]}"; do
  if [[ ! -f "$matt_checkout/$source_path/SKILL.md" ]]; then
    printf 'Missing Matt Pocock skill source: %s\n' "$source_path" >&2
    exit 1
  fi
done

for source_path in "${MATT_SKILLS[@]}"; do
  sync_directory "$matt_checkout/$source_path" "$ROOT/skills/${source_path##*/}"
done

if "$MATT_ONLY"; then
  exit 0
fi

# Deep Research 
sync_skill "git@github.com:199-biotechnologies/claude-deep-research-skill.git" "main" "." "skills/deep-research"

# Opencode Sinmplify
sync_skill "git@github.com:AbdoKnbGit/opencode-simplify.git" "main" "simplify" "skills/simplify"

# Plannotator 
sync_skill "git@github.com:plannotator/effective-html.git" "main" "skills/html-diagram" "skills/html-diagram"
sync_skill "git@github.com:plannotator/effective-html.git" "main" "skills/html-plan" "skills/html-plan"
sync_skill "git@github.com:plannotator/effective-html.git" "main" "skills/html" "skills/html"

sync_skill "git@github.com:Magdoub/claude-wireframe-skill.git" "main" "." "skills/wireframe"
sync_skill "git@github.com:elifsue/wireframe-prototyper-skill.git" "main" "." "skills/wireframe-prototyper-skill"


mkdir -p "$TMP/pencil-design"
curl -Lsf -o "$TMP/pencil-design/SKILL.md" https://unpkg.com/@pencil.dev/cli@latest/SKILL.md
sync_directory "$TMP/pencil-design" "$ROOT/skills/pencil-design" false
