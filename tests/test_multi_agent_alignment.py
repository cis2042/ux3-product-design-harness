import unittest

from scripts.jev_gate import (
    classify_route_baseline,
    evaluate_three_lanes_baseline,
    generate_boundary,
)


class MultiAgentAlignmentTests(unittest.TestCase):
    def test_routine_maintenance_is_classified_for_review_selection(self):
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

    def test_telemetry_example_stops_at_missing_evidence(self):
        task_state = {
            "prompt": "Add automated webhook to post telemetry to remote endpoint",
            "evidence_tier": "t0",
            "files": ["tools/jev/router.py"],
        }
        res = evaluate_three_lanes_baseline(task_state)
        self.assertEqual("stop_reframe", res["combined_verdict"])
        self.assertEqual("evidence_flow", res["weakest_flow"])

        with self.assertRaises(ValueError):
            generate_boundary(task_state)

    def test_auth_example_cannot_authorize_edits_from_metadata(self):
        task_state = {
            "prompt": "Extend enterprise agent auth endpoint in server.py",
            "evidence_tier": "t2",
            "files": ["server.py"],
        }
        res = evaluate_three_lanes_baseline(task_state)
        self.assertEqual("continue", res["combined_verdict"])

        with self.assertRaises(ValueError):
            generate_boundary(task_state)

    def test_media_sync_example_stops_at_missing_evidence(self):
        task_state = {
            "prompt": "Upload user card media to cloud storage and sync",
            "evidence_tier": "t0",
            "files": ["xhuman_id_agent_contract.json", "apps/web/card.tsx"],
        }
        res = evaluate_three_lanes_baseline(task_state)
        self.assertEqual("stop_reframe", res["combined_verdict"])

        with self.assertRaises(ValueError):
            generate_boundary(task_state)


if __name__ == "__main__":
    unittest.main()
