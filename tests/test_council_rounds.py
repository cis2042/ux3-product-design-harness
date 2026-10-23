import copy
import importlib.util
import itertools
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
RUNTIMES = [ROOT, ROOT / "skills/product-design-harness/resources"]
FLOW_REVIEWERS = ["user_flow", "evidence_flow", "business_flow"]
ROUND_ARRAYS = ["independent_reviews", "challenge_reviews"]


class CouncilRoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validators = {}
        cls.checkers = {}
        for index, runtime in enumerate(RUNTIMES):
            resources = []
            for path in (runtime / "schemas").glob("*.json"):
                schema = json.loads(path.read_text())
                resource = Resource.from_contents(schema)
                resources.extend([(path.name, resource), (schema["$id"], resource)])
            cls.validators[runtime] = Draft202012Validator(
                json.loads((runtime / "schemas/council-input.schema.json").read_text()),
                registry=Registry().with_resources(resources),
            )
            spec = importlib.util.spec_from_file_location(
                f"council_checker_{index}", runtime / "scripts/check_review.py"
            )
            checker = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(checker)
            cls.checkers[runtime] = checker

    def council_input(self, runtime):
        return json.loads((runtime / "examples/ux3-council-input.json").read_text())

    def council_result(self, runtime):
        return json.loads((runtime / "examples/ux3-council-review.json").read_text())

    def test_existing_council_input_and_result_remain_valid(self):
        for runtime in RUNTIMES:
            with self.subTest(runtime=str(runtime)):
                self.assertEqual(
                    [], list(self.validators[runtime].iter_errors(self.council_input(runtime)))
                )
                self.assertEqual([], self.checkers[runtime].check(self.council_result(runtime)))

    def test_each_input_round_rejects_duplicate_lane_votes(self):
        for runtime, array_name, missing, repeated in itertools.product(
            RUNTIMES, ROUND_ARRAYS, FLOW_REVIEWERS, FLOW_REVIEWERS
        ):
            if missing == repeated:
                continue
            document = self.council_input(runtime)
            for review in document[array_name]:
                if review["reviewer"] == missing:
                    review["reviewer"] = repeated
            with self.subTest(runtime=str(runtime), round=array_name, missing=missing, repeated=repeated):
                errors = list(self.validators[runtime].iter_errors(document))
                self.assertTrue(any(list(error.path)[:1] == [array_name] for error in errors))

    def test_input_round_arrays_cannot_be_swapped(self):
        for runtime, array_name in itertools.product(RUNTIMES, ROUND_ARRAYS):
            document = self.council_input(runtime)
            other = next(name for name in ROUND_ARRAYS if name != array_name)
            document[array_name] = copy.deepcopy(document[other])
            with self.subTest(runtime=str(runtime), round=array_name):
                errors = list(self.validators[runtime].iter_errors(document))
                self.assertTrue(any("review_round" in error.path for error in errors))

    def test_input_round_rejects_one_vote_from_the_other_round(self):
        for runtime, array_name, reviewer in itertools.product(
            RUNTIMES, ROUND_ARRAYS, FLOW_REVIEWERS
        ):
            document = self.council_input(runtime)
            other = next(name for name in ROUND_ARRAYS if name != array_name)
            replacement = next(review for review in document[other] if review["reviewer"] == reviewer)
            document[array_name] = [
                copy.deepcopy(replacement) if review["reviewer"] == reviewer else review
                for review in document[array_name]
            ]
            with self.subTest(runtime=str(runtime), round=array_name, reviewer=reviewer):
                errors = list(self.validators[runtime].iter_errors(document))
                self.assertTrue(any("review_round" in error.path for error in errors))

    def test_final_round_rejects_repeated_reviewers(self):
        for runtime, reviewer in itertools.product(RUNTIMES, FLOW_REVIEWERS):
            document = self.council_result(runtime)
            objection = next(flow for flow in FLOW_REVIEWERS if flow != reviewer)
            for challenge in document["council_record"]["challenges"]:
                challenge["reviewer"] = reviewer
                challenge["objection_to"] = objection
            with self.subTest(runtime=str(runtime), reviewer=reviewer):
                errors = self.checkers[runtime].check(document)
                self.assertTrue(any("exactly one reviewer per flow" in error for error in errors))

    def test_final_round_rejects_an_extra_vote(self):
        for runtime in RUNTIMES:
            document = self.council_result(runtime)
            challenges = document["council_record"]["challenges"]
            challenges.append(copy.deepcopy(challenges[0]))
            with self.subTest(runtime=str(runtime)):
                errors = self.checkers[runtime].check(document)
                self.assertTrue(any("exactly one reviewer per flow" in error for error in errors))

    def test_lane_order_does_not_change_round_validity(self):
        for runtime in RUNTIMES:
            baseline = self.council_input(runtime)
            for array_name in ROUND_ARRAYS:
                for votes in itertools.permutations(baseline[array_name]):
                    document = copy.deepcopy(baseline)
                    document[array_name] = list(votes)
                    with self.subTest(runtime=str(runtime), round=array_name, order=[v["reviewer"] for v in votes]):
                        self.assertEqual([], list(self.validators[runtime].iter_errors(document)))
            baseline = self.council_result(runtime)
            for votes in itertools.permutations(baseline["council_record"]["challenges"]):
                document = copy.deepcopy(baseline)
                document["council_record"]["challenges"] = list(votes)
                with self.subTest(runtime=str(runtime), round="final", order=[v["reviewer"] for v in votes]):
                    self.assertEqual([], self.checkers[runtime].check(document))
