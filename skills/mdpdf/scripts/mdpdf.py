#!/usr/bin/env python3
"""mdpdf: deterministic Markdown/Obsidian to PDF export via Pandoc + Typst."""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    tomllib = None

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_DIR / "assets"
TEMPLATE_DIR = ASSETS_DIR / "templates"
FILTER_DIR = ASSETS_DIR / "filters"
BRAND_DIR = ASSETS_DIR / "brands"
LOCAL_BASE_TYP = TEMPLATE_DIR / "base.typ"
OBSIDIAN_CALLOUTS_FILTER = FILTER_DIR / "obsidian-callouts.lua"
KEEP_HEADING_FILTER = FILTER_DIR / "keep-heading-with-next.lua"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
DEFAULT_CONFIG = {
    "vault_root": "",
    "output_directory": "",
    "template_kind": "internal",
    "brand": "neutral",
    "brand_label": "DOCUMENT",
    "brand_logo": "",
    "title": "",
    "subtitle": "",
    "author": "",
    "date": "",
    "status": "",
    "version": "1",
    "short_title": "",
    "lang": "fr",
    "toc": None,
    "section_breaks": "none",
    "audience": "internal",
    "justify_body": False,
    "render_mermaid": True,
    "reproducible": True,
    "contact": {
        "name": "",
        "role": "",
        "company": "",
        "address": "",
        "phone": "",
        "fax": "",
        "email": "",
        "url": "",
    },
}


def parse_frontmatter(text: str):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].strip()
    rest = text[end + 4:]
    if rest.startswith("\n"):
        rest = rest[1:]
    meta = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if val.startswith("[") and val.endswith("]"):
            val = val[1:-1].strip()
        meta[key] = val
    return meta, rest


def first(*values):
    for v in values:
        if v not in (None, ""):
            return v
    return ""


def typst_str(s: str) -> str:
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def parse_bool(value, default=False) -> bool:
    if value in (None, ""):
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise SystemExit(f"Valeur booléenne invalide: {value}")


def resolve_base_typ() -> Path:
    if LOCAL_BASE_TYP.exists():
        return LOCAL_BASE_TYP
    raise SystemExit(
        "Template Typst introuvable. Le skill mdpdf attend le template embarqué dans:\n"
        f"- {LOCAL_BASE_TYP}"
    )


def resolve_callouts_filter() -> Path:
    if OBSIDIAN_CALLOUTS_FILTER.exists():
        return OBSIDIAN_CALLOUTS_FILTER
    raise SystemExit(
        "Filtre Pandoc introuvable. Le skill mdpdf attend le filtre callouts dans:\n"
        f"- {OBSIDIAN_CALLOUTS_FILTER}"
    )


def resolve_keep_heading_filter() -> Path:
    if KEEP_HEADING_FILTER.exists():
        return KEEP_HEADING_FILTER
    raise SystemExit(
        "Pandoc filter not found. The mdpdf skill expects the heading filter at:\n"
        f"- {KEEP_HEADING_FILTER}"
    )


def resolve_skill_path(value: str) -> Path:
    if value.startswith("skill://"):
        return (SKILL_DIR / value.removeprefix("skill://")).resolve()
    return Path(value).expanduser().resolve()


def find_asset(target: str, source_dir: Path, vault_root: Path | None) -> Path | None:
    target = target.split("#", 1)[0].split("|", 1)[0].strip()
    if not target:
        return None
    candidates = []
    p = Path(target)
    if p.is_absolute():
        candidates.append(p)
    else:
        candidates.append((source_dir / p).resolve())
        if vault_root:
            candidates.append((vault_root / p).resolve())
        if p.suffix == "":
            for ext in IMAGE_EXTS:
                candidates.append((source_dir / (target + ext)).resolve())
                if vault_root:
                    candidates.append((vault_root / (target + ext)).resolve())
    for c in candidates:
        if c.exists() and c.is_file():
            return c
    if not vault_root or not vault_root.exists():
        return None
    name = Path(target).name
    hits = []
    for root, dirs, files in os.walk(vault_root):
        if ".git" in dirs:
            dirs.remove(".git")
        for f in files:
            fp = Path(root) / f
            if f == name or fp.stem == name:
                if fp.suffix.lower() in IMAGE_EXTS:
                    hits.append(fp)
        if len(hits) > 5:
            break
    if len(hits) == 1:
        return hits[0]
    return None


