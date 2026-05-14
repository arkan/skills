#!/usr/bin/env python3
"""
GitHub Stars Import — mechanical pipeline.

Fetches starred repos via gh CLI, generates Obsidian notes with
frontmatter/Resume/Voir aussi/footer. Outputs a manifest of READMEs
needing LLM summarization.

Usage:
    python3 gh_stars.py                    # last 30 stars
    python3 gh_stars.py --all              # full sync
    python3 gh_stars.py --count 50         # last 50 stars
    python3 gh_stars.py --fix-dates        # fix repo_updated on all existing files
    python3 gh_stars.py --strip-sections   # remove Details/Topics from all files
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

VAULT_ROOT = Path(__file__).resolve().parents[3]  # up from .claude/skills/github-import/
STARS_DIR = VAULT_ROOT / "Resources" / "GitHub-Stars"
BASE_FILE = STARS_DIR / "GitHub-Stars.base"
MANIFEST_FILE = Path("/tmp/gh_stars_manifest.json")
TODAY = date.today().isoformat()
MAX_WORKERS = 10  # parallel gh api calls

# Tag mapping rules
LANGUAGE_TAG_MAP = {
    "go": "go", "python": "python", "typescript": "typescript",
    "javascript": "javascript", "rust": "rust", "java": "java",
    "ruby": "ruby", "c": "c", "c++": "cpp", "c#": "csharp",
    "php": "php", "swift": "swift", "kotlin": "kotlin",
    "elixir": "elixir", "haskell": "haskell", "lua": "lua",
    "shell": "shell", "dart": "dart", "zig": "zig", "nim": "nim",
    "scala": "scala", "r": "r", "perl": "perl", "clojure": "clojure",
    "erlang": "erlang", "ocaml": "ocaml",
}

TOPIC_TAG_MAP = {
    "cli": "cli", "command-line": "cli",
    "machine-learning": "ai", "deep-learning": "ai", "llm": "ai", "ai": "ai",
    "devops": "devops", "ci-cd": "devops", "infrastructure": "devops",
    "kubernetes": "devops", "docker": "devops", "containers": "devops",
    "security": "security", "cryptography": "security",
    "database": "database", "sql": "database", "postgresql": "database",
    "frontend": "frontend", "react": "frontend", "vue": "frontend", "svelte": "frontend",
    "backend": "backend", "api": "backend", "rest": "backend", "grpc": "backend",
    "open-source": "open-source",
    "startup": "startup", "saas": "startup",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def gh_api(endpoint: str, extra_args: list[str] | None = None) -> str | None:
    """Call gh api and return stdout, or None on failure."""
    cmd = ["gh", "api", endpoint]
    if extra_args:
        cmd.extend(extra_args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return r.stdout
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def iso_to_date(iso: str | None) -> str:
    """Extract YYYY-MM-DD from ISO timestamp."""
    if not iso:
        return ""
    return iso[:10]


def generate_tags(language: str | None, topics: list[str]) -> list[str]:
    """Generate vault tags from language + topics. No github-star (redundant with type field)."""
    tags: set[str] = set()
    if language:
        lang_lower = language.lower()
        if lang_lower in LANGUAGE_TAG_MAP:
            tags.add(LANGUAGE_TAG_MAP[lang_lower])
        elif re.match(r"^[a-z]+$", lang_lower):
            tags.add(lang_lower)
    for topic in topics:
        t = topic.lower()
        if t in TOPIC_TAG_MAP:
            tags.add(TOPIC_TAG_MAP[t])
        elif re.match(r"^[a-z][a-z0-9-]*$", t) and len(t) <= 30:
            tags.add(t)
    return sorted(tags)[:8]


def yaml_list(items: list[str], quote: bool = False) -> str:
    """Format a list for YAML frontmatter inline."""
    if not items:
        return "[]"
    if quote:
        return "[" + ", ".join(f'"{i}"' for i in items) + "]"
    return "[" + ", ".join(items) + "]"


def escape_yaml_string(s: str) -> str:
    """Escape a string for YAML double-quoted value."""
    if not s:
        return ""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def fetch_last_commit_date(owner: str, repo: str) -> str | None:
    """Fetch last commit date on default branch."""
    raw = gh_api(f"/repos/{owner}/{repo}/commits?per_page=1",
                 ["--jq", ".[0].commit.committer.date"])
    if raw and raw.strip():
        return iso_to_date(raw.strip())
    return None


def fetch_readme(owner: str, repo: str) -> str | None:
    """Fetch and decode README content (truncated to 5000 chars)."""
    raw = gh_api(f"/repos/{owner}/{repo}/readme", ["--jq", ".content"])
    if not raw or not raw.strip():
        return None
    try:
        decoded = base64.b64decode(raw.strip()).decode("utf-8", errors="replace")
        return decoded[:5000]
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Fetch stars
# ---------------------------------------------------------------------------

def fetch_stars(mode: str, count: int = 30) -> list[dict]:
    """Fetch starred repos via gh CLI."""
    print(f"Fetching stars (mode={mode}, count={count})...")

    if mode == "all":
        # Paginate — can't combine --slurp with --jq in newer gh versions
        raw = subprocess.run(
            ["gh", "api", "/user/starred?per_page=100&sort=created&direction=desc",
             "-H", "Accept: application/vnd.github.star+json", "--paginate"],
            capture_output=True, text=True, timeout=300
        )
        if raw.returncode != 0:
            print(f"ERROR: gh api failed: {raw.stderr}", file=sys.stderr)
            sys.exit(1)
        # Paginated output is multiple JSON arrays concatenated
        text = raw.stdout.strip()
        # Parse concatenated JSON arrays
        stars = []
        for chunk in re.split(r"\]\s*\[", text):
            chunk = chunk.strip()
            if not chunk.startswith("["):
                chunk = "[" + chunk
            if not chunk.endswith("]"):
                chunk = chunk + "]"
            stars.extend(json.loads(chunk))
    else:
        per_page = min(count, 100)
        raw = gh_api(
            f"/user/starred?per_page={per_page}&sort=created&direction=desc",
            ["-H", "Accept: application/vnd.github.star+json"]
        )
        if not raw:
            print("ERROR: gh api failed", file=sys.stderr)
            sys.exit(1)
        stars = json.loads(raw)

    print(f"  Fetched {len(stars)} stars.")
    return stars


# ---------------------------------------------------------------------------
# Fetch lists index
# ---------------------------------------------------------------------------

def fetch_lists_index() -> dict[str, list[str]]:
    """Fetch GitHub Lists and build repo → list names reverse index."""
    print("Fetching GitHub Lists index...")
    query = '{ viewer { lists(first: 30) { nodes { name items(first: 100) { nodes { ... on Repository { nameWithOwner } } pageInfo { hasNextPage endCursor } } } } } }'
    raw = gh_api("graphql", ["-f", f"query={query}"])
    if not raw:
        print("  Warning: could not fetch lists, continuing without.")
        return {}

    data = json.loads(raw)
    index: dict[str, list[str]] = {}
    for lst in data["data"]["viewer"]["lists"]["nodes"]:
        name = lst["name"]
        for item in lst["items"]["nodes"]:
            repo = item.get("nameWithOwner", "")
            if repo:
                index.setdefault(repo, []).append(name)
    print(f"  Built index: {len(index)} repos across lists.")
    return index


# ---------------------------------------------------------------------------
# Classify new vs existing
# ---------------------------------------------------------------------------

def classify_stars(stars: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split stars into new and existing based on files in STARS_DIR."""
    # Build set of existing repo_fullnames from frontmatter
    existing_fullnames: set[str] = set()
    for f in STARS_DIR.glob("*.md"):
        with open(f, "r", encoding="utf-8") as fh:
            in_frontmatter = False
            for line in fh:
                stripped = line.strip()
                if stripped == "---":
                    if not in_frontmatter:
                        in_frontmatter = True
                        continue
                    else:
                        break  # end of frontmatter
                if in_frontmatter and stripped.startswith("repo_fullname:"):
                    match = re.search(r'"([^"]+)"', stripped)
                    if match:
                        existing_fullnames.add(match.group(1))
                    break

    new_stars = []
    existing_stars = []
    for star in stars:
        fn = star.get("repo", {}).get("full_name", "")
        if fn in existing_fullnames:
            existing_stars.append(star)
        else:
            new_stars.append(star)

    return new_stars, existing_stars


