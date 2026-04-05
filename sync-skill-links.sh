#!/usr/bin/env bash
# Sync symlinks in .claude/skills/ and .agents/skills/ to match root-level directories.
# Usage: ./sync-skill-links.sh

set -eo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGETS=(".claude/skills" ".agents/skills")

declare -A seen_added seen_removed seen_unchanged

for target in "${TARGETS[@]}"; do
  mkdir -p "$ROOT/$target"

  # Create missing symlinks
  for dir in "$ROOT"/*/; do
    name="$(basename "$dir")"
    [[ "$name" == .* ]] && continue
    link="$ROOT/$target/$name"
    if [[ -L "$link" ]]; then
      seen_unchanged["$name"]=1
      continue
    fi
    ln -s "../../$name" "$link"
    echo "  + $name"
    seen_added["$name"]=1
  done

  # Remove stale symlinks
  for link in "$ROOT/$target"/*; do
    [[ -L "$link" ]] || continue
    name="$(basename "$link")"
    if [[ ! -d "$ROOT/$name" ]]; then
      rm "$link"
      echo "  - $name"
      seen_removed["$name"]=1
    fi
  done
done

echo ""
echo "Done: ${#seen_added[@]} added, ${#seen_removed[@]} removed, ${#seen_unchanged[@]} unchanged."
