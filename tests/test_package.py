from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "project-template/.tasks/tools"))
from taskctl import TaskStore


class PackageTest(unittest.TestCase):
    def test_skills_are_self_contained(self):
        for name in ("architect", "verification-owner", "coding-owner"):
            path = ROOT / "skills" / name / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            metadata = yaml.safe_load(text.split("---", 2)[1])
            self.assertEqual(metadata["name"], name)
            self.assertTrue(metadata["description"])
            for ref in re.findall(r"\]\((references/[^)]+)\)", text):
                self.assertTrue((path.parent / ref).is_file(), ref)

    def test_relative_markdown_links_resolve(self):
        for path in ROOT.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" in target or target.startswith("#"):
                    continue
                target = target.split("#", 1)[0]
                self.assertTrue((path.parent / target).exists(), f"{path}: {target}")

    def test_template_can_be_copied_to_unrelated_workspace(self):
        with tempfile.TemporaryDirectory(prefix=".workflow-test-", dir=ROOT) as tmp:
            target = Path(tmp) / "unrelated-project"
            shutil.copytree(ROOT / "project-template", target)
            for folder in ("skills", "templates", "docs"):
                shutil.copytree(ROOT / folder, target / ".workflow" / folder)
            for path in [*(target / "docs").glob("*.md"), *(target / ".workflow/docs").glob("*.md")]:
                for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                    if "://" not in link and not link.startswith("#"):
                        self.assertTrue((path.parent / link.split("#", 1)[0]).exists(), f"deployed link: {path}: {link}")
            store = TaskStore(target)
            for template, output in (("task-card", store.active_root), ("evidence", store.evidence_root)):
                doc = yaml.safe_load((ROOT / f"templates/{template}.yaml").read_text(encoding="utf-8"))
                (output / "TASK-001.yaml").write_text(yaml.safe_dump(doc), encoding="utf-8")
            store.reindex()
            self.assertEqual(store.validate(), [])
            self.assertIsNone(store.context("TASK-001", "coding-owner")["verification"])

    def test_no_retired_paths_or_local_identity(self):
        for folder in ("skills", "project-template", "templates", "examples"):
            for path in (ROOT / folder).rglob("*"):
                if path.suffix not in {".md", ".yaml", ".py"}:
                    continue
                text = path.read_text(encoding="utf-8")
                for retired in (".tasks/tasks.yaml", "pre-cutover", "migrate_tasks_v1", "1324gcws", "hsc-frontend"):
                    self.assertNotIn(retired, text, str(path))

    def test_example_tools_match_distribution(self):
        self.assertEqual(
            (ROOT / "project-template/.tasks/tools/taskctl.py").read_bytes(),
            (ROOT / "examples/report-export/.tasks/tools/taskctl.py").read_bytes(),
        )


if __name__ == "__main__":
    unittest.main()