# ---------------------------------------------------------------------------
# Generate note content
# ---------------------------------------------------------------------------

def build_note(repo: dict, starred_at: str, lists_index: dict[str, list[str]],
               readme: str | None, last_commit_date: str | None) -> str:
    """Build the full .md note content (Resume is a placeholder if no readme)."""
    fn = repo["full_name"]
    owner = repo["owner"]["login"]
    name = repo["name"]
    desc = repo.get("description") or ""
    language = repo.get("language") or "Non spécifié"
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    license_id = (repo.get("license") or {}).get("spdx_id") or "Non spécifiée"
    if license_id == "NOASSERTION":
        license_id = "Non spécifiée"
    topics = repo.get("topics") or []
    html_url = repo.get("html_url", f"https://github.com/{fn}")
    homepage = repo.get("homepage") or ""
    created_at = iso_to_date(repo.get("created_at"))
    pushed_at = iso_to_date(repo.get("pushed_at"))
    open_issues = repo.get("open_issues_count", 0)

    repo_updated = last_commit_date or pushed_at
    tags = generate_tags(repo.get("language"), topics)
    lists = lists_index.get(fn, [])

    # Frontmatter
    lines = ["---"]
    lines.append('type: github-star')
    lines.append(f'repo_fullname: "{escape_yaml_string(fn)}"')
    lines.append(f'repo_name: "{escape_yaml_string(name)}"')
    lines.append(f'owner: "{escape_yaml_string(owner)}"')
    lines.append(f'description: "{escape_yaml_string(desc)}"')
    lines.append(f'language: "{escape_yaml_string(language)}"')
    lines.append(f'stars: {stars}')
    lines.append(f'forks: {forks}')
    lines.append(f'license: "{escape_yaml_string(license_id)}"')
    lines.append(f'topics: {yaml_list(topics)}')
    lines.append(f'tags: {yaml_list(tags)}')
    lines.append(f'lists: {yaml_list(lists, quote=True)}')
    if homepage:
        lines.append(f'homepage: "{escape_yaml_string(homepage)}"')
    lines.append(f'source: "{html_url}"')
    lines.append(f'starred_at: {iso_to_date(starred_at)}')
    lines.append(f'repo_created: {created_at}')
    lines.append(f'repo_updated: {repo_updated}')
    lines.append(f'status: draft')
    lines.append(f'created: {TODAY}')
    lines.append(f'updated_at: {TODAY}')
    lines.append("---")
    lines.append("")

    # Resume
    lines.append("## Resume")
    lines.append("")
    lines.append("{{RESUME_PLACEHOLDER}}")
    lines.append("")

    # Voir aussi (placeholder)
    lines.append("## Voir aussi")
    lines.append("")
    lines.append("")

    # Footer
    tag_links = " | ".join(f"[[{t}]]" for t in tags)
    footer = f"↑ [[GitHub-Stars]] | {tag_links}" if tag_links else "↑ [[GitHub-Stars]]"
    lines.append("---")
    lines.append(footer)
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Process new stars
# ---------------------------------------------------------------------------

