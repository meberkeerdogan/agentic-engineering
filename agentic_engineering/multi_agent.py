"""Dependency-safe isolated task execution and deterministic Git integration."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any


class MultiAgentError(ValueError):
    """Raised when isolated execution or integration cannot be trusted."""


ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _refs(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and len(value) == len(set(value))
        and all(isinstance(item, str) and item for item in value)
    )


def _safe_relative(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _run(
    command: list[str],
    cwd: Path,
    *,
    timeout: int = 60,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            check=False,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise MultiAgentError(f"command failed to execute: {command[0]}") from error


def _git(repo: Path, *arguments: str, timeout: int = 60, env: dict[str, str] | None = None) -> str:
    result = _run(["git", *arguments], repo, timeout=timeout, env=env)
    if result.returncode != 0:
        raise MultiAgentError(f"git {' '.join(arguments[:2])} failed")
    return result.stdout.strip()


def _validate_manifest(manifest: Mapping[str, Any]) -> tuple[list[str], dict[str, Mapping[str, Any]], list[list[str]]]:
    if manifest.get("version") != 1 or not isinstance(manifest.get("run_id"), str):
        raise MultiAgentError("multi-agent run must use version 1 and an ID")
    if not ID_PATTERN.fullmatch(manifest["run_id"]):
        raise MultiAgentError("run ID must be path-safe")
    tasks = manifest.get("tasks")
    parallelism = manifest.get("max_parallelism")
    if not isinstance(tasks, list) or not tasks:
        raise MultiAgentError("multi-agent run requires tasks")
    if isinstance(parallelism, bool) or not isinstance(parallelism, int) or parallelism < 1:
        raise MultiAgentError("max_parallelism must be positive")
    fixed_date = manifest.get("commit_timestamp")
    if not isinstance(fixed_date, str) or not fixed_date:
        raise MultiAgentError("commit_timestamp is required")
    validation = manifest.get("validation")
    if (
        not isinstance(validation, Mapping)
        or not isinstance(validation.get("command"), list)
        or not validation["command"]
        or not all(isinstance(part, str) and part for part in validation["command"])
        or isinstance(validation.get("timeout_seconds"), bool)
        or not isinstance(validation.get("timeout_seconds"), int)
        or validation["timeout_seconds"] < 1
    ):
        raise MultiAgentError("integration validation command is required")
    task_by_id: dict[str, Mapping[str, Any]] = {}
    declared: list[str] = []
    for task in tasks:
        if not isinstance(task, Mapping) or not isinstance(task.get("id"), str):
            raise MultiAgentError("tasks require IDs")
        task_id = task["id"]
        if task_id in task_by_id or not ID_PATTERN.fullmatch(task_id):
            raise MultiAgentError("task IDs must be unique and path-safe")
        dependencies = task.get("depends_on")
        command = task.get("command")
        allowed = task.get("allowed_paths")
        if not isinstance(dependencies, list) or len(dependencies) != len(set(dependencies)):
            raise MultiAgentError("task dependencies must be unique arrays")
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            raise MultiAgentError("task commands must be argument arrays")
        if not isinstance(allowed, list) or not allowed or len(allowed) != len(set(allowed)):
            raise MultiAgentError("tasks require unique allowed paths")
        if any(not _safe_relative(path) for path in allowed):
            raise MultiAgentError("allowed paths must be safe and relative")
        if not _refs(task.get("evidence_refs")):
            raise MultiAgentError("tasks require unique evidence references")
        timeout = task.get("timeout_seconds")
        if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout < 1:
            raise MultiAgentError("task timeouts must be positive")
        declared.append(task_id)
        task_by_id[task_id] = task
    known = set(declared)
    if any(dependency not in known for task in tasks for dependency in task["depends_on"]):
        raise MultiAgentError("dependencies must reference declared tasks")
    completed: set[str] = set()
    remaining = set(declared)
    waves: list[list[str]] = []
    index = {task_id: position for position, task_id in enumerate(declared)}
    while remaining:
        ready = sorted(
            (task_id for task_id in remaining if set(task_by_id[task_id]["depends_on"]) <= completed),
            key=index.__getitem__,
        )
        if not ready:
            raise MultiAgentError("task dependencies contain a cycle")
        for offset in range(0, len(ready), parallelism):
            wave = ready[offset : offset + parallelism]
            waves.append(wave)
            completed.update(wave)
            remaining.difference_update(wave)
    return declared, task_by_id, waves


def _changed_paths(worktree: Path) -> list[str]:
    lines = _git(worktree, "status", "--porcelain").splitlines()
    paths = []
    for line in lines:
        if len(line) < 4 or " -> " in line:
            raise MultiAgentError("renames and malformed Git status are not supported")
        paths.append(Path(line[3:]).as_posix())
    return sorted(paths)


def run_isolated_tasks(repository: Path, manifest: Mapping[str, Any], run_root: Path) -> dict[str, Any]:
    """Execute task adapters in worktrees and integrate validated commits."""

    repository = repository.resolve()
    run_root = run_root.resolve()
    if not repository.is_dir() or not (repository / ".git").exists():
        raise MultiAgentError("repository must be a Git worktree")
    if run_root.exists() or run_root == repository or repository in run_root.parents:
        raise MultiAgentError("run root must be a new directory outside the repository")
    if _git(repository, "status", "--porcelain"):
        raise MultiAgentError("source repository must be clean")
    declared, task_by_id, waves = _validate_manifest(manifest)
    base_revision = _git(repository, "rev-parse", "HEAD")
    worktree_root = run_root / "worktrees"
    worktree_root.mkdir(parents=True)
    fixed_date = manifest["commit_timestamp"]
    commit_env = os.environ.copy()
    commit_env.update(
        {
            "GIT_AUTHOR_NAME": "Agentic Engineering",
            "GIT_AUTHOR_EMAIL": "agentic-engineering@example.invalid",
            "GIT_COMMITTER_NAME": "Agentic Engineering",
            "GIT_COMMITTER_EMAIL": "agentic-engineering@example.invalid",
            "GIT_AUTHOR_DATE": fixed_date,
            "GIT_COMMITTER_DATE": fixed_date,
        }
    )
    commits: dict[str, str] = {}
    task_results: list[dict[str, Any]] = []
    for wave in waves:
        worktrees: dict[str, Path] = {}
        for task_id in wave:
            worktree = worktree_root / task_id
            branch = f"ae-{manifest['run_id']}-{task_id}"
            _git(repository, "worktree", "add", "-b", branch, str(worktree), base_revision)
            for dependency in task_by_id[task_id]["depends_on"]:
                _git(worktree, "cherry-pick", commits[dependency])
            worktrees[task_id] = worktree

        def execute(task_id: str) -> tuple[str, subprocess.CompletedProcess[str]]:
            task = task_by_id[task_id]
            command = [sys.executable if part == "{python}" else part for part in task["command"]]
            return task_id, _run(command, worktrees[task_id], timeout=task["timeout_seconds"])

        with ThreadPoolExecutor(max_workers=manifest["max_parallelism"]) as pool:
            execution_results = dict(pool.map(execute, wave))
        for task_id in wave:
            result = execution_results[task_id]
            if result.returncode != 0:
                raise MultiAgentError(f"task command exited nonzero: {task_id}")
            changed = _changed_paths(worktrees[task_id])
            allowed = {Path(path).as_posix() for path in task_by_id[task_id]["allowed_paths"]}
            if not changed or any(path not in allowed for path in changed):
                raise MultiAgentError(f"task changed undeclared paths: {task_id}")
            for path in changed:
                output = worktrees[task_id] / path
                if output.is_symlink() or getattr(output, "is_junction", lambda: False)():
                    raise MultiAgentError("task outputs may not be links")
                candidate = output.resolve()
                try:
                    candidate.relative_to(worktrees[task_id])
                except ValueError as error:
                    raise MultiAgentError("task change escapes its worktree") from error
            _git(worktrees[task_id], "add", "--", *changed)
            _git(worktrees[task_id], "commit", "-m", f"Complete isolated task {task_id}", env=commit_env)
            commit = _git(worktrees[task_id], "rev-parse", "HEAD")
            commits[task_id] = commit
            task_results.append(
                {
                    "task_id": task_id,
                    "status": "completed",
                    "commit": commit,
                    "changed_paths": changed,
                    "stdout_sha256": hashlib.sha256(result.stdout.encode("utf-8")).hexdigest(),
                    "stderr_sha256": hashlib.sha256(result.stderr.encode("utf-8")).hexdigest(),
                }
            )
    integration = worktree_root / "integration"
    integration_branch = f"ae-{manifest['run_id']}-integration"
    _git(repository, "worktree", "add", "-b", integration_branch, str(integration), base_revision)
    for task_id in declared:
        _git(integration, "cherry-pick", commits[task_id])
    validation = manifest["validation"]
    validation_command = [sys.executable if part == "{python}" else part for part in validation["command"]]
    validation_result = _run(
        validation_command, integration, timeout=validation["timeout_seconds"]
    )
    if validation_result.returncode != 0 or _git(integration, "status", "--porcelain"):
        raise MultiAgentError("integrated validation failed or mutated the worktree")
    report: dict[str, Any] = {
        "version": 1,
        "run_id": manifest["run_id"],
        "source_fingerprint": _fingerprint(manifest),
        "base_revision": base_revision,
        "parallel_waves": waves,
        "task_results": task_results,
        "integration_revision": _git(integration, "rev-parse", "HEAD"),
        "validation": {
            "outcome": "pass",
            "stdout_sha256": hashlib.sha256(validation_result.stdout.encode("utf-8")).hexdigest(),
            "stderr_sha256": hashlib.sha256(validation_result.stderr.encode("utf-8")).hexdigest(),
        },
        "conflicts": [],
        "human_interventions": 0,
        "worktree_refs": {
            task_id: f"worktrees/{task_id}" for task_id in declared
        }
        | {"integration": "worktrees/integration"},
    }
    fingerprint = _fingerprint(report)
    report["report_id"] = f"multi-agent-{fingerprint[:16]}"
    report["fingerprint"] = fingerprint
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    report = run_isolated_tasks(
        arguments.repository,
        json.loads(arguments.manifest.read_text("utf-8")),
        arguments.run_root,
    )
    arguments.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
