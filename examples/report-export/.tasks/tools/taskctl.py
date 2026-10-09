from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

import yaml


SCHEMA_VERSION = 2
STABLE_FIELDS = (
    "id",
    "goal",
    "scope",
    "constraints",
    "forbidden",
    "acceptance",
    "relations",
    "dependencies",
    "parallelism",
    "risk_level",
    "escalation_conditions",
)
ROLES = ("architect", "verification-owner", "coding-owner")
TASK_ID_PATTERN = re.compile(r"^TASK-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
WORK_PACKAGE_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _read_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def _write_yaml(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8", newline="\n")
    temporary.replace(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _normalise_strings(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace("\r\n", "\n").replace("\r", "\n")
    if isinstance(value, list):
        return [_normalise_strings(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _normalise_strings(value[key])
            for key in sorted(value.keys(), key=lambda item: str(item))
        }
    return value


def stable_payload(task: dict[str, Any]) -> dict[str, Any]:
    return {field: deepcopy(task[field]) for field in STABLE_FIELDS if field in task}


def canonical_fingerprint(task: dict[str, Any]) -> str:
    payload = _normalise_strings(stable_payload(task))
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def hard_relations(task: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for dependency in task.get("dependencies") or []:
        if dependency not in result:
            result.append(dependency)
    for relation in task.get("relations") or []:
        if relation.get("type") == "hard" and relation.get("task") not in result:
            result.append(relation["task"])
    return result


def all_relation_targets(task: dict[str, Any]) -> list[str]:
    result = list(hard_relations(task))
    for relation in task.get("relations") or []:
        target = relation.get("task")
        if isinstance(target, str) and target not in result:
            result.append(target)
    return result


def require_task_id(value: str) -> None:
    if not TASK_ID_PATTERN.fullmatch(value):
        raise ValueError(f"invalid task id: {value}")


def require_work_package(value: str) -> None:
    if not WORK_PACKAGE_PATTERN.fullmatch(value):
        raise ValueError("work_package must be one safe directory name using lowercase letters, digits and hyphens")


class TaskStore:
    def __init__(self, project_root: Path | str) -> None:
        self.project_root = Path(project_root).resolve()
        self.tasks_root = self.project_root / ".tasks"
        self.active_root = self.tasks_root / "cards" / "active"
        self.archive_root = self.tasks_root / "archive"
        self.evidence_root = self.tasks_root / "evidence"
        self.verification_root = self.tasks_root / "verification"
        self.index_path = self.tasks_root / "index.yaml"
        self.archive_manifest_path = self.archive_root / "manifest.yaml"

    def _active_paths(self) -> list[Path]:
        return sorted(self.active_root.glob("TASK-*.yaml")) if self.active_root.exists() else []

    def _archive_paths(self) -> list[Path]:
        if not self.archive_root.exists():
            return []
        return sorted(self.archive_root.glob("*/TASK-*/task.yaml"))

    def _load_card(self, path: Path) -> dict[str, Any]:
        document = _read_yaml(path)
        task = document.get("task")
        if not isinstance(task, dict):
            raise ValueError(f"{path} does not contain a task mapping")
        return task

    def all_tasks(self) -> dict[str, tuple[Path, dict[str, Any]]]:
        result: dict[str, tuple[Path, dict[str, Any]]] = {}
        duplicates: list[str] = []
        for path in [*self._active_paths(), *self._archive_paths()]:
            task = self._load_card(path)
            task_id = task.get("id")
            if not isinstance(task_id, str):
                raise ValueError(f"{path} has no string task id")
            require_task_id(task_id)
            path_task_id = path.stem if path.parent == self.active_root else path.parent.name
            if path_task_id != task_id:
                raise ValueError(f"{path}: card path does not match task id {task_id}")
            if task_id in result:
                duplicates.append(task_id)
            result[task_id] = (path, task)
        if duplicates:
            raise ValueError(f"duplicate task ids: {', '.join(sorted(set(duplicates)))}")
        return result

    def find(self, task_id: str) -> tuple[Path, dict[str, Any]]:
        require_task_id(task_id)
        active = self.active_root / f"{task_id}.yaml"
        candidates = [active] if active.exists() else []
        candidates.extend(self.archive_root.glob(f"*/{task_id}/task.yaml"))
        if not candidates:
            raise KeyError(f"task not found: {task_id}")
        if len(candidates) > 1:
            raise ValueError(f"task id has multiple cards: {task_id}")
        path = candidates[0]
        return path, self._load_card(path)

    def evidence_path(self, task: dict[str, Any]) -> Path:
        result = task.get("result") or {}
        reference = result.get("evidence_ref")
        if not reference:
            raise ValueError(f"{task.get('id')} has no evidence_ref")
        return self.project_root / Path(reference)

    def verification_path(self, task: dict[str, Any]) -> Path | None:
        verification = task.get("verification") or {}
        reference = verification.get("spec")
        return self.project_root / Path(reference) if reference else None

    def build_index(self) -> dict[str, Any]:
        all_tasks = self.all_tasks()
        active: list[dict[str, Any]] = []
        for path in self._active_paths():
            task = self._load_card(path)
            dependencies = hard_relations(task)
            blocked_by = [
                task_id
                for task_id in dependencies
                if task_id not in all_tasks or all_tasks[task_id][1].get("status") != "done"
            ]
            verification = task.get("verification") or {}
            result = task.get("result") or {}
            active.append(
                {
                    "id": task["id"],
                    "title": task.get("title"),
                    "status": task.get("status"),
                    "risk_level": task.get("risk_level"),
                    "card": _relative(path, self.project_root),
                    "verification": verification.get("spec"),
                    "evidence": result.get("evidence_ref"),
                    "hard_dependencies": dependencies,
                    "blocked_by": blocked_by,
                }
            )
        return {
            "schema_version": SCHEMA_VERSION,
            "generated": True,
            "active": active,
        }

    def reindex(self) -> dict[str, Any]:
        index = self.build_index()
        _write_yaml(self.index_path, index)
        return index

    def build_archive_manifest(self) -> dict[str, Any]:
        archived: list[dict[str, Any]] = []
        for task_path in self._archive_paths():
            task = self._load_card(task_path)
            directory = task_path.parent
            entry: dict[str, Any] = {
                "id": task["id"],
                "task": _relative(task_path, self.project_root),
                "task_sha256": _sha256(task_path),
            }
            for kind in ("evidence", "verification"):
                artifact = directory / f"{kind}.yaml"
                entry[kind] = _relative(artifact, self.project_root) if artifact.exists() else None
                entry[f"{kind}_sha256"] = _sha256(artifact) if artifact.exists() else None
            archived.append(entry)
        return {
            "schema_version": 1,
            "generated": True,
            "archived": archived,
        }

    def write_archive_manifest(self) -> dict[str, Any]:
        manifest = self.build_archive_manifest()
        _write_yaml(self.archive_manifest_path, manifest)
        return manifest

    def context(self, task_id: str, role: str) -> dict[str, Any]:
        if role not in ROLES:
            raise ValueError(f"role must be one of: {', '.join(ROLES)}")
        task_path, task = self.find(task_id)
        all_tasks = self.all_tasks()
        dependencies: list[dict[str, Any]] = []
        for dependency_id in hard_relations(task):
            if dependency_id not in all_tasks:
                dependencies.append({"id": dependency_id, "status": "unresolved"})
                continue
            dependency_path, dependency = all_tasks[dependency_id]
            dependencies.append(
                {
                    "id": dependency_id,
                    "title": dependency.get("title"),
                    "status": dependency.get("status"),
                    "card": _relative(dependency_path, self.project_root),
                }
            )
        result: dict[str, Any] = {
            "schema_version": 1,
            "role": role,
            "task_path": _relative(task_path, self.project_root),
            "task": task,
            "hard_dependencies": dependencies,
            "architecture": ".tasks/architecture.md",
        }
        if role in ("verification-owner", "coding-owner"):
            verification_path = self.verification_path(task)
            result["verification_path"] = (
                _relative(verification_path, self.project_root) if verification_path else None
            )
            result["verification"] = (
                _read_yaml(verification_path) if verification_path and verification_path.exists() else None
            )
        if role == "coding-owner":
            evidence_path = self.evidence_path(task)
            result["evidence_path"] = _relative(evidence_path, self.project_root)
            result["evidence"] = _read_yaml(evidence_path)
        return result

    def validate(self, allowed_active_done: str | None = None) -> list[str]:
        errors: list[str] = []
        try:
            all_tasks = self.all_tasks()
        except (ValueError, OSError, yaml.YAMLError) as exc:
            return [str(exc)]

        if not self.index_path.exists():
            errors.append("index is missing")
        else:
            try:
                if _read_yaml(self.index_path) != self.build_index():
                    errors.append("index is stale")
            except (ValueError, OSError, yaml.YAMLError) as exc:
                errors.append(f"index cannot be read: {exc}")

        if not self.archive_manifest_path.exists():
            errors.append("archive manifest is missing")
        else:
            try:
                if _read_yaml(self.archive_manifest_path) != self.build_archive_manifest():
                    errors.append("archive manifest or hashes are stale")
            except (ValueError, OSError, yaml.YAMLError) as exc:
                errors.append(f"archive manifest cannot be read: {exc}")

        graph: dict[str, list[str]] = {}
        active_paths = set(self._active_paths())
        for task_id, (path, task) in all_tasks.items():
            archived = path not in active_paths
            if archived and task.get("status") != "done":
                errors.append(f"{task_id}: archived task is not done")
            if not archived and task.get("status") == "done" and task_id != allowed_active_done:
                errors.append(f"{task_id}: done task remains active")

            dependencies = hard_relations(task)
            graph[task_id] = dependencies
            for relation_id in all_relation_targets(task):
                if relation_id == task_id:
                    errors.append(f"{task_id}: self relation is not allowed")
                elif relation_id not in all_tasks:
                    errors.append(f"{task_id}: unresolved relation {relation_id}")

            result = task.get("result") or {}
            evidence_ref = result.get("evidence_ref")
            if not evidence_ref:
                errors.append(f"{task_id}: evidence_ref is missing")
            else:
                evidence_path = (self.project_root / Path(evidence_ref)).resolve()
                expected_evidence = (
                    path.parent / "evidence.yaml"
                    if archived
                    else self.evidence_root / f"{task_id}.yaml"
                ).resolve()
                if evidence_path != expected_evidence:
                    errors.append(f"{task_id}: evidence path does not match task layout")
                if not evidence_path.exists():
                    errors.append(f"{task_id}: evidence file is missing: {evidence_ref}")
                else:
                    try:
                        evidence = _read_yaml(evidence_path)
                        if evidence.get("task_id") != task_id:
                            errors.append(f"{task_id}: evidence task_id mismatch")
                        for field in ("records", "verification_deviations", "follow_up_candidates"):
                            if not isinstance(evidence.get(field), list):
                                errors.append(f"{task_id}: evidence {field} must be a list")
                    except (ValueError, OSError, yaml.YAMLError) as exc:
                        errors.append(f"{task_id}: evidence cannot be read: {exc}")

            verification = task.get("verification") or {}
            if verification.get("status") == "waived":
                waiver_reason = verification.get("waiver_reason")
                if not isinstance(waiver_reason, str) or not waiver_reason.strip():
                    errors.append(f"{task_id}: waived verification has no concrete reason")
            spec_ref = verification.get("spec")
            spec_path = (self.project_root / Path(spec_ref)).resolve() if spec_ref else None
            if spec_path:
                expected_spec = (
                    path.parent / "verification.yaml"
                    if archived
                    else self.verification_root / f"{task_id}.yaml"
                ).resolve()
                if spec_path != expected_spec:
                    errors.append(f"{task_id}: verification path does not match task layout")
            if verification.get("status") == "ready":
                if not spec_path or not spec_path.exists():
                    errors.append(f"{task_id}: ready verification spec is missing")
                else:
                    try:
                        spec = _read_yaml(spec_path)
                        if spec.get("task_id") != task_id:
                            errors.append(f"{task_id}: verification task_id mismatch")
                        expected = canonical_fingerprint(task)
                        actual = verification.get("basis_fingerprint")
                        spec_actual = (spec.get("basis") or {}).get("task_card_fingerprint")
                        if actual != expected or spec_actual != expected:
                            errors.append(f"{task_id}: verification fingerprint mismatch")
                    except (ValueError, OSError, yaml.YAMLError) as exc:
                        errors.append(f"{task_id}: verification spec cannot be read: {exc}")

            if task.get("status") in {"ready", "in_progress", "awaiting_acceptance"}:
                blockers = [
                    dependency_id
                    for dependency_id in dependencies
                    if dependency_id not in all_tasks
                    or all_tasks[dependency_id][1].get("status") != "done"
                ]
                if blockers:
                    errors.append(f"{task_id}: status {task.get('status')} has hard blockers {blockers}")
                if verification.get("status") not in {"ready", "waived"}:
                    errors.append(f"{task_id}: status {task.get('status')} has no ready verification")

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str, chain: list[str]) -> None:
            if task_id in visiting:
                cycle = chain[chain.index(task_id) :] + [task_id]
                message = f"hard relation cycle: {' -> '.join(cycle)}"
                if message not in errors:
                    errors.append(message)
                return
            if task_id in visited or task_id not in graph:
                return
            visiting.add(task_id)
            for dependency_id in graph[task_id]:
                visit(dependency_id, [*chain, dependency_id])
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in graph:
            visit(task_id, [task_id])

        return errors

    def archive(self, task_id: str, work_package: str) -> Path:
        require_task_id(task_id)
        require_work_package(work_package)
        source = self.active_root / f"{task_id}.yaml"
        if not source.exists():
            raise ValueError(f"active task not found: {task_id}")
        task = self._load_card(source)
        if task.get("status") != "done":
            raise ValueError("only done tasks may be archived")
        evidence_path = self.evidence_path(task)
        evidence = _read_yaml(evidence_path)
        accepted = any(
            item.get("type") == "user_acceptance" and item.get("status") == "pass"
            for item in evidence.get("records") or []
        )
        if not accepted:
            raise ValueError("done task has no passing user acceptance evidence")

        preflight_errors = self.validate(allowed_active_done=task_id)
        if preflight_errors:
            raise ValueError("task store preflight failed:\n- " + "\n- ".join(preflight_errors))

        destination = self.archive_root / work_package / task_id
        if destination.exists():
            raise ValueError(f"archive destination already exists: {destination}")
        staging = self.archive_root / ".staging" / f"{work_package}-{task_id}"
        if staging.exists():
            raise ValueError(f"archive staging already exists: {staging}")
        original_document = _read_yaml(source)
        verification_path = self.verification_path(task)
        archived_evidence = destination / "evidence.yaml"
        archived_verification = destination / "verification.yaml"
        committed = False
        try:
            staging.mkdir(parents=True)
            shutil.copy2(evidence_path, staging / "evidence.yaml")
            task.setdefault("result", {})["evidence_ref"] = _relative(
                archived_evidence, self.project_root
            )
            if verification_path and verification_path.exists():
                shutil.copy2(verification_path, staging / "verification.yaml")
                task.setdefault("verification", {})["spec"] = _relative(
                    archived_verification, self.project_root
                )
            _write_yaml(staging / "task.yaml", {"schema_version": SCHEMA_VERSION, "task": task})

            destination.parent.mkdir(parents=True, exist_ok=True)
            staging.replace(destination)
            committed = True
            evidence_path.unlink()
            if verification_path and verification_path.exists():
                verification_path.unlink()
            source.unlink()
            self.reindex()
            self.write_archive_manifest()
            postflight_errors = self.validate()
            if postflight_errors:
                raise ValueError("task store postflight failed:\n- " + "\n- ".join(postflight_errors))
            return destination
        except Exception:
            if committed and destination.exists():
                evidence_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination / "evidence.yaml", evidence_path)
                if (destination / "verification.yaml").exists() and verification_path:
                    verification_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(destination / "verification.yaml", verification_path)
                _write_yaml(source, original_document)
                shutil.rmtree(destination)
                self.reindex()
                self.write_archive_manifest()
            raise
        finally:
            if staging.exists():
                shutil.rmtree(staging)
            staging_root = self.archive_root / ".staging"
            if staging_root.exists() and not any(staging_root.iterdir()):
                staging_root.rmdir()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Locate and validate the sharded task store")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="print the generated active index")
    show = sub.add_parser("show", help="print one authoritative task card")
    show.add_argument("task_id")
    context = sub.add_parser("context", help="print minimum role-specific task context")
    context.add_argument("task_id")
    context.add_argument("--role", choices=ROLES, required=True)
    fingerprint = sub.add_parser("fingerprint", help="print stable task basis SHA-256")
    fingerprint.add_argument("task_id")
    sub.add_parser("validate", help="validate cards, references, graph, fingerprints and indexes")
    sub.add_parser("reindex", help="regenerate derived indexes")
    archive = sub.add_parser("archive", help="archive one accepted done task")
    archive.add_argument("task_id")
    archive.add_argument("--work-package", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    store = TaskStore(args.root)
    if args.command == "list":
        print(yaml.safe_dump(_read_yaml(store.index_path), allow_unicode=True, sort_keys=False))
    elif args.command == "show":
        path, task = store.find(args.task_id)
        print(f"# source: {_relative(path, store.project_root)}")
        print(yaml.safe_dump(task, allow_unicode=True, sort_keys=False))
    elif args.command == "context":
        print(yaml.safe_dump(store.context(args.task_id, args.role), allow_unicode=True, sort_keys=False))
    elif args.command == "fingerprint":
        _, task = store.find(args.task_id)
        print(canonical_fingerprint(task))
    elif args.command == "validate":
        errors = store.validate()
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"PASS: {len(store.all_tasks())} task cards validated")
    elif args.command == "reindex":
        store.reindex()
        store.write_archive_manifest()
        print("PASS: indexes regenerated")
    elif args.command == "archive":
        destination = store.archive(args.task_id, args.work_package)
        print(f"PASS: archived at {_relative(destination, store.project_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