def process_new_star(star: dict, lists_index: dict[str, list[str]]) -> dict:
    """Process a single new star: fetch commit date, readme, build note."""
    repo = star["repo"]
    fn = repo["full_name"]
    owner = repo["owner"]["login"]
    name = repo["name"]
    starred_at = star["starred_at"]

    # Fetch last commit date
    last_commit_date = fetch_last_commit_date(owner, name)

    # Fetch README
    readme = fetch_readme(owner, name)

    # Build note
    content = build_note(repo, starred_at, lists_index, readme, last_commit_date)

    # Write file
    filename = f"{owner}-{name}.md"
    filepath = STARS_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "file": filename,
        "full_name": fn,
        "description": repo.get("description") or "",
        "language": repo.get("language") or "",
        "readme": readme,
        "has_readme": readme is not None,
    }


def process_new_stars(new_stars: list[dict], lists_index: dict[str, list[str]]) -> list[dict]:
    """Process all new stars in parallel. Returns manifest entries."""
    # Sort oldest first
    new_stars.sort(key=lambda s: s.get("starred_at", ""))

    total = len(new_stars)
    manifest = []
    done = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_new_star, star, lists_index): star
            for star in new_stars
        }
        for future in as_completed(futures):
            try:
                entry = future.result()
                manifest.append(entry)
            except Exception as e:
                star = futures[future]
                fn = star.get("repo", {}).get("full_name", "???")
                print(f"  ERROR processing {fn}: {e}", file=sys.stderr)
            done += 1
            if done % 50 == 0 or done == total:
                print(f"  Progress: {done}/{total} new stars processed.")

    return manifest


