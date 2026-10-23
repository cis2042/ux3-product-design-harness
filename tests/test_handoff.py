"""One-pass handoff validation preserves the boundary while avoiding duplicate checks."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.check_review import check_handoff

ROOT = Path(__file__).resolve().parents[1]


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.review = json.loads((ROOT / "examples/live-coding-review.json").read_text())
        self.pack = json.loads((ROOT / "examples/live-coding-context-pack.json").read_text())

    def test_existing_handoff_passes(self):
        self.assertEqual([], check_handoff(self.review, self.pack))

    def test_scope_cannot_expand_during_handoff(self):
        self.pack["execution_boundary"]["may_do"].append("Add a new workflow.")
        self.assertTrue(any("execution_boundary" in e for e in check_handoff(self.review, self.pack)))

    def test_identity_evidence_and_controls_cannot_drift(self):
        for field, value in [
            ("review_id", "another-review"),
            ("evidence_snapshot_ids", ["another-source"]),
            ("stop_conditions", ["Never stop."]),
            ("actor_boundary", dict(self.pack["actor_boundary"], target_population=["Everyone"])),
        ]:
            with self.subTest(field=field):
                pack = copy.deepcopy(self.pack)
                pack[field] = value
                self.assertTrue(check_handoff(self.review, pack))

    def test_verify_and_stop_do_not_authorize_handoff(self):
        for name in ["standard-gate-review.json", "stop-reframe-review.json"]:
            with self.subTest(name=name):
                review = json.loads((ROOT / "examples" / name).read_text())
                errors = check_handoff(review, self.pack)
                self.assertIn("context pack requires a continue review", errors)

    def test_missing_and_malformed_pack_rejected_without_crash(self):
        for pack in [{}, [], None]:
            with self.subTest(pack=pack):
                self.assertTrue(check_handoff(self.review, pack))

    def test_invalid_review_cannot_be_hidden_by_valid_pack(self):
        self.review["evidence_tier"] = "t0"
        self.assertTrue(check_handoff(self.review, self.pack))

    def test_single_invocation_supports_installed_bundle(self):
        for base in [ROOT, ROOT / "skills/product-design-harness/resources"]:
            for review, pack in [
                ("live-coding-review.json", "live-coding-context-pack.json"),
                ("quick-gate-review.json", "quick-context-pack.json"),
            ]:
                with self.subTest(base=base, review=review):
                    result = subprocess.run([
                        sys.executable, str(base / "scripts/check_review.py"),
                        str(base / "examples" / review),
                        "--context-pack", str(base / "examples" / pack),
                    ], capture_output=True, text=True)
                    self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
