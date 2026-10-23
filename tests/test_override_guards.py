"""Regression tests for the verdict-override contract (RFC 0001).

Covers: golden pair validity, review cross-checks, expiry, and scope
laundering rejection.
"""

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_json(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def run_check(override, review, script_path="scripts/check_override.py"):
    override_path = ROOT / "tests" / "_override_probe.json"
    review_path = ROOT / "tests" / "_override_review_probe.json"
    override_path.write_text(json.dumps(override), encoding="utf-8")
    review_path.write_text(json.dumps(review), encoding="utf-8")
    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / script_path),
                str(override_path),
                str(review_path),
            ],
            capture_output=True,
            text=True,
        )
        return completed.returncode, completed.stderr
    finally:
        override_path.unlink(missing_ok=True)
        review_path.unlink(missing_ok=True)


class OverrideGuardTests(unittest.TestCase):
    def setUp(self):
        self.override = load_json("examples/verdict-override.json")
        self.review = load_json("examples/stop-reframe-review.json")

    def test_golden_pair_passes(self):
        code, err = run_check(self.override, self.review)
        self.assertEqual(0, code, err)

    def test_schema_rejects_missing_expiry(self):
        override = copy.deepcopy(self.override)
        del override["expires_at"]
        code, err = run_check(override, self.review)
        self.assertNotEqual(0, code)
        self.assertIn("schema", err)

    def test_review_id_must_match(self):
        override = copy.deepcopy(self.override)
        override["review_id"] = "some-other-review"
        code, err = run_check(override, self.review)
        self.assertNotEqual(0, code)
        self.assertIn("review_id mismatch", err)

    def test_overridden_verdict_must_match_the_review(self):
        override = copy.deepcopy(self.override)
        override["overridden_verdict"] = "verify"
        code, err = run_check(override, self.review)
        self.assertNotEqual(0, code)
        self.assertIn("combined_verdict", err)

    def test_a_continue_review_cannot_be_overridden(self):
        review = load_json("examples/quick-gate-review.json")
        override = copy.deepcopy(self.override)
        override["review_id"] = review["review_id"]
        override["acknowledged_weakest_flow"] = review["weakest_flow"]
        code, err = run_check(override, review)
        self.assertNotEqual(0, code)
        self.assertIn("needs no override", err)

    def test_weakest_flow_must_be_restated(self):
        override = copy.deepcopy(self.override)
        override["acknowledged_weakest_flow"] = "business"
        code, err = run_check(override, self.review)
        self.assertNotEqual(0, code)
        self.assertIn("weakest_flow", err)

    def test_expired_override_is_rejected(self):
        override = copy.deepcopy(self.override)
        override["expires_at"] = "2020-01-01T00:00:00Z"
        code, err = run_check(override, self.review)
        self.assertNotEqual(0, code)
        self.assertIn("expired", err)

    def test_may_do_cannot_repeat_the_reviews_must_not_do(self):
        override = copy.deepcopy(self.override)
        banned = self.review["execution_boundary"]["must_not_do"][0]
        override["authorized_scope"]["may_do"].append(banned.upper())
        code, err = run_check(override, self.review)
        self.assertNotEqual(0, code)
        self.assertIn("must_not_do", err)

    def test_prohibited_actions_reject_surrounding_whitespace(self):
        banned = self.review["execution_boundary"]["must_not_do"][0]
        for script_path in [
            "scripts/check_override.py",
            "skills/product-design-harness/resources/scripts/check_override.py",
        ]:
            for prohibited, permitted in [
                (banned, " " + banned.upper() + " "),
                ("\t" + banned + "\n", banned.upper()),
                ("\u00a0" + banned + "\u00a0", "\n" + banned.upper() + "\t"),
            ]:
                with self.subTest(script=script_path, prohibited=prohibited, permitted=permitted):
                    review = copy.deepcopy(self.review)
                    review["execution_boundary"]["must_not_do"][0] = prohibited
                    override = copy.deepcopy(self.override)
                    override["authorized_scope"]["may_do"].append(permitted)
                    code, err = run_check(override, review, script_path)
                    self.assertNotEqual(0, code)
                    self.assertIn("must_not_do", err)

    def test_distinct_authorized_actions_remain_valid_with_whitespace(self):
        override = copy.deepcopy(self.override)
        override["authorized_scope"]["may_do"] = [
            "\t" + entry + "\n" for entry in override["authorized_scope"]["may_do"]
        ]
        for script_path in [
            "scripts/check_override.py",
            "skills/product-design-harness/resources/scripts/check_override.py",
        ]:
            with self.subTest(script=script_path):
                code, err = run_check(override, self.review, script_path)
                self.assertEqual(0, code, err)


if __name__ == "__main__":
    unittest.main()
