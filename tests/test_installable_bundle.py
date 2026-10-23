import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "skills" / "product-design-harness"
RESOURCES = BUNDLE / "resources"

RUNTIME_DIRECTORIES = [
    "agents",
    "docs",
    "examples",
    "knowledge",
    "prompts",
    "schemas",
    "templates",
]


class InstallableBundleTests(unittest.TestCase):
    def test_bundle_contains_the_skill_and_runtime_dependencies(self):
        required_files = [
            "SKILL.md",
            "LICENSE",
            "resources/requirements-dev.txt",
            "resources/scripts/check_review.py",
            "resources/schemas/review-result.schema.json",
            "resources/knowledge/ontology.json",
            "resources/knowledge/rules.json",
            "resources/prompts/start-review.md",
            "resources/templates/product-brief.md",
            "resources/examples/quick-gate-review.json",
        ]
        missing = [path for path in required_files if not (BUNDLE / path).is_file()]
        self.assertEqual([], missing)

        skill = (BUNDLE / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("resources/schemas/session-config.schema.json", skill)
        self.assertIn("resources/scripts/check_review.py", skill)
        self.assertEqual((ROOT / "LICENSE").read_bytes(), (BUNDLE / "LICENSE").read_bytes())

    def test_bundle_resources_match_the_canonical_runtime(self):
        for directory in RUNTIME_DIRECTORIES:
            canonical_files = sorted(
                path for path in (ROOT / directory).rglob("*") if path.is_file()
            )
            self.assertGreater(len(canonical_files), 0, directory)
            for canonical_path in canonical_files:
                relative_path = canonical_path.relative_to(ROOT)
                bundled_path = RESOURCES / relative_path
                with self.subTest(path=str(relative_path)):
                    self.assertTrue(bundled_path.is_file())
                    self.assertEqual(
                        canonical_path.read_bytes(), bundled_path.read_bytes()
                    )

        self.assertEqual(
            (ROOT / "requirements-dev.txt").read_bytes(),
            (RESOURCES / "requirements-dev.txt").read_bytes(),
        )
        bundled_scripts = sorted((RESOURCES / "scripts").glob("*.py"))
        self.assertTrue(bundled_scripts)
        for bundled_script in bundled_scripts:
            with self.subTest(script=bundled_script.name):
                self.assertEqual(
                    (ROOT / "scripts" / bundled_script.name).read_bytes(),
                    bundled_script.read_bytes(),
                )

    def test_schema_ids_use_the_published_pages_urls(self):
        published_base = "https://cis2042.github.io/ux3-product-design-harness/schemas/"
        for schema_path in sorted((ROOT / "schemas").glob("*.schema.json")):
            with self.subTest(schema=schema_path.name):
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                self.assertEqual(published_base + schema_path.name, schema["$id"])

    def test_machine_discovery_uses_publishable_skill_manifest(self):
        self.assertTrue((ROOT / ".nojekyll").is_file())
        manifest_path = ROOT / ".well-known" / "skill-manifest.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual("skill_manifest", manifest["manifestType"])
        self.assertFalse(manifest["claims"]["a2aEndpoint"])

        llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
        self.assertIn(".well-known/skill-manifest.json", llms)
        self.assertIn("skills/product-design-harness/SKILL.md", llms)


if __name__ == "__main__":
    unittest.main()
