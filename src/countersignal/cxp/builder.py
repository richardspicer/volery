"""Repo builder -- assembles poisoned test repositories.

v0.2: Assembles context files from clean base templates plus modular rules,
replacing the Jinja2 template rendering system. Also generates a prompt
reference companion file.

Legacy functions (build_repo, build_all, etc.) are preserved for backward
compatibility and will be removed in Brief 4.
"""

from __future__ import annotations

import json
import re
import shlex
from dataclasses import replace
from datetime import UTC, datetime
from importlib.resources import files as resource_files
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.abc import Traversable

import jinja2

from countersignal.cxp.base_loader import insert_rules, load_base, strip_markers
from countersignal.cxp.formats import get_format
from countersignal.cxp.models import BuildResult, PayloadMode, Rule, Technique
from countersignal.cxp.prompt_reference import generate_prompt_reference
from countersignal.cxp.techniques import list_techniques, load_stealth_override

# Pattern to detect any CXP/countersignal reference in output files.
_CXP_REFERENCE = re.compile(r"(?:cxp|countersignal)", re.IGNORECASE)


def _copy_tree(source: Traversable, dest: Path) -> None:
    """Recursively copy a Traversable directory tree to a filesystem path.

    Args:
        source: Source directory (importlib.resources Traversable).
        dest: Destination filesystem path.
    """
    for item in source.iterdir():
        if item.name == "__pycache__" and item.is_dir():
            continue
        if item.is_file():
            target = dest / item.name
            try:
                target.write_text(item.read_text(encoding="utf-8"), encoding="utf-8")
            except UnicodeDecodeError:
                target.write_bytes(item.read_bytes())
        elif item.is_dir():
            subdir = dest / item.name
            subdir.mkdir(parents=True, exist_ok=True)
            _copy_tree(item, subdir)


def build(
    format_id: str,
    rules: list[Rule],
    output_dir: Path,
    repo_name: str,
) -> BuildResult:
    """Assemble a poisoned context file and project skeleton.

    Steps:
    1. Load the base template for the format
    2. Resolve each rule's content for the format's syntax type
    3. Insert rules at section markers
    4. Strip all section markers
    5. Write the assembled context file to the repo directory
    6. Copy the project skeleton
    7. Generate the prompt reference
    8. Write the manifest

    Args:
        format_id: Target format (e.g., "cursorrules", "claude-md").
        rules: Selected rules to insert.
        output_dir: Parent directory for the generated repo.
        repo_name: Directory name for the generated repo.

    Returns:
        BuildResult with paths and metadata.

    Raises:
        ValueError: If format_id is not recognized.
    """
    fmt = get_format(format_id)
    if fmt is None:
        raise ValueError(f"Unknown format: {format_id!r}")

    # 1. Load base template
    base_content = load_base(format_id)

    # 2-3. Insert rules at section markers
    assembled = insert_rules(base_content, rules, fmt.syntax)

    # 4. Strip all section markers
    clean_content = strip_markers(assembled)

    # 5. Create repo dir and write assembled context file
    repo_dir = output_dir / repo_name
    repo_dir.mkdir(parents=True, exist_ok=True)

    context_file = repo_dir / fmt.filename
    context_file.parent.mkdir(parents=True, exist_ok=True)
    context_file.write_text(clean_content, encoding="utf-8")

    # 6. Copy project skeleton
    skeleton = resource_files("countersignal.cxp.techniques") / "skeleton"
    _copy_tree(skeleton, repo_dir)

    # 7. Generate prompt reference
    prompt_ref_content = generate_prompt_reference(rules)
    prompt_ref_path = repo_dir / "prompt-reference.md"
    prompt_ref_path.write_text(prompt_ref_content, encoding="utf-8")

    # 8. Write manifest
    manifest = {
        "generated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "format_id": format_id,
        "repo_name": repo_name,
        "rules_inserted": [r.id for r in rules],
        "prompt_reference": "prompt-reference.md",
    }
    manifest_path = repo_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return BuildResult(
        repo_dir=repo_dir,
        context_file=context_file,
        rules_inserted=[r.id for r in rules],
        format_id=format_id,
        prompt_reference_path=prompt_ref_path,
        manifest_path=manifest_path,
    )


# ---------------------------------------------------------------------------
# Legacy v0.1 functions — preserved for backward compatibility (Brief 4 removes these)
# ---------------------------------------------------------------------------


def _render_template(technique: Technique) -> str:
    """Render a technique's Jinja2 template with technique metadata.

    Args:
        technique: The technique whose template to render.

    Returns:
        Rendered template content.
    """
    env = jinja2.Environment(
        autoescape=False,  # noqa: S701  # nosec B701 — markdown templates, not HTML
        undefined=jinja2.StrictUndefined,
        keep_trailing_newline=True,
    )
    template = env.from_string(technique.template)
    result: str = template.render(
        objective_id=technique.objective.id,
        format_id=technique.format.id,
        technique_id=technique.id,
    )
    return result


def _generate_trigger_md(technique: Technique) -> str:
    """Generate TRIGGER.md content for a technique.

    Args:
        technique: The technique to document.

    Returns:
        TRIGGER.md content string.
    """
    return f"""# Testing Instructions

## Technique: {technique.id}
## Objective: {technique.objective.name}
## Target Assistant: {technique.format.assistant}

## Setup
1. Open this directory in {technique.format.assistant}
2. Ensure the assistant reads `{technique.format.filename}`

## Trigger Prompt
Copy and paste this prompt into the assistant:

> {technique.trigger_prompt}

## What to Look For
{technique.objective.description}

## Recording Results
```
countersignal cxp record \\
    --technique {shlex.quote(technique.id)} \\
    --assistant {shlex.quote(technique.format.assistant)} \\
    --trigger-prompt {shlex.quote(technique.trigger_prompt)} \\
    --file <path-to-generated-code>
```
"""


