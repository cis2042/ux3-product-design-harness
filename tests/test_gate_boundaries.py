import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.jev_gate import classify_route_baseline, evaluate_three_lanes_baseline, generate_boundary

ROOT = Path(__file__).resolve().parents[1]


def example(name):
    return json.loads((ROOT / "examples" / name).read_text())


class GateBoundaryTests(unittest.TestCase):
    def test_large_scope_takes_priority_over_routine_words(self):
        self.assertEqual("commitment", classify_route_baseline("Update README", {"files_changed": 20}))

    def test_invalid_scope_is_rejected(self):
        for count in [-1, "20", True, None]:
            with self.subTest(count=count), self.assertRaises(ValueError):
                classify_route_baseline("Update README", {"files_changed": count})

    def test_unsupported_evidence_tiers_cannot_authorize_continue(self):
        for tier in ["not-a-tier", "t5", "T2", "", None, 2, []]:
            with self.subTest(tier=tier), self.assertRaises(ValueError):
                evaluate_three_lanes_baseline({"evidence_tier": tier})

    def test_assessments_remain_advisory_for_all_supported_tiers(self):
        for tier, verdict in [("t0", "stop_reframe"), ("t1", "verify"), ("t2", "continue"), ("t3", "continue"), ("t4", "continue")]:
            with self.subTest(tier=tier):
                result = evaluate_three_lanes_baseline({"evidence_tier": tier})
                self.assertEqual(verdict, result["combined_verdict"])
                self.assertTrue(result["advisory"])

    def test_unreviewed_tasks_never_receive_execution_boundaries(self):
        for state in [None, [], {}, {"review": []}, {"review": {}}, {"evidence_tier": "t1", "files": ["app.py"]}, {"evidence_tier": "t4", "files": ["app.py"]}]:
            with self.subTest(state=state), self.assertRaises(ValueError):
                generate_boundary(state)

    def test_continue_requires_a_valid_context_pack(self):
        review = example("live-coding-review.json")
        for pack in [None, {}, []]:
            with self.subTest(pack=pack), self.assertRaises(ValueError):
                generate_boundary({"review": review, "context_pack": pack})

    def test_invalid_reviews_and_drifting_handoffs_are_rejected(self):
        review = example("live-coding-review.json")
        pack = example("live-coding-context-pack.json")
        invalid_review = copy.deepcopy(review)
        invalid_review["evidence_tier"] = "t0"
        with self.assertRaises(ValueError):
            generate_boundary({"review": invalid_review, "context_pack": pack})
        for field, value in [("review_id", "another-review"), ("execution_boundary", dict(pack["execution_boundary"], may_do=["Change database schema."]))]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                generate_boundary({"review": review, "context_pack": dict(pack, **{field: value})})

    def test_continue_preserves_review_scope_and_all_controls(self):
        review = example("live-coding-review.json")
        state = {"review": review, "context_pack": example("live-coding-context-pack.json"), "files": ["unreviewed.py"]}
        original = copy.deepcopy(state)
        boundary = generate_boundary(state)
        self.assertEqual("continue", boundary["verdict"])
        self.assertEqual(review["review_id"], boundary["review_id"])
        for field, value in review["execution_boundary"].items():
            self.assertEqual(value, boundary[field])
        for field in ["stop_conditions", "human_approval_gates", "high_risk_actions"]:
            self.assertEqual(review[field], boundary[field])
        self.assertNotIn("unreviewed.py", json.dumps(boundary))
        boundary["may_do"].append("Mutate the returned list.")
        self.assertEqual(original, state)

    def test_verify_and_stop_preserve_their_reviewed_boundaries(self):
        for name, field in [("standard-gate-review.json", "proof_step"), ("stop-reframe-review.json", "reframed_question")]:
            review = example(name)
            with self.subTest(name=name):
                boundary = generate_boundary({"review": review, "files": ["app.py"]})
                self.assertEqual(review["combined_verdict"], boundary["verdict"])
                self.assertEqual(review[field], boundary[field])
                for key, value in review["execution_boundary"].items():
                    self.assertEqual(value, boundary[key])
                self.assertNotIn("app.py", json.dumps(boundary))

    def test_repository_and_installed_cli_never_bypass_review(self):
        for base in [ROOT, ROOT / "skills/product-design-harness/resources"]:
            with self.subTest(base=base):
                result = subprocess.run([sys.executable, str(base / "scripts/jev_gate.py"), "route", "Fix typo in README"], capture_output=True, text=True)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertFalse(json.loads(result.stdout)["bypass"])
                self.assertTrue(json.loads(result.stdout)["review_required"])

    def test_repository_and_installed_cli_enforce_canonical_handoff(self):
        valid = {"review": example("live-coding-review.json"), "context_pack": example("live-coding-context-pack.json")}
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory) / "task.json"
            for base in [ROOT, ROOT / "skills/product-design-harness/resources"]:
                for state, expected in [({"evidence_tier": "t1", "files": ["app.py"]}, 1), (valid, 0)]:
                    with self.subTest(base=base, expected=expected):
                        task.write_text(json.dumps(state))
                        result = subprocess.run([sys.executable, str(base / "scripts/jev_gate.py"), "boundary", "--task", str(task)], capture_output=True, text=True)
                        self.assertEqual(expected, result.returncode, result.stderr)
                        if expected:
                            self.assertEqual("", result.stdout)
                            self.assertIn("review", result.stderr.lower())
                            self.assertNotIn("Traceback", result.stderr)
                        else:
                            self.assertEqual(valid["review"]["execution_boundary"]["may_do"], json.loads(result.stdout)["may_do"])


if __name__ == "__main__":
    unittest.main()
