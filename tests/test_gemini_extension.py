import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.package_gemini_extension import ROOT, build_package


class GeminiExtensionTests(unittest.TestCase):
    def test_archive_preserves_the_complete_skill_without_extra_components(self):
        with tempfile.TemporaryDirectory() as temporary:
            receipt = build_package(temporary)
            archive = Path(temporary) / receipt["archive"]
            with zipfile.ZipFile(archive) as bundle:
                names = bundle.namelist()
                self.assertEqual(96, len(names))
                self.assertEqual(len(names), len(set(names)))
                skill_files = [name for name in names if name.startswith("skills/")]
                self.assertEqual(94, len(skill_files))
                self.assertEqual({"gemini-extension.json", "LICENSE"}, set(names) - set(skill_files))
                for name in names:
                    with self.subTest(path=name):
                        self.assertEqual((ROOT / name).read_bytes(), bundle.read(name))
                manifest = json.loads(bundle.read("gemini-extension.json"))
                self.assertEqual([], manifest["contextFileName"])
                self.assertEqual(
                    {"name", "version", "description", "contextFileName"}, set(manifest)
                )
                self.assertEqual(
                    bundle.read("LICENSE"),
                    bundle.read("skills/product-design-harness/LICENSE"),
                )
            self.assertEqual(
                hashlib.sha256(archive.read_bytes()).hexdigest(), receipt["archive_sha256"]
            )

    def test_archive_is_reproducible(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_receipt = build_package(first)
            second_receipt = build_package(second)
            self.assertEqual(first_receipt, second_receipt)
            self.assertEqual(
                (Path(first) / first_receipt["archive"]).read_bytes(),
                (Path(second) / second_receipt["archive"]).read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
