from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import contextlib
import io
import shutil
import sys
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "project-template/.tasks/tools"))
from taskctl import TaskStore, canonical_fingerprint, main

class TaskStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix=".workflow-test-", dir=ROOT)
        self.project = Path(self.tmp.name) / "project"
        shutil.copytree(ROOT / "examples/report-export", self.project)
        self.store = TaskStore(self.project)
    def tearDown(self):
        self.tmp.cleanup()
    def edit(self, path, change):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        change(doc)
        path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    def card(self, task_id, change):
        self.edit(self.store.active_root / f"{task_id}.yaml", lambda d: change(d["task"]))
        self.store.reindex()
    def mark_done(self, accepted=True):
        self.card("TASK-002", lambda t: t.update(status="done"))
        if accepted:
            self.edit(self.store.evidence_root / "TASK-002.yaml", lambda d: d["records"].append({
                "type": "user_acceptance", "status": "pass", "summary": "synthetic test acceptance"}))
    def test_empty_template(self):
        target = Path(self.tmp.name) / "empty"
        shutil.copytree(ROOT / "project-template", target)
        self.assertEqual(TaskStore(target).validate(), [])
    def test_example(self):
        self.assertEqual(self.store.validate(), [])
    def test_role_context(self):
        self.assertNotIn("verification", self.store.context("TASK-002", "architect"))
        v = self.store.context("TASK-002", "verification-owner")
        self.assertIn("verification", v)
        self.assertNotIn("evidence", v)
        c = self.store.context("TASK-002", "coding-owner")
        self.assertEqual(c["hard_dependencies"][0]["status"], "done")
        self.assertEqual(c["evidence"]["task_id"], "TASK-002")
        self.assertNotIn("SYNTHETIC: 虚构用户", yaml.safe_dump(c, allow_unicode=True))
    def test_fingerprint_stability(self):
        _, t = self.store.find("TASK-002")
        initial = canonical_fingerprint(t)
        t = deepcopy(t)
        t.update(status="in_progress")
        t["result"].update(owner="new-owner", attempts=3)
        self.assertEqual(initial, canonical_fingerprint(t))
        t["acceptance"][0]["expect"] = "changed behavior"
        self.assertNotEqual(initial, canonical_fingerprint(t))
    def test_fingerprint_cli(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.project), "fingerprint", "TASK-002"]), 0)
        self.assertEqual(output.getvalue().strip(), self.store.find("TASK-002")[1]["verification"]["basis_fingerprint"])
    def test_stale_index(self):
        self.edit(self.store.index_path, lambda d: d["active"][0].update(title="stale"))
        self.assertIn("index is stale", self.store.validate())
    def test_stale_or_missing_spec(self):
        self.card("TASK-002", lambda t: t.update(goal="changed goal"))
        self.assertTrue(any("fingerprint mismatch" in e for e in self.store.validate()))
        (self.store.verification_root / "TASK-002.yaml").unlink()
        self.assertTrue(any("spec is missing" in e for e in self.store.validate()))
    def test_missing_verification_blocks_ready(self):
        self.card("TASK-003", lambda t: t.update(status="ready"))
        self.assertTrue(any("no ready verification" in e for e in self.store.validate()))
    def test_hard_blockers(self):
        self.card("TASK-002", lambda t: t.update(relations=[{"task":"TASK-003", "type":"hard"}]))
        self.assertTrue(any("has hard blockers" in e for e in self.store.validate()))
    def test_missing_relation_and_cycle(self):
        self.card("TASK-003", lambda t: t.update(relations=[{"task":"TASK-404", "type":"coordination"}]))
        self.assertTrue(any("unresolved relation" in e for e in self.store.validate()))
        self.card("TASK-003", lambda t: t.update(relations=[{"task":"TASK-002", "type":"hard"}]))
        self.card("TASK-002", lambda t: t.update(relations=[{"task":"TASK-003", "type":"hard"}]))
        self.assertTrue(any("hard relation cycle" in e for e in self.store.validate()))
    def test_wrong_artifact_owner(self):
        self.edit(self.store.evidence_root / "TASK-002.yaml", lambda d: d.update(task_id="TASK-003"))
        self.edit(self.store.verification_root / "TASK-002.yaml", lambda d: d.update(task_id="TASK-003"))
        errors = self.store.validate()
        self.assertTrue(any("evidence task_id mismatch" in e for e in errors))
        self.assertTrue(any("verification task_id mismatch" in e for e in errors))
    def test_waiver_reason(self):
        self.card("TASK-003", lambda t: t["verification"].update(status="waived", waiver_reason=""))
        self.assertTrue(any("no concrete reason" in e for e in self.store.validate()))
    def test_archive_gates(self):
        with self.assertRaisesRegex(ValueError, "only done"):
            self.store.archive("TASK-002", "report-export")
        self.mark_done(accepted=False)
        with self.assertRaisesRegex(ValueError, "no passing user acceptance"):
            self.store.archive("TASK-002", "report-export")
    def test_archive_preserves_basis_and_hashes(self):
        self.mark_done()
        before = canonical_fingerprint(self.store.find("TASK-002")[1])
        dest = self.store.archive("TASK-002", "report-export")
        self.assertTrue((dest / "verification.yaml").exists())
        self.assertEqual(before, canonical_fingerprint(self.store.find("TASK-002")[1]))
        self.assertEqual(self.store.validate(), [])
        self.edit(dest / "evidence.yaml", lambda d: d["records"][0].update(summary="tampered"))
        self.assertIn("archive manifest or hashes are stale", self.store.validate())
    def test_archive_path_guard(self):
        self.mark_done()
        with self.assertRaisesRegex(ValueError, "safe directory name"):
            self.store.archive("TASK-002", "../escape")
        self.assertTrue((self.store.active_root / "TASK-002.yaml").exists())
    def test_archive_copy_failure(self):
        self.mark_done()
        with patch("taskctl.shutil.copy2", side_effect=OSError("copy failed")):
            with self.assertRaisesRegex(OSError, "copy failed"):
                self.store.archive("TASK-002", "report-export")
        for path in (self.store.active_root, self.store.evidence_root, self.store.verification_root):
            self.assertTrue((path / "TASK-002.yaml").exists())
    def test_archive_postflight_rollback(self):
        self.mark_done()
        with patch.object(self.store, "validate", side_effect=[[], ["injected failure"]]):
            with self.assertRaisesRegex(ValueError, "postflight failed"):
                self.store.archive("TASK-002", "report-export")
        self.assertTrue((self.store.active_root / "TASK-002.yaml").exists())
        self.assertFalse((self.store.archive_root / "report-export/TASK-002").exists())

if __name__ == "__main__":
    unittest.main()
