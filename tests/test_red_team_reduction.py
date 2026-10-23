import copy
import json
import unittest
from pathlib import Path

from scripts.check_review import check


ROOT = Path(__file__).resolve().parents[1]


class RedTeamReductionTests(unittest.TestCase):
    def test_counter_case_changes_the_affected_final_lane_before_reduction(self):
        review = json.loads((ROOT / "examples/ux3-council-review.json").read_text())
        review["evidence_tier"] = "t2"
        for lane in review["reviews"].values():
            lane["verdict"] = "continue"
            lane["evidence_tier"] = "t2"

        self.assertTrue(check(review))

        accepted = copy.deepcopy(review)
        accepted["reviews"]["evidence"]["verdict"] = "verify"
        accepted["reviews"]["evidence"]["missing_evidence"] = (
            "Red-team counter-case: supervised recovery has not been observed."
        )
        self.assertEqual([], check(accepted))
        self.assertEqual(review["council_record"], accepted["council_record"])


if __name__ == "__main__":
    unittest.main()