# ---------------------------------------------------------------------------
# Update existing stars
# ---------------------------------------------------------------------------

def update_existing_star(star: dict, lists_index: dict[str, list[str]]) -> str | None:
    """Update an existing note with fresh API data. Returns filename or None."""
    repo = star["repo"]
    fn = repo["full_name"]
    owner = repo["owner"]["login"]
    name = repo["name"]

    filename = f"{owner}-{name}.md"
    filepath = STARS_DIR / filename
    if not filepath.exists():
        return None

    content = filepath.read_text(encoding="utf-8")

    # Fetch last commit date
    last_commit_date = fetch_last_commit_date(owner, name)
    pushed_at = iso_to_date(repo.get("pushed_at"))
    repo_updated = last_commit_date or pushed_at

    # Update frontmatter fields
    def replace_fm(key: str, value: str) -> None:
        nonlocal content
        pattern = re.compile(rf"^{re.escape(key)}:.*$", re.MULTILINE)
        if pattern.search(content):
            content = pattern.sub(f"{key}: {value}", content)

    replace_fm("stars", str(repo.get("stargazers_count", 0)))
    replace_fm("forks", str(repo.get("forks_count", 0)))
    license_id = (repo.get("license") or {}).get("spdx_id") or "Non spécifiée"
    if license_id == "NOASSERTION":
        license_id = "Non spécifiée"
    replace_fm("license", f'"{escape_yaml_string(license_id)}"')
    replace_fm("description", f'"{escape_yaml_string(repo.get("description") or "")}"')
    replace_fm("topics", yaml_list(repo.get("topics") or []))
    replace_fm("lists", yaml_list(lists_index.get(fn, []), quote=True))
    replace_fm("repo_updated", repo_updated)
    replace_fm("updated_at", TODAY)

    # Re-derive tags (preserve user-added ones)
    new_tags = set(generate_tags(repo.get("language"), repo.get("topics") or []))
    # Extract current tags from frontmatter
    tag_match = re.search(r"^tags:\s*\[([^\]]*)\]", content, re.MULTILINE)
    if tag_match:
        current_tags = {t.strip().strip('"').strip("'") for t in tag_match.group(1).split(",") if t.strip()}
        # Find user-added tags (in current but not derivable from any mapping)
        all_derivable = set(LANGUAGE_TAG_MAP.values()) | set(TOPIC_TAG_MAP.values()) | {"github-star"}
        all_single_topics = {t.lower() for t in (repo.get("topics") or [])}
        all_derivable |= all_single_topics
        if repo.get("language"):
            all_derivable.add(repo["language"].lower())
        user_tags = current_tags - all_derivable
        final_tags = sorted((new_tags | user_tags) - {"github-star"})[:8]
        replace_fm("tags", yaml_list(final_tags))

    filepath.write_text(content, encoding="utf-8")
    return filename