def preprocess_obsidian(md: str, source: Path, vault_root: Path | None) -> str:
    source_dir = source.parent
    missing = []
    md = re.sub(r"<!--\s*pdf:\s*(pagebreak|section-break)\s*-->", "\n\nPDF_PAGEBREAK_TOKEN\n\n", md, flags=re.I)

    def repl_embed(m):
        raw = m.group(1).strip()
        target, _, alt = raw.partition("|")
        asset = find_asset(target, source_dir, vault_root)
        if not asset:
            missing.append(target)
            return m.group(0)
        if asset.suffix.lower() not in IMAGE_EXTS:
            missing.append(target + " (embed non-image non supporté en V1)")
            return m.group(0)
        label = alt or asset.stem
        rel = os.path.relpath(asset, source_dir)
        return f"![{label}]({asset})"

    md = re.sub(r"!\[\[([^\]]+)\]\]", repl_embed, md)

    def repl_markdown_image(m):
        alt = m.group(1)
        url = m.group(2).strip()
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url) or url.startswith("#"):
            return m.group(0)
        asset = find_asset(url, source_dir, vault_root)
        if not asset:
            missing.append(url)
            return m.group(0)
        return f"![{alt}]({asset})"

    md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl_markdown_image, md)

    def repl_wikilink(m):
        raw = m.group(1).strip()
        target, sep, alias = raw.partition("|")
        if alias:
            return alias.strip()
        target = target.split("#", 1)[0].strip()
        return Path(target).stem or target

    md = re.sub(r"(?<!!)\[\[([^\]]+)\]\]", repl_wikilink, md)
    if missing:
        raise SystemExit("Images/embeds introuvables ou non supportés:\n" + "\n".join(f"- {x}" for x in missing))
    return md


