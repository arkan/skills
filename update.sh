#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
MATT_REPO="https://github.com/mattpocock/skills.git"
MATT_REF="v1.3.1"
MATT_COMMIT="24fe0ef7737efae15c87225755e9f6f5965e4888"
EMIL_REPO="https://github.com/emilkowalski/skills.git"
EMIL_COMMIT="e8a175de22ae1e49370fc144c1f3bb9aeedf988d"
JAKUB_REPO="https://github.com/jakubkrehel/skills.git"
JAKUB_COMMIT="267330e1adfc66a718fb65fa6918c1f06d0a689e"
SHADCN_REPO="https://github.com/shadcn-ui/ui.git"
SHADCN_COMMIT="295a1f114a138f23b5dfee0e0c6812394dfeb90c"
MATT_ONLY=false
UI_ONLY=false
DRY_RUN=false

for option in "$@"; do
  case "$option" in
    --matt-only) MATT_ONLY=true ;;
    --ui-only) UI_ONLY=true ;;
    --dry-run) DRY_RUN=true ;;
    --help)
      printf 'Usage: %s [--matt-only | --ui-only] [--dry-run]\n' "$0"
      printf '  --matt-only  Update only the pinned Matt Pocock collection.\n'
      printf '  --ui-only    Update only the pinned UI skills and licenses.\n'
      printf '  --dry-run    Show file changes without modifying the repository.\n'
      exit 0
      ;;
    *) printf 'Unknown option: %s\n' "$option" >&2; exit 1 ;;
  esac
done

if "$MATT_ONLY" && "$UI_ONLY"; then
  printf 'Choose either --matt-only or --ui-only, not both.\n' >&2
  exit 1
fi

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

ensure_pinned_checkout() {
  local repo="$1"
  local commit="$2"
  local checkout

  checkout="$(checkout_path "$repo" "$commit")"
  git init --quiet "$checkout" >&2 || return 1
  git -C "$checkout" remote add origin "$repo" || return 1
  git -C "$checkout" fetch --quiet --depth 1 origin "$commit" || return 1
  git -C "$checkout" checkout --quiet --detach FETCH_HEAD || return 1

  if [[ "$(git -C "$checkout" rev-parse HEAD)" != "$commit" ]]; then
    printf 'UI source %s does not match the pinned commit %s.\n' "$repo" "$commit" >&2
    return 1
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

sync_file() {
  local source="$1"
  local destination="$2"

  if "$DRY_RUN"; then
    if ! cmp -s "$source" "$destination"; then
      printf '>f %s\n' "${destination#"$ROOT/"}"
    fi
  else
    mkdir -p "$(dirname "$destination")"
    # Replace the file via rsync's temporary file instead of truncating hardlinks.
    rsync -a "$source" "$destination"
  fi
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

EMIL_SKILLS=(
  emil-design-eng
  animate
  review-animations
  break-ui
  mobile-native
)

JAKUB_SKILLS=(
  better-ui
  better-typography
  better-layout
  better-accessibility
  better-colors
  better-writing
  better-interface
)

sync_ui_collection() {
  local emil jakub shadcn name source destination changes index
  local sources=() destinations=()

  emil="$(ensure_pinned_checkout "$EMIL_REPO" "$EMIL_COMMIT")" || return 1
  jakub="$(ensure_pinned_checkout "$JAKUB_REPO" "$JAKUB_COMMIT")" || return 1
  shadcn="$(ensure_pinned_checkout "$SHADCN_REPO" "$SHADCN_COMMIT")" || return 1

  for name in "${EMIL_SKILLS[@]}"; do
    sources+=("$emil/skills/$name")
    destinations+=("skills/$name")
  done
  for name in "${JAKUB_SKILLS[@]}"; do
    sources+=("$jakub/skills/$name")
    destinations+=("skills/$name")
  done
  sources+=("$shadcn/skills/shadcn")
  destinations+=("skills/shadcn")

  sources+=("$emil/LICENSE" "$jakub/LICENSE" "$shadcn/LICENSE.md")
  destinations+=(
    licenses/emilkowalski-skills-LICENSE
    licenses/jakubkrehel-skills-LICENSE
    licenses/shadcn-ui-LICENSE
  )

  # A symlinked destination or parent could redirect rsync outside this checkout.
  for destination in skills licenses "${destinations[@]}"; do
    if [[ -L "$ROOT/$destination" ]]; then
      printf 'Refusing symlinked UI destination: %s\n' "$destination" >&2
      return 1
    fi
  done

  for destination in skills licenses; do
    if [[ -e "$ROOT/$destination" && ! -d "$ROOT/$destination" ]]; then
      printf 'UI destination parent must be a directory: %s\n' "$destination" >&2
      return 1
    fi
  done

  for index in "${!sources[@]}"; do
    source="${sources[$index]}"
    destination="$ROOT/${destinations[$index]}"
    if [[ "${destinations[$index]}" == skills/* ]]; then
      if [[ ! -f "$source/SKILL.md" ]]; then
        printf 'Missing UI skill source: %s\n' "$source" >&2
        return 1
      fi
      if [[ -e "$destination" && ! -d "$destination" ]]; then
        printf 'UI skill destination must be a directory: %s\n' "$destination" >&2
        return 1
      fi
    else
      if [[ ! -f "$source" ]]; then
        printf 'Missing UI license source: %s\n' "$source" >&2
        return 1
      fi
      if [[ -e "$destination" && ! -f "$destination" ]]; then
        printf 'UI license destination must be a file: %s\n' "$destination" >&2
        return 1
      fi
    fi
  done

  changes="$(git -C "$ROOT" status --porcelain=v1 --untracked-files=all --ignored \
    -- "${destinations[@]}")" || return 1
  if [[ -n "$changes" ]]; then
    printf 'Local changes in UI destinations:\n%s\n' "$changes" >&2
    if ! "$DRY_RUN"; then
      printf 'Preserve and commit these changes before updating. Use --ui-only --dry-run to preview.\n' >&2
      return 1
    fi
  fi

  for index in "${!sources[@]}"; do
    source="${sources[$index]}"
    destination="$ROOT/${destinations[$index]}"
    if [[ -d "$source" ]]; then
      sync_directory "$source" "$destination"
    else
      sync_file "$source" "$destination"
    fi
  done
  if "$DRY_RUN"; then
    printf 'UI collection preview complete: %s skills and 3 licenses; no writes.\n' "$(( ${#sources[@]} - 3 ))"
  else
    printf 'UI collection synchronized: %s skills and 3 licenses.\n' "$(( ${#sources[@]} - 3 ))"
  fi
}

if "$UI_ONLY"; then
  sync_ui_collection
  exit 0
fi

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

sync_ui_collection

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
