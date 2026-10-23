import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CursorPluginTests(unittest.TestCase):
    def test_plugin_loads_the_complete_existing_skill(self):
        manifest = json.loads(
            (ROOT / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(["./skills/product-design-harness"], manifest["skills"])
        skill = ROOT / manifest["skills"][0]
        self.assertTrue((skill / "SKILL.md").is_file())
        self.assertEqual((ROOT / "LICENSE").read_bytes(), (skill / "LICENSE").read_bytes())
        for relative_path in [
            "resources/prompts/start-review.md",
            "resources/knowledge/ontology.json",
            "resources/schemas/review-result.schema.json",
            "resources/scripts/check_review.py",
            "resources/examples/quick-gate-review.json",
        ]:
            with self.subTest(path=relative_path):
                self.assertTrue((skill / relative_path).is_file())

    def test_plugin_keeps_reviewers_as_skill_resources(self):
        manifest = json.loads(
            (ROOT / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual([], manifest["agents"])
        for component in ["rules", "commands", "hooks", "mcpServers", "variables"]:
            with self.subTest(component=component):
                self.assertNotIn(component, manifest)
        self.assertFalse((ROOT / "mcp.json").exists())
        self.assertFalse((ROOT / "hooks" / "hooks.json").exists())


if __name__ == "__main__":
    unittest.main()