def improve_markdown_tables(md: str) -> str:
    """Normalize Markdown table alignment and emphasize total rows before Pandoc."""
    lines = md.splitlines()
    out = []
    i = 0

    def is_table_line(line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2

    def split_row(line: str) -> list[str]:
        stripped = line.strip()
        if stripped.startswith("|"):
            stripped = stripped[1:]
        if stripped.endswith("|"):
            stripped = stripped[:-1]

        cells = []
        current = []
        escaped = False
        code = False

        for ch in stripped:
            if escaped:
                current.append(ch)
                escaped = False
                continue
            if ch == "\\":
                current.append(ch)
                escaped = True
                continue
            if ch == "`":
                current.append(ch)
                code = not code
                continue
            if ch == "|" and not code:
                cells.append("".join(current).strip())
                current = []
                continue
            current.append(ch)

        cells.append("".join(current).strip())
        return cells

    def make_separator(headers: list[str], rows: list[list[str]]) -> str:
        cols = len(headers)
        markers = []
        for col in range(cols):
            values = [row[col] for row in rows if col < len(row)]
            header = headers[col].lower()
            numeric = sum(1 for value in values if re.search(r"(^|\s)[+−-]?\d[\d\s.,–-]*(k|k€|€|ht|ttc|%)?", value.lower()))
            money = sum(1 for value in values if re.search(r"(€|k€|\\bht\\b|\\bttc\\b)", value.lower()))
            labelish = re.search(r"(sujet|périmètre|perimetre|description|contre-proposition)", header)
            if not labelish and (money >= 2 or numeric >= max(2, len(values) // 2)):
                markers.append("---:")
            else:
                markers.append(":---")
        return "| " + " | ".join(markers) + " |"

    def emphasize_total(row: list[str]) -> list[str]:
        if not row:
            return row
        first = re.sub(r"[*_`]", "", row[0]).strip().lower()
        if not re.match(r"^(total|coût|cout|budget)", first):
            return row
        emphasized = []
        for cell in row:
            stripped = cell.strip()
            if stripped.startswith("**") and stripped.endswith("**"):
                emphasized.append(stripped)
            else:
                emphasized.append(f"**{stripped}**")
        return emphasized

    while i < len(lines):
        if i + 1 < len(lines) and is_table_line(lines[i]) and is_table_line(lines[i + 1]) and re.fullmatch(r"[:|\-\s]+", lines[i + 1].strip()):
            block = [lines[i]]
            i += 2
            while i < len(lines) and is_table_line(lines[i]):
                block.append(lines[i])
                i += 1

            headers = split_row(block[0])
            rows = [split_row(line) for line in block[1:]]
            rows = [emphasize_total(row) for row in rows]

            out.append("| " + " | ".join(headers) + " |")
            out.append(make_separator(headers, rows))
            for row in rows:
                out.append("| " + " | ".join(row) + " |")
            continue

        out.append(lines[i])
        i += 1

    return "\n".join(out) + ("\n" if md.endswith("\n") else "")


def render_mermaid_diagrams(md: str, output_dir: Path) -> str:
    """Render Mermaid fenced code blocks to SVG files and replace them with images."""
    if not re.search(r"(?im)^\s*(`{3,}|~{3,})\s*mermaid\b", md):
        return md
    if not shutil.which("npx"):
        raise SystemExit(
            "Mermaid diagrams detected, but `npx` is unavailable.\n"
            "Install Node.js/npm or run with --no-render-mermaid to keep Mermaid as code blocks."
        )

    diagrams_dir = output_dir / "mermaid"
    diagrams_dir.mkdir(parents=True, exist_ok=True)
    config = diagrams_dir / "mermaid-config.json"
    config.write_text(
        '{\n'
        '  "htmlLabels": false,\n'
        '  "flowchart": { "htmlLabels": false },\n'
        '  "theme": "base",\n'
        '  "themeVariables": {\n'
        '    "fontFamily": "Arial, sans-serif",\n'
        '    "primaryColor": "#EEF2FF",\n'
        '    "primaryBorderColor": "#64748B",\n'
        '    "primaryTextColor": "#111827",\n'
        '    "lineColor": "#475569",\n'
        '    "clusterBkg": "#FFFFDE",\n'
        '    "clusterBorder": "#CBD5E1"\n'
        '  }\n'
        '}\n',
        encoding="utf-8",
    )
    lines = md.splitlines()
    out = []
    i = 0
    diagram_index = 1

    while i < len(lines):
        line = lines[i]
        match = re.match(r"^(`{3,}|~{3,})\s*mermaid\b.*$", line.strip(), flags=re.I)
        if not match:
            out.append(line)
            i += 1
            continue

        fence = match.group(1)
        fence_char = fence[0]
        fence_len = len(fence)
        body_lines = []
        i += 1
        while i < len(lines):
            stripped = lines[i].strip()
            if stripped.startswith(fence_char * fence_len):
                break
            body_lines.append(lines[i])
            i += 1

        if i >= len(lines):
            raise SystemExit("Bloc Mermaid non fermé détecté.")

        source = diagrams_dir / f"mermaid-{diagram_index:02d}.mmd"
        svg = diagrams_dir / f"mermaid-{diagram_index:02d}.svg"
        source.write_text("\n".join(body_lines).strip() + "\n", encoding="utf-8")
        cmd = [
            "npx",
            "--yes",
            "-p",
            "@mermaid-js/mermaid-cli",
            "mmdc",
            "-i",
            str(source),
            "-o",
            str(svg),
            "--configFile",
            str(config),
            "-b",
            "transparent",
        ]
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            sys.stderr.write(proc.stdout)
            sys.stderr.write(proc.stderr)
            raise SystemExit(f"Erreur lors du rendu Mermaid du diagramme {diagram_index}.")

        out.append(f"![Diagramme Mermaid {diagram_index}]({svg})")
        diagram_index += 1
        i += 1

    return "\n".join(out) + ("\n" if md.endswith("\n") else "")


def insert_section_breaks(body_text: str, mode: str) -> str:
    """Insert Typst page breaks before major section headings in Pandoc output."""
    body_text = re.sub(r"PDF(?:\\_|\_)PAGEBREAK(?:\\_|\_)TOKEN", "#pagebreak(weak: true)", body_text)
    if mode == "none":
        return body_text
    if mode not in {"h1", "h2", "h2-major"}:
        raise SystemExit(f"Mode --section-breaks invalide: {mode}")

    heading_re = re.compile(r"^(=+\s+.+)$", re.MULTILINE)
    target_level = 1 if mode == "h1" else 2
    seen_target = 0
    major_h2 = re.compile(
        r"^(stratégie|strategie|message prêt|message pret|conclusion|synthèse finale|synthese finale|recommandation finale|prochaines étapes|prochaines etapes)",
        re.I,
    )

    def repl(m):
        nonlocal seen_target
        line = m.group(1)
        level = len(line) - len(line.lstrip("="))
        if level != target_level:
            return line
        title = line.lstrip("=").strip().lower()
        seen_target += 1
        # Keep the first heading of that level with the opening content. For H2
        # this avoids a lonely document H1 followed by an immediate page break.
        if seen_target == 1:
            return line
        if mode == "h2-major" and not major_h2.search(title):
            return line
        return "#pagebreak(weak: true)\n\n" + line

    return heading_re.sub(repl, body_text)


def split_typst_blocks(body_text: str) -> list[str]:
    blocks = []
    current = []
    blank_count = 0
    fence_open = False
    bracket_depth = 0
    paren_depth = 0

    for line in body_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            fence_open = not fence_open

        if not fence_open:
            bracket_depth += line.count("[") - line.count("]")
            paren_depth += line.count("(") - line.count(")")

        is_boundary = (
            stripped == ""
            and not fence_open
            and bracket_depth <= 0
            and paren_depth <= 0
        )

        if is_boundary:
            blank_count += 1
            if blank_count >= 1 and current:
                blocks.append("\n".join(current).strip("\n"))
                current = []
            continue

        blank_count = 0
        current.append(line)

    if current:
        blocks.append("\n".join(current).strip("\n"))

    return [block for block in blocks if block.strip()]


def is_heading_block(block: str) -> bool:
    first_line = block.lstrip().splitlines()[0] if block.strip() else ""
    return bool(re.match(r"^={1,3}\s+", first_line))


def is_safe_heading_companion(block: str) -> bool:
    stripped = block.lstrip()
    if not stripped:
        return False
    if stripped.startswith("=") or stripped.startswith("#pagebreak"):
        return False
    if stripped.startswith("```") or stripped.startswith("#raw") or stripped.startswith("#block(sticky"):
        return False
    if stripped.startswith("table(") or stripped.startswith("#table(") or stripped.startswith("figure(") or stripped.startswith("#figure("):
        return False
    return True


def keep_headings_with_next(body_text: str) -> str:
    """Wrap headings and their first lightweight companion block after page breaks."""
    blocks = split_typst_blocks(body_text)
    out = []
    i = 0

    while i < len(blocks):
        block = blocks[i]
        if is_heading_block(block) and i + 1 < len(blocks) and is_safe_heading_companion(blocks[i + 1]):
            out.append("#block(sticky: true)[\n" + block + "\n\n" + blocks[i + 1] + "\n]")
            i += 2
            continue
        out.append(block)
        i += 1

    return "\n\n".join(out) + ("\n" if body_text.endswith("\n") else "")


def run_cmd(cmd, cwd: Path):
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(proc.returncode)
    return proc


def tool_cmd(binary: str):
    found = shutil.which(binary)
    if found:
        return [found]
    nix = shutil.which("nix") or "/nix/var/nix/profiles/default/bin/nix"
    if Path(nix).exists():
        return [nix, "shell", f"nixpkgs#{binary}", "-c", binary]
    raise SystemExit(f"Binaire requis introuvable: {binary}. Installe pandoc/typst ou rends nix disponible.")


def deep_merge(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        elif value is not None:
            merged[key] = value
    return merged


def normalize_config(raw: dict) -> dict:
    normalized = {}
    normalized.update({k: v for k, v in raw.items() if k in DEFAULT_CONFIG})
    if "vault" in raw and isinstance(raw["vault"], dict):
        normalized["vault_root"] = raw["vault"].get("root", normalized.get("vault_root", ""))
    if "output" in raw and isinstance(raw["output"], dict):
        normalized["output_directory"] = raw["output"].get("directory", normalized.get("output_directory", ""))
    if "document" in raw and isinstance(raw["document"], dict):
        document = raw["document"]
        aliases = {
            "template": "template_kind",
            "language": "lang",
            "section_breaks": "section_breaks",
            "render_mermaid": "render_mermaid",
        }
        for key, value in document.items():
            normalized[aliases.get(key, key)] = value
    if "contact" in raw and isinstance(raw["contact"], dict):
        normalized["contact"] = raw["contact"]
    if "brands" in raw and isinstance(raw["brands"], dict):
        normalized["brands"] = raw["brands"]
    if "profiles" in raw and isinstance(raw["profiles"], dict):
        normalized["profiles"] = raw["profiles"]
    return normalized


def load_config_file(path: Path | None) -> tuple[dict, Path | None]:
    if path is None:
        return {}, None
    if tomllib is None:
        raise SystemExit("Python 3.11+ is required to read TOML config files.")
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    return normalize_config(raw), path.parent


def find_config(start: Path | None, explicit: Path | None) -> Path | None:
    if explicit:
        path = explicit.expanduser().resolve()
        if not path.exists():
            raise SystemExit(f"Config file not found: {path}")
        return path
    if start:
        for directory in [start, *start.parents]:
            candidate = directory / ".mdpdf.toml"
            if candidate.exists():
                return candidate
    user_config = Path(os.environ.get("MDPDF_CONFIG", "")).expanduser()
    if str(user_config) not in {"", "."} and user_config.exists():
        return user_config.resolve()
    xdg_config = Path.home() / ".config" / "mdpdf" / "config.toml"
    if xdg_config.exists():
        return xdg_config
    return None


def env_config() -> dict:
    config = {}
    env_aliases = {
        "MDPDF_VAULT_ROOT": "vault_root",
        "OBSIDIAN_VAULT_PATH": "vault_root",
        "MDPDF_OUTPUT_DIR": "output_directory",
        "MDPDF_PROFILE": "profile",
    }
    for env_name, key in env_aliases.items():
        value = os.environ.get(env_name)
        if value and key not in config:
            config[key] = value
    return config


def frontmatter_config(meta: dict) -> dict:
    config = {}
    direct = {
        "title": "title",
        "subtitle": "subtitle",
        "author": "author",
        "date": "date",
        "status": "status",
        "confidentiality": "status",
        "version": "version",
        "pdf_version": "version",
        "short_title": "short_title",
        "pdf_template": "template_kind",
        "pdf_section_breaks": "section_breaks",
        "pdf_brand": "brand",
        "pdf_audience": "audience",
        "lang": "lang",
    }
    for source_key, target_key in direct.items():
        if meta.get(source_key) not in (None, ""):
            config[target_key] = meta[source_key]
    if meta.get("pdf_justify_body") not in (None, ""):
        config["justify_body"] = parse_bool(meta["pdf_justify_body"], False)
    if meta.get("toc") not in (None, ""):
        config["toc"] = parse_bool(meta["toc"], False)
    return config


def cli_config(args) -> dict:
    config = {}
    for key in ["template_kind", "brand", "brand_label", "title", "subtitle", "author", "date", "status", "version", "short_title", "lang", "section_breaks", "audience"]:
        value = getattr(args, key, None)
        if value not in (None, ""):
            config[key] = value
    if getattr(args, "toc", False):
        config["toc"] = True
    if getattr(args, "no_toc", False):
        config["toc"] = False
    if getattr(args, "justify_body", False):
        config["justify_body"] = True
    if getattr(args, "no_justify_body", False):
        config["justify_body"] = False
    if getattr(args, "no_render_mermaid", False):
        config["render_mermaid"] = False
    if getattr(args, "reproducible", False):
        config["reproducible"] = True
    if getattr(args, "no_reproducible", False):
        config["reproducible"] = False
    return config


def apply_profile(config: dict, profile: str | None) -> dict:
    if not profile:
        return config
    profiles = config.get("profiles", {})
    if profile not in profiles:
        raise SystemExit(f"Profile '{profile}' not found in config.")
    profile_config = normalize_config(profiles[profile])
    return deep_merge(config, profile_config)


def apply_brand(config: dict, config_dir: Path | None) -> dict:
    brand = str(config.get("brand") or "neutral")
    brands = config.get("brands", {})
    if brand in brands:
        brand_config = brands[brand]
        if brand_config.get("label") and config.get("brand_label") in ("", DEFAULT_CONFIG["brand_label"]):
            config["brand_label"] = brand_config["label"]
        if brand_config.get("logo") and not config.get("brand_logo"):
            config["brand_logo"] = resolve_config_path(brand_config["logo"], config_dir)
    return config


def resolve_config_path(value: str, config_dir: Path | None) -> str:
    expanded = os.path.expandvars(os.path.expanduser(str(value)))
    if expanded.startswith("skill://"):
        return str(resolve_skill_path(expanded))
    path = Path(expanded)
    if path.is_absolute():
        return str(path)
    if config_dir:
        return str((config_dir / path).resolve())
    return str(path.resolve())


def format_path_template(value: str, source: Path | None, config: dict) -> Path:
    today = dt.date.today()
    vault = str(config.get("vault_root") or "")
    if "{vault}" in value and not vault:
        raise SystemExit("output_directory uses {vault}, but no vault_root is configured.")
    source_stem = source.stem if source else "document"
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", source_stem).strip("-").lower() or "document"
    formatted = value.format(
        vault=vault,
        source_dir=str(source.parent) if source else str(Path.cwd()),
        source_stem=source_stem,
        slug=slug,
        year_month=today.strftime("%Y-%m"),
        date=today.isoformat(),
    )
    return Path(os.path.expandvars(os.path.expanduser(formatted)))


def resolve_settings(args, source: Path | None, meta: dict | None = None) -> tuple[dict, Path | None]:
    config_path = find_config(source.parent if source else None, getattr(args, "config", None))
    file_config, config_dir = load_config_file(config_path)
    profile = getattr(args, "profile", None) or os.environ.get("MDPDF_PROFILE") or file_config.get("profile")
    config = copy.deepcopy(DEFAULT_CONFIG)
    config = deep_merge(config, env_config())
    config = deep_merge(config, file_config)
    config = apply_profile(config, profile)
    if meta:
        config = deep_merge(config, frontmatter_config(meta))
    config = deep_merge(config, cli_config(args))
    config = apply_brand(config, config_dir)
    if not config.get("title") and source:
        config["title"] = source.stem
    if not config.get("short_title"):
        config["short_title"] = config.get("title", "")
    if not config.get("status"):
        config["status"] = "Confidentiel - version de travail" if config.get("audience") == "external" else "Interne"
    if config.get("toc") is None:
        config["toc"] = config.get("template_kind") == "pro"
    if config.get("vault_root"):
        config["vault_root"] = str(Path(os.path.expandvars(os.path.expanduser(config["vault_root"]))).resolve())
    config["_profile"] = profile or ""
    config["_config_path"] = str(config_path or "")
    return config, config_dir


def resolve_output_path(args, source: Path, config: dict) -> Path:
    if getattr(args, "output", None):
        return args.output.expanduser().resolve()
    if config.get("output_directory"):
        directory = format_path_template(config["output_directory"], source, config)
        if not directory.is_absolute():
            directory = (source.parent / directory).resolve()
        slug = re.sub(r"[^A-Za-z0-9._-]+", "-", source.stem).strip("-").lower() or "document"
        return directory / f"{slug}.pdf"
    return source.with_suffix(".pdf").resolve()


def public_config(config: dict) -> dict:
    return {k: v for k, v in config.items() if not k.startswith("_") and k not in {"profiles", "brands"}}


def check_binary(binary: str, required: bool = True) -> tuple[bool, str]:
    found = shutil.which(binary)
    if found:
        return True, found
    nix = shutil.which("nix") or "/nix/var/nix/profiles/default/bin/nix"
    if Path(nix).exists():
        return True, f"available through nix shell nixpkgs#{binary}"
    return (not required), "missing"


def run_doctor(args) -> int:
    config, _ = resolve_settings(args, None)
    if getattr(args, "print_config", False):
        print(json.dumps(public_config(config), indent=2, ensure_ascii=False, sort_keys=True))
    checks = [
        ("pandoc", *check_binary("pandoc", required=True)),
        ("typst", *check_binary("typst", required=True)),
        ("npx", *check_binary("npx", required=False)),
        ("template", LOCAL_BASE_TYP.exists(), str(LOCAL_BASE_TYP)),
        ("callouts_filter", OBSIDIAN_CALLOUTS_FILTER.exists(), str(OBSIDIAN_CALLOUTS_FILTER)),
        ("keep_heading_filter", KEEP_HEADING_FILTER.exists(), str(KEEP_HEADING_FILTER)),
    ]
    logo = config.get("brand_logo")
    if logo:
        checks.append(("brand_logo", Path(logo).exists(), logo))
    vault = config.get("vault_root")
    if vault:
        checks.append(("vault_root", Path(vault).exists(), vault))
    ok = True
    for name, passed, detail in checks:
        status = "OK" if passed else "MISSING"
        print(f"{status:8} {name}: {detail}")
        if not passed and name != "npx":
            ok = False
    if not shutil.which("npx") and config.get("render_mermaid"):
        print("WARN     npx: Mermaid rendering will fail; use --no-render-mermaid or install Node.js/npm.")
    return 0 if ok else 1


def run_export(args) -> int:
    source = args.input.expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"Input file not found: {source}")
    base_typ = resolve_base_typ()
    callouts_filter = resolve_callouts_filter()
    keep_heading_filter = resolve_keep_heading_filter()

    text = source.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    config, _ = resolve_settings(args, source, meta)
    output = resolve_output_path(args, source, config)
    if args.print_config:
        printable = public_config(config)
        printable["output"] = str(output)
        print(json.dumps(printable, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    vault_root = Path(config["vault_root"]) if config.get("vault_root") else None
    body = preprocess_obsidian(body, source, vault_root)
    body = improve_markdown_tables(body)
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="mdpdf-") as td:
        tmp = Path(td)
        if config.get("render_mermaid"):
            body = render_mermaid_diagrams(body, tmp)
        (tmp / "source.md").write_text(body, encoding="utf-8")
        shutil.copy2(base_typ, tmp / "base.typ")
        logo_path = ""
        if config.get("brand_logo"):
            logo_src = Path(config["brand_logo"])
            if not logo_src.exists():
                raise SystemExit(f"Brand logo not found: {logo_src}")
            logo_dir = tmp / "assets"
            logo_dir.mkdir(exist_ok=True)
            logo_dest = logo_dir / logo_src.name
            shutil.copy2(logo_src, logo_dest)
            logo_path = f"assets/{logo_dest.name}"
        body_typ = tmp / "body.typ"
        pandoc = tool_cmd("pandoc")
        typst = tool_cmd("typst")
        pandoc_cmd = pandoc + [
            str(tmp / "source.md"),
            "-f", "markdown+pipe_tables+footnotes+task_lists",
            "-t", "typst",
            "--wrap=none",
            "-M", f"brand={config['brand']}",
        ]
        pandoc_cmd += ["--lua-filter", str(callouts_filter)]
        pandoc_cmd += ["--lua-filter", str(keep_heading_filter)]
        pandoc_cmd += ["-o", str(body_typ)]
        run_cmd(pandoc_cmd, cwd=source.parent)

        assets_dir = tmp / "assets"
        body_text = body_typ.read_text(encoding="utf-8")
        body_text = insert_section_breaks(body_text, config["section_breaks"])
        copied = {}

        def repl_typst_image(m):
            raw_path = m.group(1)
            p = Path(raw_path)
            if not p.is_absolute() or not p.exists():
                return m.group(0)
            if p not in copied:
                assets_dir.mkdir(exist_ok=True)
                safe = re.sub(r"[^A-Za-z0-9._-]+", "-", p.name)
                dest = assets_dir / safe
                n = 1
                while dest.exists() and dest.read_bytes() != p.read_bytes():
                    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", p.stem)
                    dest = assets_dir / f"{stem}-{n}{p.suffix}"
                    n += 1
                shutil.copy2(p, dest)
                copied[p] = f"assets/{dest.name}"
            return f'image("{copied[p]}")'

        body_text = re.sub(r'image\("([^"]+)"\)', repl_typst_image, body_text)
        body_typ.write_text('#import "base.typ": callout, scope_box\n\n' + body_text, encoding="utf-8")
        contact = config.get("contact", {})
        exported_at = "" if config.get("reproducible") else dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
        full = tmp / "document.typ"
        full.write_text(
            '#import "base.typ": mdpdf_document, callout, scope_box\n'
            '#show: body => mdpdf_document(body, '
            f'title: {typst_str(config["title"])}, subtitle: {typst_str(config["subtitle"])}, author: {typst_str(config["author"])}, date: {typst_str(config["date"])}, '
            f'status: {typst_str(config["status"])}, version: {typst_str(config["version"])}, exported_at: {typst_str(exported_at)}, short_title: {typst_str(config["short_title"])}, '
            f'template_kind: {typst_str(config["template_kind"])}, brand: {typst_str(config["brand"])}, brand_label: {typst_str(config["brand_label"])}, lang: {typst_str(config["lang"])}, toc: {str(bool(config["toc"])).lower()}, '
            f'justify_body: {str(bool(config["justify_body"])).lower()}, audience: {typst_str(config["audience"])}, logo_path: {typst_str(logo_path)}, '
            f'contact_name: {typst_str(contact.get("name", ""))}, contact_role: {typst_str(contact.get("role", ""))}, '
            f'contact_company: {typst_str(contact.get("company", ""))}, contact_address: {typst_str(contact.get("address", ""))}, '
            f'contact_phone: {typst_str(contact.get("phone", ""))}, contact_fax: {typst_str(contact.get("fax", ""))}, '
            f'contact_email: {typst_str(contact.get("email", ""))}, contact_url: {typst_str(contact.get("url", ""))})\n\n'
            '#include "body.typ"\n',
            encoding="utf-8",
        )
        typst_compile = typst + ["compile"]
        if config.get("reproducible") and config.get("audience") != "external":
            typst_compile += ["--creation-timestamp", "0"]
        typst_compile += [str(full), str(output)]
        run_cmd(typst_compile, cwd=source.parent)
    print(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export Markdown/Obsidian files to PDF through Pandoc + Typst.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_flags(p):
        p.add_argument("--config", type=Path, help="TOML config file. Defaults to nearest .mdpdf.toml, MDPDF_CONFIG, or ~/.config/mdpdf/config.toml.")
        p.add_argument("--profile", help="Named profile from the config file.")
        p.add_argument("--brand")
        p.add_argument("--brand-label")
        p.add_argument("--template", choices=["internal", "pro"], dest="template_kind")
        p.add_argument("--title")
        p.add_argument("--subtitle")
        p.add_argument("--author")
        p.add_argument("--date")
        p.add_argument("--status")
        p.add_argument("--version")
        p.add_argument("--short-title")
        p.add_argument("--lang", choices=["fr", "en"])
        p.add_argument("--section-breaks", choices=["none", "h1", "h2", "h2-major"])
        p.add_argument("--audience", choices=["internal", "external"])
        reproducible = p.add_mutually_exclusive_group()
        reproducible.add_argument("--reproducible", action="store_true")
        reproducible.add_argument("--no-reproducible", action="store_true", help="Include current export timestamps and normal PDF creation timestamps.")
        p.add_argument("--no-render-mermaid", action="store_true")
        p.add_argument("--print-config", action="store_true")
        toc = p.add_mutually_exclusive_group()
        toc.add_argument("--toc", action="store_true")
        toc.add_argument("--no-toc", action="store_true")
        justify = p.add_mutually_exclusive_group()
        justify.add_argument("--justify-body", action="store_true")
        justify.add_argument("--no-justify-body", action="store_true")

    export_parser = subparsers.add_parser("export", help="Export one Markdown file to PDF.")
    export_parser.add_argument("input", type=Path)
    export_parser.add_argument("--output", type=Path)
    add_common_flags(export_parser)

    doctor_parser = subparsers.add_parser("doctor", help="Check runtime dependencies and configured assets.")
    add_common_flags(doctor_parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in {"export", "doctor", "-h", "--help"}:
        argv.insert(0, "export")
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "doctor":
        return run_doctor(args)
    if args.command == "export":
        return run_export(args)
    parser.error(f"Unknown command: {args.command}")

if __name__ == "__main__":
    raise SystemExit(main())