def update_existing_stars(existing_stars: list[dict], lists_index: dict[str, list[str]]) -> list[str]:
    """Update all existing stars in parallel. Returns list of updated filenames."""
    total = len(existing_stars)
    updated = []
    done = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(update_existing_star, star, lists_index): star
            for star in existing_stars
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    updated.append(result)
            except Exception as e:
                star = futures[future]
                fn = star.get("repo", {}).get("full_name", "???")
                print(f"  ERROR updating {fn}: {e}", file=sys.stderr)
            done += 1
            if done % 20 == 0 or done == total:
                print(f"  Progress: {done}/{total} existing stars updated.")

    return updated


# ---------------------------------------------------------------------------
# Fix dates only (--fix-dates mode)
# ---------------------------------------------------------------------------

def fix_dates():
    """Fix repo_updated on all existing files by fetching actual last commit dates."""
    files = list(STARS_DIR.glob("*.md"))
    total = len(files)
    print(f"Fixing repo_updated on {total} files...")

    def fix_one(filepath: Path) -> tuple[str, bool]:
        content = filepath.read_text(encoding="utf-8")
        # Extract owner/repo from frontmatter
        match = re.search(r'^repo_fullname:\s*"([^"]+)"', content, re.MULTILINE)
        if not match:
            return filepath.name, False
        fn = match.group(1)
        owner, repo = fn.split("/", 1)
        new_date = fetch_last_commit_date(owner, repo)
        if not new_date:
            return filepath.name, False

        # Check current value
        date_match = re.search(r"^repo_updated:\s*(\S+)", content, re.MULTILINE)
        if date_match and date_match.group(1) == new_date:
            return filepath.name, False  # already correct

        # Update frontmatter
        content = re.sub(
            r"^repo_updated:.*$", f"repo_updated: {new_date}",
            content, flags=re.MULTILINE
        )
        filepath.write_text(content, encoding="utf-8")
        return filepath.name, True

    fixed = 0
    done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fix_one, f): f for f in files}
        for future in as_completed(futures):
            name, changed = future.result()
            if changed:
                fixed += 1
            done += 1
            if done % 100 == 0 or done == total:
                print(f"  Progress: {done}/{total} checked, {fixed} fixed.")

    print(f"Done. Fixed {fixed}/{total} files.")


# ---------------------------------------------------------------------------
# Strip Details/Topics sections (--strip-sections mode)
# ---------------------------------------------------------------------------

def strip_sections():
    """Remove ## Details and ## Topics sections from all existing files."""
    files = list(STARS_DIR.glob("*.md"))
    total = len(files)
    print(f"Stripping Details/Topics sections from {total} files...")

    stripped = 0
    for i, filepath in enumerate(files, 1):
        content = filepath.read_text(encoding="utf-8")
        original = content

        # Remove ## Details section (heading + blank line + bullet lines + trailing blank line)
        content = re.sub(
            r"## Details\n\n(?:- \*\*[^\n]*\n)+\n",
            "",
            content
        )

        # Remove ## Topics section (heading + blank line + content line + trailing blank line)
        content = re.sub(
            r"## Topics\n\n[^\n#]+\n\n",
            "",
            content
        )

        if content != original:
            filepath.write_text(content, encoding="utf-8")
            stripped += 1

        if i % 200 == 0 or i == total:
            print(f"  Progress: {i}/{total} checked, {stripped} stripped.")

    print(f"Done. Stripped sections from {stripped}/{total} files.")


# ---------------------------------------------------------------------------
# Create .base file
# ---------------------------------------------------------------------------

