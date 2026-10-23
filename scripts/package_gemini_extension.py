import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_PREFIX = "skills/product-design-harness/"


def build_package(output_dir):
    manifest = json.loads((ROOT / "gemini-extension.json").read_text(encoding="utf-8"))
    if set(manifest) != {"name", "version", "description", "contextFileName"}:
        raise ValueError("The Gemini package must expose only the existing skill")
    if manifest["name"] != "ux3-product-design-harness" or manifest["version"] != "0.2.0":
        raise ValueError("Unexpected Gemini package identity or version")
    if manifest["contextFileName"] != [] or not manifest["description"]:
        raise ValueError("Global context must remain disabled")
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", SKILL_PREFIX], cwd=ROOT
    ).decode("utf-8").split("\0")
    skill_files = sorted(name for name in tracked if name)
    if len(skill_files) != 94:
        raise ValueError("Expected the complete 94-file skill")
    if (ROOT / "LICENSE").read_bytes() != (ROOT / SKILL_PREFIX / "LICENSE").read_bytes():
        raise ValueError("The original MIT licenses must match")
    entries = sorted(["gemini-extension.json", "LICENSE", *skill_files])
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"{manifest['name']}-gemini-{manifest['version']}.zip"
    file_hashes = {}
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in entries:
            source = ROOT / name
            if source.is_symlink() or not source.is_file():
                raise ValueError(f"Expected a regular source file: {name}")
            data = source.read_bytes()
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            bundle.writestr(entry, data)
            file_hashes[name] = hashlib.sha256(data).hexdigest()
    receipt = {
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "name": manifest["name"],
        "version": manifest["version"],
        "archive": archive.name,
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "skill_file_count": len(skill_files),
        "files": file_hashes,
    }
    (output_dir / "gemini-extension-provenance.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    arguments = parser.parse_args()
    print(json.dumps(build_package(arguments.output_dir), indent=2))