def _generate_readme(technique: Technique) -> str:
    """Generate README.md with security warnings.

    Args:
        technique: The technique this repo tests.

    Returns:
        README.md content string.
    """
    return f"""# CounterSignal CXP Test Repository

## WARNING -- SECURITY RESEARCH MATERIAL

**This repository contains intentionally malicious instruction files.**

It was generated by CounterSignal CXP, a context poisoning tester for AI coding assistants.
The instruction files in this repo are designed to manipulate coding assistants into
generating insecure or malicious code.

**Do not use this repository for any purpose other than authorized security testing.**

## Details

- **Technique:** {technique.id}
- **Objective:** {technique.objective.name}
- **Target Assistant:** {technique.format.assistant}
- **Poisoned File:** `{technique.format.filename}`

## How to Use

See `TRIGGER.md` for testing instructions.

## Disclaimer

This material is provided for authorized security research and red-team testing only.
The authors are not responsible for misuse. Always obtain proper authorization before
testing against systems you do not own.
"""


def _apply_mode(technique: Technique, mode: PayloadMode) -> Technique:
    """Return a technique with template and trigger prompt swapped for the given mode.

    Args:
        technique: The base technique (always explicit from the registry).
        mode: Payload mode to apply.

    Returns:
        The original technique if explicit, or a copy with stealth overrides.
    """
    if mode == PayloadMode.EXPLICIT:
        return technique
    template, trigger_prompt = load_stealth_override(technique)
    return replace(technique, template=template, trigger_prompt=trigger_prompt)


def build_repo(
    technique: Technique,
    output_dir: Path,
    repo_name: str,
    *,
    research: bool = False,
    mode: PayloadMode = PayloadMode.EXPLICIT,
) -> Path:
    """Build a test repo for the given technique.

    In clean mode (default), produces a realistic-looking project repo with no
    security research references. In research mode, includes TRIGGER.md and
    security-warning README for documentation and sharing.

    Args:
        technique: The technique to build a repo for.
        output_dir: Parent directory for the generated repo.
        repo_name: Name for the output directory (e.g. ``webapp-demo-01``).
        research: If True, include TRIGGER.md and security-warning README.
        mode: Payload mode (explicit or stealth).

    Returns:
        Path to the created repo directory.
    """
    technique = _apply_mode(technique, mode)

    repo_dir = output_dir / repo_name
    repo_dir.mkdir(parents=True, exist_ok=True)

    # Copy project skeleton
    skeleton = resource_files("countersignal.cxp.techniques") / "skeleton"
    _copy_tree(skeleton, repo_dir)

    # Render and write poisoned instruction file
    rendered = _render_template(technique)
    poisoned_path = repo_dir / technique.format.filename
    poisoned_path.parent.mkdir(parents=True, exist_ok=True)
    poisoned_path.write_text(rendered, encoding="utf-8")

    if research:
        # Write TRIGGER.md
        (repo_dir / "TRIGGER.md").write_text(_generate_trigger_md(technique), encoding="utf-8")

        # Write README.md (overwrites skeleton README)
        (repo_dir / "README.md").write_text(_generate_readme(technique), encoding="utf-8")

    return repo_dir


def _write_manifest(
    repos: list[tuple[Path, Technique]],
    output_dir: Path,
    mode: PayloadMode = PayloadMode.EXPLICIT,
) -> None:
    """Write a manifest.json with testing instructions for each generated repo.

    The manifest lives in the output directory alongside the repos (not inside
    them) and provides researchers with trigger prompts, expected indicators,
    and record commands.

    Args:
        repos: List of (repo_path, technique) tuples.
        output_dir: Output directory where manifest.json is written.
        mode: Payload mode used for generation.
    """
    manifest = {
        "generated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repos": [
            {
                "path": repo_path.name,
                "technique_id": technique.id,
                "objective": technique.objective.name,
                "format": technique.format.id,
                "assistant": technique.format.assistant,
                "poisoned_file": technique.format.filename,
                "trigger_prompt": technique.trigger_prompt,
                "what_to_look_for": technique.objective.description,
                "mode": str(mode),
                "record_command": (
                    f"countersignal cxp record --technique {shlex.quote(technique.id)}"
                    f" --assistant {shlex.quote(technique.format.assistant)}"
                    f" --trigger-prompt {shlex.quote(technique.trigger_prompt)}"
                    f" --file <path-to-generated-code>"
                ),
            }
            for repo_path, technique in repos
        ],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def build_all(
    output_dir: Path,
    objective: str | None = None,
    format_id: str | None = None,
    *,
    research: bool = False,
    mode: PayloadMode = PayloadMode.EXPLICIT,
) -> list[Path]:
    """Build repos for all techniques, optionally filtered.

    Args:
        output_dir: Parent directory for generated repos.
        objective: Filter to this objective ID only.
        format_id: Filter to this format ID only.
        research: If True, include TRIGGER.md and security-warning README.
        mode: Payload mode (explicit or stealth).

    Returns:
        List of paths to created repo directories.
    """
    techniques = list_techniques()
    if objective:
        techniques = [t for t in techniques if t.objective.id == objective]
    if format_id:
        techniques = [t for t in techniques if t.format.id == format_id]

    repos: list[tuple[Path, Technique]] = []
    for i, t in enumerate(techniques, start=1):
        repo_name = f"webapp-demo-{i:02d}"
        repo_path = build_repo(t, output_dir, repo_name, research=research, mode=mode)
        repos.append((repo_path, _apply_mode(t, mode)))

    _write_manifest(repos, output_dir, mode=mode)

    return [repo_path for repo_path, _ in repos]