def ensure_base_file():
    """Create the .base file if it doesn't exist."""
    if BASE_FILE.exists():
        return
    content = """filters:
  and:
    - file.inFolder("Resources/GitHub-Stars")
    - 'type == "github-star"'

formulas:
  days_since_update: '(today() - date(repo_updated)).days'
  popularity: 'if(stars, stars.toString() + " ⭐", "")'

properties:
  repo_fullname:
    displayName: "Repo"
  language:
    displayName: "Langage"
  formula.popularity:
    displayName: "Stars"
  description:
    displayName: "Description"
  starred_at:
    displayName: "Starred"
  formula.days_since_update:
    displayName: "Dernière MAJ (jours)"

views:
  - type: table
    name: "Tous les repos"
    order:
      - file.name
      - language
      - formula.popularity
      - starred_at
      - formula.days_since_update
    groupBy:
      property: language
      direction: ASC

  - type: table
    name: "Recents"
    limit: 30
    order:
      - file.name
      - language
      - formula.popularity
      - description
    filters:
      and: []

  - type: cards
    name: "Galerie"
    order:
      - file.name
      - description
      - language
      - formula.popularity
"""
    BASE_FILE.write_text(content, encoding="utf-8")
    print(f"Created {BASE_FILE}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="GitHub Stars Import")
    parser.add_argument("--all", action="store_true", help="Fetch all stars")
    parser.add_argument("--count", type=int, default=30, help="Number of stars to fetch")
    parser.add_argument("--fix-dates", action="store_true", help="Fix repo_updated on all existing files")
    parser.add_argument("--strip-sections", action="store_true", help="Remove Details/Topics sections from all files")
    args = parser.parse_args()

    # Ensure output directory
    STARS_DIR.mkdir(parents=True, exist_ok=True)

    if args.strip_sections:
        strip_sections()
        return

    if args.fix_dates:
        fix_dates()
        return

    # Step 1 — Fetch stars
    mode = "all" if args.all else "incremental"
    stars = fetch_stars(mode, args.count)
    if not stars:
        print("No stars found.")
        return

    # Step 2 — Classify
    new_stars, existing_stars = classify_stars(stars)
    total = len(stars)
    print(f"\n{len(new_stars)} nouveaux repos, {len(existing_stars)} à mettre à jour sur {total} total.\n")

    if not new_stars and not existing_stars:
        print("Nothing to do.")
        return

    # Step 2b — Fetch lists index
    lists_index = fetch_lists_index()

    # Step 3-4 — Process new stars
    manifest = []
    if new_stars:
        print(f"\nProcessing {len(new_stars)} new stars...")
        manifest = process_new_stars(new_stars, lists_index)
        readmes_found = sum(1 for m in manifest if m["has_readme"])
        print(f"  Done: {len(manifest)} notes created, {readmes_found} READMEs fetched.")

    # Step 4c — Update existing stars
    updated_files = []
    if existing_stars:
        print(f"\nUpdating {len(existing_stars)} existing stars...")
        updated_files = update_existing_stars(existing_stars, lists_index)
        print(f"  Done: {len(updated_files)} notes updated.")

    # Step 5 — Ensure .base file
    ensure_base_file()

    # Write manifest for LLM summarization
    # Only include new stars that have READMEs and need summaries
    summary_manifest = [
        {
            "file": m["file"],
            "full_name": m["full_name"],
            "description": m["description"],
            "language": m["language"],
            "readme": m["readme"],
        }
        for m in manifest if m["has_readme"]
    ]
    MANIFEST_FILE.write_text(json.dumps(summary_manifest, ensure_ascii=False), encoding="utf-8")

    # Step 6 — Report
    print(f"""
========================================
Import GitHub Stars terminé.
- Stars récupérées : {total}
- Nouvelles : {len(new_stars)}
- Mises à jour : {len(existing_stars)}
- READMEs récupérés : {sum(1 for m in manifest if m['has_readme'])}
- Notes créées : {len(manifest)}
- Notes mises à jour : {len(updated_files)}
- Manifest LLM : {MANIFEST_FILE} ({len(summary_manifest)} résumés à générer)
========================================
""")


if __name__ == "__main__":
    main()
