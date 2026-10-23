import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "skills/product-design-harness/resources"


def load_example(name):
    return json.loads((ROOT / "examples" / name).read_text())


class ExampleScenarioTests(unittest.TestCase):
    def test_council_input_and_result_describe_the_same_workflow(self):
        brief = load_example("ux3-council-input.json")["product_brief"]
        review = load_example("ux3-council-review.json")
        self.assertEqual(review["product_direction"], brief["product_direction"])
        self.assertEqual(review["actor_boundary"], brief["actor_boundary"])
        self.assertEqual(
            review["product_organization"]["organization"],
            brief["business_boundary"]["product_organization"],
        )
        self.assertEqual(
            set(review["evidence_receipt_ids"]),
            {receipt["evidence_id"] for receipt in brief["current_evidence"]},
        )
        self.assertEqual(
            {review["evidence_tier"]},
            {receipt["evidence_tier"] for receipt in brief["current_evidence"]},
        )

    def test_support_stop_example_does_not_inherit_report_export_actors(self):
        review = load_example("stop-reframe-review.json")
        self.assertIn("support", review["actor_boundary"]["operator"].lower())
        scenario = json.dumps({
            key: review[key]
            for key in [
                "actor_boundary", "product_organization", "stakeholder_effects",
                "human_judgment_boundary", "unresolved_assumptions",
            ]
        }).lower()
        for stale_scenario in ["reporting", "export", "scheduling"]:
            self.assertNotIn(stale_scenario, scenario)
        self.assertEqual(
            review["human_approval_gates"],
            review["human_judgment_boundary"]["approval_gates"],
        )

    def test_quick_markdown_uses_the_validated_json_evidence_tier(self):
        review = load_example("quick-gate-review.json")
        markdown = (ROOT / "examples/quick-gate-review.md").read_text()
        tier = re.search(r"\| Evidence tier \| (t[0-4]) \|", markdown).group(1)
        self.assertEqual(review["evidence_tier"], tier)
        self.assertIn(f'`{review["combined_verdict"]}`', markdown)

    def test_installed_live_coding_command_validates_the_joint_handoff(self):
        markdown = (RESOURCES / "docs/LIVE-CODING.md").read_text()
        commands = [
            line for block in re.findall(r"```text\n(.*?)```", markdown, re.DOTALL)
            for line in block.splitlines()
            if "scripts/check_review.py examples/live-coding-review.json" in line
        ]
        self.assertEqual(1, len(commands))
        command = shlex.split(commands[0])
        self.assertIn("--context-pack", command)
        with tempfile.TemporaryDirectory() as directory:
            installed = Path(directory) / "resources"
            shutil.copytree(RESOURCES, installed)
            self.assertFalse((installed / "tests").exists())
            self.assertFalse((installed / "scripts/validate.py").exists())
            result = subprocess.run(
                [sys.executable, "-B", *command[1:]],
                cwd=installed, capture_output=True, text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)

    def test_installed_handbook_images_resolve_without_the_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            installed = Path(directory) / "resources"
            shutil.copytree(RESOURCES, installed)
            handbook = installed / "docs/HARNESS.md"
            images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", handbook.read_text())
            self.assertEqual(2, len(images))
            for image in images:
                with self.subTest(image=image):
                    target = handbook.parent / image
                    self.assertTrue(target.is_file(), image)
                    ET.parse(target)
                    self.assertEqual(
                        (ROOT / "assets" / target.name).read_bytes(), target.read_bytes()
                    )


if __name__ == "__main__":
    unittest.main()
