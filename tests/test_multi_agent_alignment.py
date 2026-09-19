"""Test suite for Autonomous Multi-Agent Product Alignment and Jev System One Gate."""
import json
import unittest
from pathlib import Path

from scripts.jev_gate import (
    classify_route_baseline,
    evaluate_three_lanes_baseline,
    generate_boundary,
)


class MultiAgentAlignmentTests(unittest.TestCase):
    def test_routine_maintenance_bypasses_review_with_zero_stall(self):
        prompts = [
            "Fix typo in README documentation",
            "Update CSS button padding and colors",
            "Lint code and fix formatting errors",
            "Cleanup comments and remove dead code",
        ]
        for p in prompts:
            with self.subTest(prompt=p):
                route = classify_route_baseline(p)
                self.assertEqual("routine", route)

    def test_high_risk_actions_trigger_commitment_route(self):
        prompts = [
            "Drop table users and recreate schema",
            "Add webhook to export user telemetry",
            "Implement payment and billing checkout",
            "Alter table contracts migration",
        ]
        for p in prompts:
            with self.subTest(prompt=p):
                route = classify_route_baseline(p)
                self.assertEqual("commitment", route)

    def test_pilot_twin3_sdk_telemetry_webhook_blocked_by_evidence_flow(self):
        task_state = {
            "prompt": "Add automated webhook to post telemetry to remote endpoint",
            "evidence_tier": "t0",
            "files": ["tools/jev/router.py"],
        }
        res = evaluate_three_lanes_baseline(task_state)
        self.assertEqual("stop_reframe", res["combined_verdict"])
        self.assertEqual("evidence_flow", res["weakest_flow"])

        boundary = generate_boundary(task_state)
        self.assertEqual("stop_reframe", boundary["verdict"])
        self.assertTrue(any("evidence" in c.lower() for c in boundary["must_not_do"]))

    def test_pilot_xagent_id_monolith_boundary_locks_database(self):
        task_state = {
            "prompt": "Extend enterprise agent auth endpoint in server.py",
            "evidence_tier": "t2",
            "files": ["server.py"],
        }
        res = evaluate_three_lanes_baseline(task_state)
        self.assertEqual("continue", res["combined_verdict"])

        boundary = generate_boundary(task_state)
        self.assertIn("Implement changes inside server.py", boundary["may_do"])
        self.assertTrue(any("database schema" in c.lower() for c in boundary["must_not_do"]))

    def test_pilot_xhuman_id_privacy_contract_respected(self):
        task_state = {
            "prompt": "Upload user card media to cloud storage and sync",
            "evidence_tier": "t0",
            "files": ["xhuman_id_agent_contract.json", "apps/web/card.tsx"],
        }
        res = evaluate_three_lanes_baseline(task_state)
        self.assertEqual("stop_reframe", res["combined_verdict"])

        boundary = generate_boundary(task_state)
        self.assertEqual("stop_reframe", boundary["verdict"])


if __name__ == "__main__":
    unittest.main()
