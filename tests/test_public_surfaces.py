import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stderr
from html import unescape
from pathlib import Path
from unittest.mock import patch

from scripts import validate
from scripts.serve import UTF8HTTPRequestHandler


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_VALIDATOR_SURFACES = [
    "README.md",
    "skills/product-design-harness/SKILL.md",
    "llms.txt",
    "docs/ADOPTION.md",
    "docs/LIVE-CODING.md",
    "docs/CONTRACTS.md",
    "index.html",
]


class PublicSurfaceTests(unittest.TestCase):
    def test_decision_kernel_is_consistent_across_public_surfaces(self):
        required_terms = [
            "UX3 Decision Kernel",
            "Validate",
            "Reduce",
            "Gate",
            "Emit",
        ]
        for relative_path in [
            "README.md",
            "index.html",
            "docs/UX3.md",
            "assets/ux3-model.svg",
            "skills/product-design-harness/SKILL.md",
            "llms.txt",
        ]:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            for term in required_terms:
                self.assertIn(term, text, f"{relative_path}: {term}")

    def test_hero_animation_never_hides_first_paint(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for animation in ["fadeUp", "stampIn"]:
            keyframes = re.search(
                rf"@keyframes {animation}\s*\{{(?P<body>.*?)\}}\s*\}}",
                html,
                re.DOTALL,
            )
            self.assertIsNotNone(keyframes, animation)
            self.assertNotIn("opacity: 0", keyframes.group("body"), animation)
            self.assertNotIn("scale(1.5)", keyframes.group("body"), animation)

    def test_mobile_header_uses_the_compact_brand(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="product-name"', html)
        self.assertIn("@media (max-width: 560px)", html)
        self.assertIn(".topbar .product-name { display: none; }", html)

    def test_site_uses_the_official_ux3_logo_only_in_the_header(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertTrue((ROOT / "assets/ux3-logo.jpeg").is_file())
        self.assertEqual(1, html.count('src="assets/ux3-logo.jpeg"'))
        self.assertNotIn('class="hero-logo', html)
        self.assertNotIn('aria-label="UX3 mark"', html)
        self.assertNotIn('<svg class="ux3logo"', html)
        self.assertNotIn('<svg class="hero-logo"', html)

    def test_header_logo_blends_with_light_and_dark_backgrounds(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("mix-blend-mode: multiply", html)
        self.assertIn("mix-blend-mode: screen", html)

    def test_homepage_exposes_canonical_social_and_audience_metadata(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        canonical = "https://cis2042.github.io/ux3-product-design-harness/"
        self.assertIn(f'<link rel="canonical" href="{canonical}">', html)
        self.assertIn('<meta property="og:type" content="website">', html)
        self.assertIn(f'<meta property="og:url" content="{canonical}">', html)
        self.assertIn('<meta property="og:title"', html)
        self.assertIn('<meta property="og:description"', html)
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', html)
        self.assertIn('<meta name="audience" content="Product designers, product builders, founders, and AI agents">', html)

    def test_visible_faq_matches_machine_structured_answers(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        scripts = re.findall(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            html,
            re.DOTALL,
        )
        self.assertEqual(1, len(scripts))
        graph = json.loads(scripts[0])["@graph"]
        graph_types = {node["@type"] for node in graph}
        self.assertEqual(
            {"WebSite", "SoftwareSourceCode", "FAQPage"},
            graph_types,
        )
        faq_node = next(node for node in graph if node["@type"] == "FAQPage")
        structured = [
            (item["name"], item["acceptedAnswer"]["text"])
            for item in faq_node["mainEntity"]
        ]
        visible_matches = re.findall(
            r'<details class="faq-item">\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>',
            html,
            re.DOTALL,
        )
        visible = [
            (
                unescape(re.sub(r"<[^>]+>", "", question)).strip(),
                unescape(re.sub(r"<[^>]+>", "", answer)).strip(),
            )
            for question, answer in visible_matches
        ]
        self.assertEqual(10, len(visible))
        self.assertEqual(visible, structured)

    def test_homepage_explains_agentic_design_and_designer_in_the_loop(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        hero_start = html.index('<div class="hero-head">')
        hero_end = html.index('</section>', hero_start)
        hero = html[hero_start:hero_end]
        self.assertIn("Agentic Design Process", hero)
        self.assertIn("Designer-in-the-Loop", hero)
        self.assertIn("AI agents now join product design", hero)
        self.assertIn("designers own taste, trade-offs, and accountable judgment", hero)
        self.assertIn("Agentic design needs a human judgment loop.", html)

    def test_machine_discovery_artifacts_are_parseable_and_honest(self):
        for relative_path in [
            "robots.txt",
            "sitemap.xml",
            "answers.md",
            "llms-full.txt",
            ".well-known/agent-card.json",
            ".well-known/skill-manifest.json",
        ]:
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("User-agent: *", robots)
        self.assertIn("Allow: /", robots)
        self.assertIn(
            "Sitemap: https://cis2042.github.io/ux3-product-design-harness/sitemap.xml",
            robots,
        )

        sitemap = ET.parse(ROOT / "sitemap.xml")
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = {
            node.text for node in sitemap.findall("sm:url/sm:loc", namespace)
        }
        self.assertIn(
            "https://cis2042.github.io/ux3-product-design-harness/", locations
        )
        self.assertIn(
            "https://cis2042.github.io/ux3-product-design-harness/llms.txt", locations
        )

        card = json.loads(
            (ROOT / ".well-known/agent-card.json").read_text(encoding="utf-8")
        )
        manifest = json.loads(
            (ROOT / ".well-known/skill-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual("skill_manifest", card["manifestType"])
        self.assertEqual("skill_manifest", manifest["manifestType"])
        self.assertEqual("installable_skill", card["interface"]["type"])
        self.assertEqual("installable_skill", manifest["interface"]["type"])
        self.assertIsNone(card["interface"]["remoteEndpoint"])
        self.assertIsNone(manifest["interface"]["remoteEndpoint"])
        self.assertIn("npx skills add", card["interface"]["installCommand"])
        self.assertIn("skills/product-design-harness/SKILL.md", manifest["interface"]["entryPoint"])
        self.assertFalse(card["claims"]["a2aEndpoint"])
        self.assertFalse(manifest["claims"]["a2aEndpoint"])

        answers = (ROOT / "answers.md").read_text(encoding="utf-8")
        full_context = (ROOT / "llms-full.txt").read_text(encoding="utf-8")
        self.assertEqual(10, answers.count("## "))
        self.assertIn("## Limitations", full_context)
        self.assertIn("does not guarantee ranking", full_context)
        self.assertIn("Agentic Design Process", full_context)
        self.assertIn("Designer-in-the-Loop", full_context)

        concise_context = (ROOT / "llms.txt").read_text(encoding="utf-8")
        self.assertIn("answers.md", concise_context)
        self.assertIn("llms-full.txt", concise_context)
        self.assertIn("Agentic Design Process", concise_context)
        self.assertIn("Designer-in-the-Loop", concise_context)
        self.assertIn(".well-known/skill-manifest.json", concise_context)

        self.assertTrue(card["capabilities"]["agenticDesignProcess"])
        self.assertTrue(card["capabilities"]["designerInTheLoop"])

    def test_repository_validator_accepts_binary_visual_assets(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_homepage_has_clear_human_and_agent_entrances(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('<div class="eyebrow">For Humans</div>', html)
        self.assertIn('<div class="eyebrow">For Agents</div>', html)
        self.assertIn("Read the philosophy", html)
        self.assertIn("Install for agent", html)
        self.assertNotIn("Read the contract", html)

    def test_agent_entrance_exposes_copyable_public_install_command(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        public_command = (
            "npx skills add cis2042/ux3-product-design-harness -g -y"
        )
        self.assertGreaterEqual(html.count(public_command), 2)
        self.assertIn('class="install-command"', html)
        self.assertIn('class="cli-terminal"', html)
        self.assertIn('class="cli-titlebar"', html)
        self.assertIn('class="cli-prompt" aria-hidden="true">$</span>', html)
        self.assertIn('aria-label="Agent CLI installer"', html)
        self.assertIn('data-copy-install="public"', html)
        self.assertIn('aria-label="Copy public agent install command"', html)
        self.assertIn("btn.dataset.defaultLabel", html)
        self.assertIn('markDone(btn, "unavailable")', html)
        self.assertIn("Public install", html)

    def test_public_install_surfaces_do_not_offer_an_ssh_install_url(self):
        surfaces = [
            ROOT / "README.md",
            ROOT / "index.html",
            *(ROOT / "i18n").glob("*/README.md"),
        ]
        for path in surfaces:
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertNotIn(
                    "git@github.com:cis2042/ux3-product-design-harness.git",
                    path.read_text(encoding="utf-8"),
                )
                self.assertNotIn(
                    "Private repository",
                    path.read_text(encoding="utf-8"),
                )

    def test_human_and_agent_entrances_have_distinct_surface_treatments(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn(".door.human {", html)
        self.assertIn(".door.machine {", html)
        self.assertIn(".machine-console {", html)
        self.assertRegex(html, r'class="[^"]*door-panel[^"]*human[^"]*"')
        self.assertRegex(html, r'class="[^"]*door-panel[^"]*machine[^"]*"')

    def test_topbar_has_a_distinct_github_repository_icon(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="github-icon"', html)
        self.assertIn(
            'aria-label="Open cis2042/ux3-product-design-harness on GitHub"', html
        )
        self.assertIn('title="Open repository on GitHub"', html)

    def test_homepage_local_links_and_anchors_resolve(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        ids = set(re.findall(r'\bid="([^"]+)"', html))
        findings = []
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            path_part, _, anchor = href.partition("#")
            target = ROOT / (path_part or "index.html")
            if not target.is_file():
                findings.append(f"missing file: {href}")
            elif anchor and path_part:
                target_text = target.read_text(encoding="utf-8")
                if not re.search(rf'\bid="{re.escape(anchor)}"', target_text):
                    findings.append(f"missing anchor: {href}")
            elif anchor and anchor not in ids:
                findings.append(f"missing anchor: {href}")
        self.assertEqual([], findings)

    def test_homepage_exposes_agent_documentation_and_working_languages(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        nav_match = re.search(
            r'<nav class="language-nav" aria-label="Agent documentation language">(?P<body>.*?)</nav>',
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(nav_match)
        nav_body = nav_match.group("body")
        manifest = json.loads(
            (ROOT / "i18n" / "locales.json").read_text(encoding="utf-8")
        )
        hrefs = re.findall(r'href="([^"]+)"', nav_body)
        expected_hrefs = [
            "README.md" if locale["code"] == "en" else f'i18n/{locale["code"]}/README.md'
            for locale in manifest["locales"]
        ]
        self.assertEqual(expected_hrefs, hrefs)
        self.assertIn(">Agent documentation</", html)
        self.assertIn(">Agent working language</", html)
        self.assertIn("Copy one invocation into the agent session.", html)
        for locale_code in ["en", "zh-TW", "zh-CN", "ja", "ko", "es", "fr", "de", "pt"]:
            self.assertIn(f"Working language: {locale_code}.", html)
        self.assertIn('href="docs/LIVE-CODING.md"', html)
        self.assertIn("Live coding workflow", html)

    def test_homepage_source_order_keeps_primary_doors_before_entry_rails(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        hero_head = html.find('<div class="hero-head">')
        doors = html.find('<div class="doors">')
        entry_rails = html.find('<div class="entry-rails"')
        self.assertNotEqual(-1, hero_head)
        self.assertNotEqual(-1, doors)
        self.assertNotEqual(-1, entry_rails)
        self.assertLess(hero_head, doors)
        self.assertLess(doors, entry_rails)

    def test_agent_controls_are_not_inside_human_reading_surface(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        hero = html[html.index('<section class="hero">'):html.index("<!-- ================= FOR HUMANS")]
        human = html[html.index('<div class="human-zone">'):html.index("<!-- ================= FOR AGENTS")]
        machine = html[html.index('<div class="machine-zone">'):]
        self.assertNotIn('class="entry-rails"', hero)
        self.assertNotIn('class="entry-rails"', human)
        self.assertNotIn("Working language:", human)
        self.assertIn('class="entry-rails"', machine)
        self.assertIn("Working language:", machine)
        self.assertLess(machine.index('id="for-agents"'), machine.index('class="entry-rails"'))

    def test_preview_server_declares_utf8_for_markdown(self):
        handler = UTF8HTTPRequestHandler.__new__(UTF8HTTPRequestHandler)
        content_type = handler.guess_type("i18n/zh-TW/README.md")
        self.assertEqual("text/markdown; charset=utf-8", content_type)

    def test_homepage_flow_definitions_match_canonical_ontology(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        ontology = json.loads(
            (ROOT / "knowledge" / "ontology.json").read_text(encoding="utf-8")
        )
        flow_blocks = re.findall(
            r'<div class="flow"(?: data-definition="(?P<data>[^"]*)")?><b>(?P<name>[^<]+)</b><span>(?P<text>.*?)</span></div>',
            html,
            re.DOTALL,
        )
        self.assertEqual(3, len(flow_blocks))
        by_name = {
            name: {"data_definition": data, "text": text}
            for data, name, text in flow_blocks
        }
        for flow in ontology["flows"]:
            self.assertIn(flow["name"], by_name)
            rendered = by_name[flow["name"]]
            self.assertTrue(
                flow["definition"] in rendered["text"]
                or flow["definition"] == rendered["data_definition"]
            )

    def test_working_language_controls_preserve_locale_code_case_and_valid_semantics(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        work_chip_css = re.search(
            r"\.work-chip\s*\{(?P<body>.*?)\}",
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(work_chip_css)
        self.assertNotIn("text-transform: uppercase;", work_chip_css.group("body"))
        work_tools_match = re.search(
            r'<div class="work-tools"(?P<attrs>[^>]*)aria-label="Working language invocations"',
            html,
        )
        self.assertIsNotNone(work_tools_match)
        self.assertNotIn('role="list"', work_tools_match.group("attrs"))

    def test_site_install_verify_uses_fresh_macos_venv_commands(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        required_commands = [
            "python3 -m venv .venv",
            ".venv/bin/python -m pip install -r requirements-dev.txt",
            ".venv/bin/python -m unittest discover -s tests",
            ".venv/bin/python scripts/validate.py",
            ".venv/bin/python scripts/check_review.py examples/quick-gate-review.json",
        ]
        for command in required_commands:
            self.assertIn(command, html)
        forbidden_line_patterns = [
            r"(?m)^pip install -r requirements-dev\.txt\b",
            r"(?m)^python -m unittest discover -s tests\b",
            r"(?m)^python scripts/validate\.py\b",
            r"(?m)^python scripts/check_review\.py examples/quick-gate-review\.json\b",
        ]
        for pattern in forbidden_line_patterns:
            self.assertNotRegex(html, pattern)

    def test_site_repository_map_and_examples_table_are_current(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        schema_count = len(list((ROOT / "schemas").glob("*.json")))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertEqual(18, schema_count)
        self.assertIn(f"({schema_count} JSON Schema contracts)", html)
        self.assertIn(f"one of {schema_count} schemas", readme)
        self.assertNotIn("(twelve JSON Schema contracts)", html)
        self.assertIn("examples/live-coding-product-brief.json", html)
        self.assertIn("examples/live-coding-review.json", html)
        self.assertIn("examples/live-coding-context-pack.json", html)
        self.assertIn("examples/red-team-review.json", html)

    def test_readme_exposes_distilled_rule_inventory(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("21 decision rule cards", readme)
        self.assertIn("six newly distilled cards carry chapter-level provenance", readme)
        self.assertIn("docs/DECISION-RULES.md", readme)
        self.assertIn("knowledge/source-chapters.json", readme)
        self.assertIn("ux3.rule.human_agent_interaction", readme)
        self.assertIn("ux3.rule.motivation_ethics", readme)

    def test_public_surfaces_name_actor_boundary_target_population_as_canonical(self):
        for relative_path in [
            "README.md",
            "index.html",
            "llms.txt",
            "docs/CONTRACTS.md",
            "docs/LIVE-CODING.md",
        ]:
            with self.subTest(relative_path=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn("actor_boundary.target_population", text)

        live_coding = (ROOT / "docs" / "LIVE-CODING.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn(
            "target_population, product_organization",
            live_coding,
        )

    def test_release_manifest_excludes_internal_superpowers_artifacts(self):
        completed = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        forbidden = [
            path
            for path in completed.stdout.splitlines()
            if path.startswith((".superpowers/", "docs/superpowers/"))
        ]
        self.assertEqual([], forbidden)

    def test_public_surfaces_require_check_review_as_canonical_validator(self):
        required_phrase = "scripts/check_review.py"
        for relative_path in PUBLIC_VALIDATOR_SURFACES:
            with self.subTest(relative_path=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(required_phrase, text)

    def test_ci_runs_check_review_on_golden_review_outputs(self):
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        for relative_path in [
            "examples/quick-gate-review.json",
            "examples/standard-gate-review.json",
            "examples/ux3-council-review.json",
            "examples/live-coding-review.json",
        ]:
            with self.subTest(relative_path=relative_path):
                self.assertIn(
                    f"python scripts/check_review.py {relative_path}",
                    workflow,
                )

    def test_public_release_security_baseline_is_explicit(self):
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        requirements = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
        self.assertTrue((ROOT / "SECURITY.md").is_file())
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn(
            "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5",
            workflow,
        )
        self.assertIn(
            "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
            workflow,
        )
        self.assertNotRegex(workflow, r"uses:\s+actions/[^@]+@v\d+")
        self.assertEqual("jsonschema==4.26.0\n", requirements)

    def test_public_surfaces_do_not_claim_weakest_flow_is_schema_only(self):
        forbidden_patterns = [
            r"schema[- ]only.{0,120}weakest[-_ ]flow",
            r"weakest[-_ ]flow.{0,120}schema[- ]only",
            r"schema-level.{0,120}weakest[-_ ]flow",
            r"weakest[-_ ]flow.{0,120}schema-level",
        ]
        for relative_path in PUBLIC_VALIDATOR_SURFACES:
            text = (ROOT / relative_path).read_text(encoding="utf-8").lower()
            for pattern in forbidden_patterns:
                with self.subTest(relative_path=relative_path, pattern=pattern):
                    self.assertNotRegex(text, pattern)

    def test_working_language_runtime_has_selected_state_without_clipboard_dependency(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="work-feedback mono" aria-live="polite"', html)
        self.assertIn('workFeedback.textContent = "Selected: " + displayText;', html)
        self.assertIn('workFeedback.textContent = "Copied: Working language: " + code + ".";', html)
        self.assertIn('var displayText = text.replace(/\\s+/g, " ").trim();', html)
        self.assertNotIn('workFeedback.innerHTML =', html)
        work_chip_section = re.search(
            r'var workFeedback = document\.querySelector\("\.work-feedback"\);(?P<body>.*?)\}\);\n\}\)\(\);',
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(work_chip_section)
        body = work_chip_section.group("body")
        self.assertNotIn("fallbackCopy(text)", body)

    def test_validator_scopes_utf8_to_i18n_metadata(self):
        self.assertTrue(validate.is_ascii_exempt_path(ROOT / "i18n" / "locales.json"))
        self.assertFalse(
            validate.is_ascii_exempt_path(
                ROOT / "schemas" / "session-config.schema.json"
            )
        )
        manifest = json.loads(
            (ROOT / "i18n" / "locales.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            "\u7e41\u9ad4\u4e2d\u6587", manifest["locales"][1]["native_label"]
        )

    def test_ascii_validator_ignores_sdd_scratch_but_checks_design_docs(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            scratch = root / ".superpowers" / "sdd" / "reviewer-report.md"
            scratch.parent.mkdir(parents=True)
            scratch.write_text("review: \u9700\u8981\u4fee\u6b63", encoding="utf-8")

            with patch.object(validate, "ROOT", root):
                with redirect_stderr(io.StringIO()):
                    try:
                        validate.validate_ascii_policy()
                    except SystemExit:
                        self.fail(".superpowers scratch artifact was validated")

                design_doc = root / "docs" / "superpowers" / "plan.md"
                design_doc.parent.mkdir(parents=True)
                design_doc.write_text("plan: \u4fdd\u6301\u9a57\u8b49", encoding="utf-8")
                stderr = io.StringIO()
                with redirect_stderr(stderr), self.assertRaises(SystemExit):
                    validate.validate_ascii_policy()

            self.assertIn("docs/superpowers/plan.md", stderr.getvalue())

    def test_repository_path_checks_skip_superpowers_design_docs(self):
        self.assertTrue(
            validate.should_check_repository_paths(ROOT / "docs" / "UX3.md")
        )
        self.assertTrue(
            validate.should_check_repository_paths(
                ROOT / ".github" / "workflows" / "release-notes.md"
            )
        )
        self.assertFalse(
            validate.should_check_repository_paths(
                ROOT
                / "docs"
                / "superpowers"
                / "plans"
                / "2026-07-10-ux3-knowledge-multilingual-live-coding.md"
            )
        )
        self.assertFalse(
            validate.should_check_repository_paths(
                ROOT / ".superpowers" / "sdd" / "task-1-brief.md"
            )
        )

    def test_repository_path_validator_skips_canonical_rule_ids(self):
        self.assertFalse(
            validate.should_check_bare_reference(
                "ux3.rule.human_agent_interaction"
            )
        )
        self.assertTrue(validate.should_check_bare_reference("README.md"))

    def test_released_tree_excludes_internal_superpowers_docs(self):
        self.assertFalse((ROOT / "docs" / "superpowers").exists())

    def test_skill_loads_kernel_language_and_start_review_in_order(self):
        skill = (ROOT / "skills" / "product-design-harness" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        expected_order = [
            "schemas/session-config.schema.json",
            "knowledge/ontology.json",
            "knowledge/rules.json",
            "prompts/start-review.md",
        ]
        positions = [skill.find(term) for term in expected_order]
        self.assertFalse(
            any(position == -1 for position in positions),
            "installed skill must name session config, ontology, rules, and start-review",
        )
        self.assertEqual(positions, sorted(positions))
        self.assertIn("working_language", skill)
        self.assertIn("canonical_identifiers", skill)
        self.assertIn("canonical UX3 knowledge kernel", skill)

    def test_skill_names_new_distilled_rule_triggers(self):
        skill = (ROOT / "skills" / "product-design-harness" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        expected_rule_ids = [
            "ux3.rule.mental_model_alignment",
            "ux3.rule.human_factors_load",
            "ux3.rule.research_validity",
            "ux3.rule.value_market_path",
            "ux3.rule.human_agent_interaction",
            "ux3.rule.motivation_ethics",
        ]
        for rule_id in expected_rule_ids:
            self.assertIn(rule_id, skill)
        for trigger_phrase in [
            "mental-model mismatch",
            "cognitive or recovery burden",
            "research claim",
            "value proposition, positioning, buyer, channel, or gtm path",
            "agent plan or tool action",
            "retention, personalization, or gamification",
        ]:
            self.assertIn(trigger_phrase, skill.lower())

    def test_decision_rule_docs_project_new_families_and_source_boundary(self):
        text = (ROOT / "docs" / "DECISION-RULES.md").read_text(encoding="utf-8")
        for rule_id in [
            "ux3.rule.mental_model_alignment",
            "ux3.rule.human_factors_load",
            "ux3.rule.research_validity",
            "ux3.rule.value_market_path",
            "ux3.rule.human_agent_interaction",
            "ux3.rule.motivation_ethics",
        ]:
            self.assertIn(rule_id, text)
        self.assertIn(
            "Operationalization is narrower than the source curriculum",
            text,
        )
        self.assertIn("UX3 chapter", text)

    def test_skill_blocks_live_coding_until_continue_context_pack(self):
        surfaces = {
            "skills/product-design-harness/SKILL.md": (
                ROOT / "skills" / "product-design-harness" / "SKILL.md"
            ).read_text(encoding="utf-8"),
            "prompts/start-review.md": (ROOT / "prompts/start-review.md").read_text(
                encoding="utf-8"
            ),
            "prompts/gate-review.md": (ROOT / "prompts/gate-review.md").read_text(
                encoding="utf-8"
            ),
            "docs/ORCHESTRATION.md": (ROOT / "docs/ORCHESTRATION.md").read_text(
                encoding="utf-8"
            ),
            "docs/OPERATING-PROTOCOL.md": (
                ROOT / "docs/OPERATING-PROTOCOL.md"
            ).read_text(encoding="utf-8"),
        }
        for relative_path, text in surfaces.items():
            self.assertIn(
                "verify authorizes only the exact proof_step",
                text,
                relative_path,
            )
            self.assertIn(
                "continue plus a valid context pack authorizes implementation",
                text,
                relative_path,
            )
            self.assertIn("Reversibility lowers mode", text, relative_path)
            self.assertIn("may_do", text, relative_path)
            self.assertIn("must_not_do", text, relative_path)
            self.assertIn("must_ask", text, relative_path)

    def test_reviewers_reference_kernel_language_flows_and_coding_boundary(self):
        for relative_path, reviewer, flow in [
            ("agents/user-flow-reviewer.md", "user_flow", "User Flow"),
            ("agents/evidence-flow-reviewer.md", "evidence_flow", "Evidence Flow"),
            ("agents/business-flow-reviewer.md", "business_flow", "Business Flow"),
        ]:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("knowledge/ontology.json", text, relative_path)
            self.assertIn("knowledge/rules.json", text, relative_path)
            self.assertIn("working_language", text, relative_path)
            self.assertIn(flow, text, relative_path)
            self.assertIn(
                "schemas/reviewer-verdict.schema.json", text, relative_path
            )
            self.assertIn(f"reviewer: {reviewer}", text, relative_path)
            self.assertIn(
                "verify authorizes only the exact proof_step",
                text,
                relative_path,
            )

    def test_pressure_scenarios_record_observed_baseline_failure(self):
        text = (ROOT / "tests" / "skill-pressure-scenarios.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("5/5 agents", text)
        self.assertIn("called the direction unvalidated", text)
        self.assertIn("started coding because it was reversible", text)
        self.assertIn("do not fabricate post-skill evidence", text)

    def test_pressure_scenarios_have_machine_readable_outcome_markers(self):
        text = (ROOT / "tests" / "skill-pressure-scenarios.md").read_text(
            encoding="utf-8"
        )
        markers = {
            "pressure.baseline.general_implementation_started=5/5",
            "pressure.post_skill.general_implementation_refused=5/5",
            "pressure.post_skill.verdict_split.verify=4",
            "pressure.post_skill.verdict_split.stop_reframe=1",
            (
                "pressure.post_skill.bounded_prototype_policy="
                "exact_proof_step_only_not_general_implementation"
            ),
        }
        for marker in markers:
            self.assertIn(marker, text)

    def test_pressure_scenarios_cover_new_distilled_rule_failures(self):
        text = (ROOT / "tests" / "skill-pressure-scenarios.md").read_text(
            encoding="utf-8"
        )
        scenario_markers = {
            "pressure.scenario.mental_model_hidden_autonomy",
            "pressure.scenario.research_synthetic_as_validation",
            "pressure.scenario.agent_action_without_recovery",
            "pressure.scenario.retention_manipulation",
        }
        for marker in scenario_markers:
            self.assertIn(marker, text)
        self.assertIn("Scenario definitions are not observed compliance evidence", text)

    def test_pressure_scenarios_record_fresh_distilled_rule_evidence(self):
        text = (ROOT / "tests" / "skill-pressure-scenarios.md").read_text(
            encoding="utf-8"
        )
        markers = {
            "pressure.distilled.total_general_implementation_refused=3/3",
            "pressure.distilled.mental_model_hidden_autonomy=stop_reframe",
            "pressure.distilled.agent_action_without_recovery=verify",
            "pressure.distilled.retention_manipulation=stop_reframe",
            "pressure.distilled.expanded_general_implementation_refused=6/6",
            "pressure.distilled.research_synthetic_as_validation=verify",
            "pressure.distilled.human_factors_interruption=stop_reframe",
            "pressure.distilled.value_market_path_missing=verify",
            "pressure.distilled.negative_control_continue=1/1",
        }
        for marker in markers:
            self.assertIn(marker, text)

    def test_distilled_pressure_cases_are_machine_readable_and_cover_rules(self):
        pressure_record = json.loads(
            (ROOT / "tests" / "distilled-pressure-cases.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn("observation_limitations", pressure_record)
        cases = pressure_record["cases"]
        expected_scenarios = {
            "mental_model_hidden_autonomy",
            "agent_action_without_recovery",
            "research_synthetic_as_validation",
            "human_factors_interruption",
            "value_market_path_missing",
            "retention_manipulation",
            "distilled_rules_negative_control",
        }
        distilled_rules = {
            "ux3.rule.mental_model_alignment",
            "ux3.rule.human_factors_load",
            "ux3.rule.research_validity",
            "ux3.rule.value_market_path",
            "ux3.rule.human_agent_interaction",
            "ux3.rule.motivation_ethics",
        }
        self.assertEqual(expected_scenarios, {case["scenario_id"] for case in cases})
        covered_rules = set()
        run_ids = set()
        for case in cases:
            with self.subTest(scenario_id=case["scenario_id"]):
                required = set(case["expected_required_rule_ids"])
                forbidden = set(case["forbidden_rule_ids"])
                observed = case["observed"]
                run_ids.add(observed["run_id"])
                self.assertRegex(
                    observed["run_id"],
                    r"\A[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z",
                )
                triggered = set(observed["triggered_rule_ids"])
                covered_rules.update(required)
                self.assertTrue(required.issubset(triggered))
                self.assertTrue(forbidden.isdisjoint(triggered))
                self.assertIn(observed["verdict"], case["allowed_verdicts"])
                self.assertEqual(
                    case["general_implementation_allowed"],
                    observed["general_implementation_allowed"],
                )
        self.assertEqual(distilled_rules, covered_rules)
        self.assertEqual(len(cases), len(run_ids))
        negative = next(
            case for case in cases
            if case["scenario_id"] == "distilled_rules_negative_control"
        )
        self.assertEqual(distilled_rules, set(negative["forbidden_rule_ids"]))


if __name__ == "__main__":
    unittest.main()
