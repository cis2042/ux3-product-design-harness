import json
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_RULES = {
    "ux3.rule.actor_boundary",
    "ux3.rule.problem_hypothesis",
    "ux3.rule.behavior_subjective_separation",
    "ux3.rule.disconfirm_first",
    "ux3.rule.evidence_separation",
    "ux3.rule.evidence_sized_action",
    "ux3.rule.minimum_authority",
    "ux3.rule.high_risk_action_bundle",
    "ux3.rule.minimum_validated_proof",
    "ux3.rule.feedback_classification",
    "ux3.rule.false_product_market_fit",
    "ux3.rule.whole_ownership_cost",
    "ux3.rule.depth_accumulation",
    "ux3.rule.failure_to_rule_learning",
    "ux3.rule.human_judgment",
    "ux3.rule.mental_model_alignment",
    "ux3.rule.human_factors_load",
    "ux3.rule.research_validity",
    "ux3.rule.value_market_path",
    "ux3.rule.human_agent_interaction",
    "ux3.rule.motivation_ethics",
}
NEW_RULE_SOURCE_CHAPTERS = {
    "ux3.rule.mental_model_alignment": {"0-2", "1-3", "2-3"},
    "ux3.rule.human_factors_load": {"1-7", "2-3", "3-8"},
    "ux3.rule.research_validity": {"1-8", "2-9", "3-7", "3-8"},
    "ux3.rule.value_market_path": {"1-5", "1-9", "2-2", "3-1", "3-2"},
    "ux3.rule.human_agent_interaction": {"2-3", "2-4", "2-6", "3-3", "3-4"},
    "ux3.rule.motivation_ethics": {"3-5", "3-6"},
}
NEW_RULE_TOKEN_PROBES = {
    "ux3.rule.mental_model_alignment": {
        "mental model", "conceptual model", "expectation", "prediction",
        "mental_model_record",
    },
    "ux3.rule.human_factors_load": {
        "task", "tool", "environment", "attention", "memory", "recovery",
        "human_factors_review",
    },
    "ux3.rule.research_validity": {
        "research question", "method", "sample", "attitude", "behavior",
        "simulation", "research_validity_record",
    },
    "ux3.rule.value_market_path": {
        "target actor", "alternative", "willingness", "channel", "retention",
        "value_market_path_record",
    },
    "ux3.rule.human_agent_interaction": {
        "intent", "plan", "interrupt", "correct", "undo", "approve", "log",
        "interaction_contract",
    },
    "ux3.rule.motivation_ethics": {
        "intrinsic", "extrinsic", "vulnerable", "manipulation", "exit",
        "motivation_ethics_review",
    },
}
REQUIRED_README_MARKERS = [
    "locale-selector",
    "where-it-sits",
    "why-install",
    "ux3-model",
    "review-modes",
    "live-coding-quickstart",
    "working-language",
    "canonical-contracts",
]
PUBLIC_SKILL_INSTALL_COMMAND = (
    "npx skills add cis2042/ux3-product-design-harness -g -y"
)
REQUIRED_README_TOKENS = [
    "User Flow",
    "Evidence Flow",
    "Business Flow",
    "UX3 Decision Kernel",
    "user_evidence",
    "evidence_business",
    "user_business",
    "ux3_decision_kernel",
    "Quick Gate",
    "Standard Gate",
    "UX3 Council",
    "working_language",
    "canonical_identifiers",
    "fallback_language",
    "continue",
    "verify",
    "stop_reframe",
    "ux3.rule.actor_boundary",
    "schemas/session-config.schema.json",
    "schemas/review-result.schema.json",
    "knowledge/ontology.json",
    "knowledge/rules.json",
    "prompts/start-review.md",
    "templates/context-pack.md",
    "docs/HARNESS.md",
]
NON_ENGLISH_LOCALES = ["zh-TW", "zh-CN", "ja", "ko", "es", "fr", "de", "pt"]
PUBLIC_ENTRY_FILES = [
    "README.md",
    "docs/ADOPTION.md",
    "docs/LIVE-CODING.md",
    "llms.txt",
]
PUBLIC_QUICKSTART_COMMANDS = [
    "python3 -m venv .venv",
    ".venv/bin/python -m pip install -r requirements-dev.txt",
    ".venv/bin/python -m unittest discover -s tests",
    ".venv/bin/python scripts/validate.py",
    ".venv/bin/python scripts/check_review.py examples/quick-gate-review.json",
    ".venv/bin/python scripts/serve.py",
]
NATIVE_PHRASE_PROBES = {
    "zh-TW": [
        "\u516d\u500b gates \u662f Stage\u3001User Flow\u3001Evidence Flow\u3001Business Flow\u3001Council\u3001Human Judgment",
    ],
    "zh-CN": [
        "\u516d\u4e2a gates \u662f Stage\u3001User Flow\u3001Evidence Flow\u3001Business Flow\u3001Council\u3001Human Judgment",
    ],
    "ja": [
        "\u516d\u3064\u306e gate \u306f Stage\u3001User Flow\u3001Evidence Flow\u3001Business Flow\u3001Council\u3001Human Judgment",
        "`stop_reframe` \u306f\u5b9f\u88c5\u3092\u6b62\u3081\u3001\u3088\u308a\u3088\u3044\u30d7\u30ed\u30c0\u30af\u30c8\u554f\u3044\u3092\u8fd4\u3059\u304b\u8981\u6c42\u3057\u307e\u3059\u3002",
    ],
    "ko": [
        "\uc5ec\uc12f gate \ub294 Stage, User Flow, Evidence Flow, Business Flow, Council, Human Judgment",
    ],
    "es": [
        "juicio de producto verificable por m\xe1quina",
        "avanza desde la especificaci\xf3n, la construcci\xf3n, el lanzamiento, las pruebas con usuarios y el an\xe1lisis de comentarios",
        "Las seis puertas son Stage, User Flow, Evidence Flow, Business Flow, Council y Human Judgment",
        "fuente, se\xf1al, interpretaci\xf3n, se\xf1al contraria e impacto en la decisi\xf3n",
        "puntuaciones de los carriles",
        "gestiona la incertidumbre",
    ],
    "fr": [
        "jugement produit v\xe9rifiable par machine",
        "progresse de la sp\xe9cification \xe0 la construction, au lancement, aux tests utilisateurs et \xe0 l'analyse des retours",
        "Les six portes sont Stage, User Flow, Evidence Flow, Business Flow, Council et Human Judgment",
        "source, signal, interpr\xe9tation, signal contraire et impact sur la d\xe9cision",
        "scores de voie",
        "encadre l'incertitude",
    ],
    "de": [
        "maschinenpr\xfcfbare Produktbeurteilung",
        "von der Spezifikation \xfcber die Umsetzung, die Einf\xfchrung, Nutzertests und die Auswertung von R\xfcckmeldungen",
        "Die sechs Gates sind Stage, User Flow, Evidence Flow, Business Flow, Council und Human Judgment",
        "Quelle, Signal, Interpretation, Gegensignal und Entscheidungswirkung",
        "Spurwertungen",
        "steuert Unsicherheit",
    ],
    "pt": [
        "Julgamento de produto verific\xe1vel por m\xe1quina",
        "Os seis gates s\xe3o Stage, User Flow, Evidence Flow, Business Flow, Council e Human Judgment",
    ],
}
FORBIDDEN_LOCALIZATION_PHRASES = {
    "es": [
        "Juicio de producto verificable por maquina",
        "spec, build, launch, user testing",
        "feedback digestion",
        "devuelve un verdict",
        "Tres flow",
        "Que source, signal, interpretation, counter-signal y decision impact",
        "promedia lane score",
        "controla uncertainty",
        "review no es implementation",
        "implementation dentro del execution boundary",
    ],
    "fr": [
        "jugement produit verifiable par machine",
        "spec, build, launch, user testing",
        "feedback digestion",
        "retourne un verdict",
        "Trois flow",
        "Quelle source, signal, interpretation, counter-signal et decision impact",
        "moyenne pas les lane score",
        "gate uncertainty",
        "review n'est pas implementation",
        "implementation dans le execution boundary",
    ],
    "de": [
        "Maschinenpruefbare Produktentscheidung",
        "spec, build, launch, user testing",
        "feedback digestion",
        "verdict zurueck",
        "Drei flow",
        "Welche source, signal, interpretation, counter-signal und decision impact",
        "lane score",
        "gate uncertainty",
        "review ist nicht implementation",
        "implementation innerhalb des execution boundary",
    ],
}


def load_json(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def manifest_locales():
    return load_json("i18n/locales.json")["locales"]


def readme_path_for_locale(locale_code):
    if locale_code == "en":
        return ROOT / "README.md"
    return ROOT / "i18n" / locale_code / "README.md"


def public_entry_paths():
    paths = [ROOT / path for path in PUBLIC_ENTRY_FILES]
    paths.extend(readme_path_for_locale(locale["code"]) for locale in manifest_locales())
    return sorted(set(paths))


def markdown_link_targets(readme_path, text):
    targets = set()
    for raw_target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = raw_target.split("#", 1)[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        targets.add((readme_path.parent / target).resolve())
    return targets


def markdown_heading_anchors(text):
    anchors = set()
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*$", text, re.MULTILINE):
        anchor = heading.lower().strip()
        anchor = re.sub(r"[`*_~]", "", anchor)
        anchor = re.sub(r"[^\w\-\s\u0080-\uffff]", "", anchor)
        anchor = re.sub(r"\s+", "-", anchor)
        anchor = re.sub(r"-+", "-", anchor).strip("-")
        anchors.add(anchor)
    return anchors


def fenced_code_blocks(text):
    return re.findall(r"```[^\n]*\n(.*?)\n```", text, re.DOTALL)


def squash_whitespace(text):
    return re.sub(r"\s+", " ", text)


def marked_section(text, marker, next_marker=None):
    start = text.index(f"<!-- {marker} -->")
    end = text.index(f"<!-- {next_marker} -->", start) if next_marker else len(text)
    return text[start:end]


class KnowledgeAndLocaleContractTests(unittest.TestCase):
    def test_supported_locales_are_exact(self):
        manifest = load_json("i18n/locales.json")
        self.assertEqual(
            {"en", "zh-TW", "zh-CN", "ja", "ko", "es", "fr", "de", "pt"},
            {item["code"] for item in manifest["locales"]},
        )
        self.assertEqual(9, len(manifest["locales"]))

    def test_each_locale_has_a_readme(self):
        for locale in manifest_locales():
            with self.subTest(locale=locale["code"]):
                self.assertTrue(readme_path_for_locale(locale["code"]).is_file())

    def test_readmes_include_stable_section_markers(self):
        for locale in manifest_locales():
            readme_path = readme_path_for_locale(locale["code"])
            if not readme_path.is_file():
                with self.subTest(locale=locale["code"]):
                    self.fail(f"Missing README for locale {locale['code']}")
                continue
            text = readme_path.read_text(encoding="utf-8")
            for marker in REQUIRED_README_MARKERS:
                with self.subTest(locale=locale["code"], marker=marker):
                    self.assertIn(f"<!-- {marker} -->", text)

    def test_readmes_are_content_complete_against_english_section_contract(self):
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        english_markers = re.findall(r"<!-- ([a-z0-9-]+) -->", english)
        self.assertEqual(REQUIRED_README_MARKERS, english_markers)
        for locale in manifest_locales():
            text = readme_path_for_locale(locale["code"]).read_text(encoding="utf-8")
            markers = re.findall(r"<!-- ([a-z0-9-]+) -->", text)
            with self.subTest(locale=locale["code"]):
                self.assertEqual(english_markers, markers)
                self.assertEqual(
                    marked_section(english, "why-install", "ux3-model").count("\n|"),
                    marked_section(text, "why-install", "ux3-model").count("\n|"),
                )
                self.assertEqual(
                    marked_section(english, "canonical-contracts").count("\n|"),
                    marked_section(text, "canonical-contracts").count("\n|"),
                )
                self.assertIn("assets/product-design-harness-cover.svg", text)
                self.assertIn("assets/process-comparison.svg", text)
                self.assertIn("knowledge/source-chapters.json", text)
                self.assertIn("docs/DECISION-RULES.md", text)

    def test_readmes_expose_the_public_agent_install_command(self):
        for locale in manifest_locales():
            text = readme_path_for_locale(locale["code"]).read_text(encoding="utf-8")
            with self.subTest(locale=locale["code"]):
                self.assertIn(PUBLIC_SKILL_INSTALL_COMMAND, text)

    def test_all_relative_readme_links_and_anchors_resolve(self):
        findings = []
        for locale in manifest_locales():
            readme_path = readme_path_for_locale(locale["code"])
            text = readme_path.read_text(encoding="utf-8")
            for raw_target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if raw_target.startswith(("http://", "https://", "mailto:")):
                    continue
                path_part, _, anchor = raw_target.partition("#")
                target = (readme_path.parent / (path_part or readme_path.name)).resolve()
                if not target.is_file():
                    findings.append(
                        f"{readme_path.relative_to(ROOT)} -> missing {raw_target}"
                    )
                    continue
                if anchor and target.suffix.lower() == ".md":
                    target_text = target.read_text(encoding="utf-8")
                    if anchor not in markdown_heading_anchors(target_text):
                        findings.append(
                            f"{readme_path.relative_to(ROOT)} -> missing anchor {raw_target}"
                        )
        self.assertEqual([], findings)

    def test_all_markdown_page_links_resolve(self):
        findings = []
        for markdown_path in sorted(ROOT.rglob("*.md")):
            relative_path = markdown_path.relative_to(ROOT)
            if any(part.startswith(".") for part in relative_path.parts):
                continue
            if relative_path.parts[:3] == (
                "skills",
                "product-design-harness",
                "resources",
            ):
                continue
            text = markdown_path.read_text(encoding="utf-8")
            for raw_target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if raw_target.startswith(("http://", "https://", "mailto:")):
                    continue
                path_part, _, anchor = raw_target.partition("#")
                target = (markdown_path.parent / (path_part or markdown_path.name)).resolve()
                if not target.is_file():
                    findings.append(
                        f"{markdown_path.relative_to(ROOT)} -> missing {raw_target}"
                    )
                    continue
                if anchor and target.suffix.lower() == ".md":
                    if anchor not in markdown_heading_anchors(
                        target.read_text(encoding="utf-8")
                    ):
                        findings.append(
                            f"{markdown_path.relative_to(ROOT)} -> missing anchor {raw_target}"
                        )
        self.assertEqual([], findings)

    def test_readmes_have_reciprocal_locale_links(self):
        locale_codes = [locale["code"] for locale in manifest_locales()]
        expected_paths = {
            code: readme_path_for_locale(code).resolve() for code in locale_codes
        }

        for locale in manifest_locales():
            readme_path = readme_path_for_locale(locale["code"])
            if not readme_path.is_file():
                with self.subTest(locale=locale["code"]):
                    self.fail(f"Missing README for locale {locale['code']}")
                continue
            targets = markdown_link_targets(
                readme_path, readme_path.read_text(encoding="utf-8")
            )
            linked_locales = {
                code for code, expected_path in expected_paths.items()
                if expected_path in targets
            }
            with self.subTest(locale=locale["code"]):
                self.assertEqual(set(locale_codes), linked_locales)

    def test_readmes_include_copyable_working_language_invocation(self):
        for locale in manifest_locales():
            readme_path = readme_path_for_locale(locale["code"])
            if not readme_path.is_file():
                with self.subTest(locale=locale["code"]):
                    self.fail(f"Missing README for locale {locale['code']}")
                continue
            text = readme_path.read_text(encoding="utf-8")
            with self.subTest(locale=locale["code"]):
                self.assertIn(f"Working language: {locale['code']}.", text)

    def test_working_language_invocation_is_inside_fenced_code_block(self):
        for locale in manifest_locales():
            readme_path = readme_path_for_locale(locale["code"])
            text = readme_path.read_text(encoding="utf-8")
            invocation = f"Working language: {locale['code']}."
            with self.subTest(locale=locale["code"]):
                self.assertTrue(
                    any(invocation in block for block in fenced_code_blocks(text))
                )

    def test_localized_readmes_include_native_phrase_probes(self):
        for locale_code, probes in NATIVE_PHRASE_PROBES.items():
            text = squash_whitespace(
                readme_path_for_locale(locale_code).read_text(encoding="utf-8")
            )
            for phrase in probes:
                with self.subTest(locale=locale_code, phrase=phrase):
                    self.assertIn(squash_whitespace(phrase), text)

    def test_es_fr_de_reject_known_machine_like_mixed_phrases(self):
        for locale_code, forbidden_phrases in FORBIDDEN_LOCALIZATION_PHRASES.items():
            text = squash_whitespace(
                readme_path_for_locale(locale_code).read_text(encoding="utf-8")
            )
            for phrase in forbidden_phrases:
                with self.subTest(locale=locale_code, phrase=phrase):
                    self.assertNotIn(squash_whitespace(phrase), text)

    def test_non_english_readmes_name_all_six_gates(self):
        gate_terms = [
            "Stage",
            "User Flow",
            "Evidence Flow",
            "Business Flow",
            "Council",
            "Human Judgment",
        ]
        for locale_code in NON_ENGLISH_LOCALES:
            text = readme_path_for_locale(locale_code).read_text(encoding="utf-8")
            for gate_term in gate_terms:
                with self.subTest(locale=locale_code, gate=gate_term):
                    self.assertIn(gate_term, text)

    def test_readmes_preserve_canonical_machine_tokens(self):
        for locale in manifest_locales():
            readme_path = readme_path_for_locale(locale["code"])
            if not readme_path.is_file():
                with self.subTest(locale=locale["code"]):
                    self.fail(f"Missing README for locale {locale['code']}")
                continue
            text = readme_path.read_text(encoding="utf-8")
            for token in REQUIRED_README_TOKENS:
                with self.subTest(locale=locale["code"], token=token):
                    self.assertIn(token, text)

    def test_readme_quickstarts_use_fresh_macos_venv_commands(self):
        for locale in manifest_locales():
            readme_path = readme_path_for_locale(locale["code"])
            text = readme_path.read_text(encoding="utf-8")
            for command in PUBLIC_QUICKSTART_COMMANDS:
                with self.subTest(locale=locale["code"], command=command):
                    self.assertIn(command, text)

    def test_public_entry_files_reject_bare_python_and_pip_commands(self):
        banned = [
            re.compile(r"(?<!-m )\bpip install\b"),
            re.compile(r"(?<!/)\bpython -m unittest\b"),
            re.compile(r"(?<!/)\bpython scripts/"),
        ]
        findings = []
        for path in public_entry_paths():
            for line_number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if any(pattern.search(line) for pattern in banned):
                    findings.append(f"{path.relative_to(ROOT)}:{line_number}: {line}")
        self.assertEqual([], findings)

    def test_llms_verify_commands_are_list_items(self):
        text = (ROOT / "llms.txt").read_text(encoding="utf-8")
        in_verify_section = False
        findings = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line == "Verify locally (CI runs the full suite on every push):":
                in_verify_section = True
                continue
            if in_verify_section and line == "Operating rules:":
                break
            if not in_verify_section:
                continue
            stripped = line.strip()
            if stripped and not stripped.startswith("- "):
                findings.append(f"llms.txt:{line_number}: {line}")
        self.assertEqual([], findings)

    def test_session_config_accepts_supported_working_language(self):
        validator = Draft202012Validator(
            load_json("schemas/session-config.schema.json")
        )
        self.assertTrue(
            validator.is_valid(
                {
                    "working_language": "ja",
                    "canonical_identifiers": "en",
                    "fallback_language": "en",
                }
            )
        )

    def test_session_config_rejects_unknown_locale(self):
        validator = Draft202012Validator(
            load_json("schemas/session-config.schema.json")
        )
        self.assertFalse(
            validator.is_valid(
                {
                    "working_language": "xx",
                    "canonical_identifiers": "en",
                    "fallback_language": "en",
                }
            )
        )

    def test_session_config_requires_english_canonical_fields(self):
        validator = Draft202012Validator(
            load_json("schemas/session-config.schema.json")
        )
        self.assertFalse(
            validator.is_valid(
                {
                    "working_language": "es",
                    "canonical_identifiers": "es",
                    "fallback_language": "en",
                }
            )
        )
        self.assertFalse(
            validator.is_valid(
                {
                    "working_language": "es",
                    "canonical_identifiers": "en",
                    "fallback_language": "es",
                }
            )
        )

    def test_decision_rule_schema_accepts_complete_rule_contract(self):
        validator = Draft202012Validator(
            load_json("schemas/decision-rule.schema.json")
        )
        self.assertTrue(
            validator.is_valid(
                {
                    "rule_id": "ux3.rule.example",
                    "title": "Example",
                    "flow": "cross_flow",
                    "strength": "conditional",
                    "trigger": ["observable condition"],
                    "must_inspect": ["required input"],
                    "must_do": ["required behavior"],
                    "must_not_do": ["forbidden behavior"],
                    "evidence_required": ["decision-changing evidence"],
                    "counter_signal": ["possible disconfirmation"],
                    "human_boundary": ["human-owned decision"],
                    "stop_condition": ["stop or reframe condition"],
                    "output_requirement": ["machine-readable output"],
                    "source": ["UX3 handbook concept"],
                }
            )
        )

    def test_decision_rule_schema_requires_all_contract_fields(self):
        validator = Draft202012Validator(
            load_json("schemas/decision-rule.schema.json")
        )
        self.assertFalse(
            validator.is_valid(
                {
                    "rule_id": "ux3.rule.example",
                    "title": "Example",
                    "flow": "cross_flow",
                    "strength": "conditional",
                    "trigger": ["observable condition"],
                    "must_inspect": ["required input"],
                    "must_do": ["required behavior"],
                    "must_not_do": ["forbidden behavior"],
                    "evidence_required": ["decision-changing evidence"],
                    "counter_signal": ["possible disconfirmation"],
                    "human_boundary": ["human-owned decision"],
                    "stop_condition": ["stop or reframe condition"],
                    "source": ["UX3 handbook concept"],
                }
            )
        )

    def test_ontology_defines_canonical_ux3_flows_and_intersections(self):
        ontology = load_json("knowledge/ontology.json")

        self.assertEqual(
            {"user_flow", "evidence_flow", "business_flow"},
            {item["id"] for item in ontology["flows"]},
        )
        self.assertEqual(
            {
                "user_evidence",
                "evidence_business",
                "user_business",
                "ux3_decision_kernel",
            },
            {item["id"] for item in ontology["intersections"]},
        )

    def test_ontology_defines_actor_stakeholder_and_judgment_terms(self):
        ontology = load_json("knowledge/ontology.json")

        self.assertTrue(
            {
                "primary_user",
                "secondary_user",
                "machine_actor",
                "beneficiary",
                "affected_person",
                "excluded_group",
            }.issubset({item["id"] for item in ontology["actor_roles"]})
        )
        self.assertTrue(
            {
                "company",
                "project_owner",
                "issuer",
                "customer",
                "buyer",
                "employee_operator",
                "partner_channel",
                "investor_funder",
                "platform_provider",
                "regulator",
                "externality_bearer",
            }.issubset({item["id"] for item in ontology["stakeholder_roles"]})
        )
        self.assertTrue(
            {
                "human_taste",
                "human_judgment",
                "accountable_input",
            }.issubset({item["id"] for item in ontology["human_judgment_terms"]})
        )

    def test_evidence_flow_keeps_human_judgment_separate(self):
        ontology = load_json("knowledge/ontology.json")
        evidence_flow = next(
            item for item in ontology["flows"] if item["id"] == "evidence_flow"
        )
        evidence_terms = " ".join(
            f'{item["id"]} {item["definition"]}'
            for item in ontology["evidence_terms"]
        ).lower()

        self.assertEqual(
            "Evidence Flow is the product sensing, learning, and calibration "
            "system joining internal and external data, behavior, subjective "
            "experience, interpretation, counter-signals, evaluations, and "
            "action traces; evidence informs decisions, while taste is recorded "
            "separately as an accountable human decision input.",
            evidence_flow["definition"],
        )
        self.assertNotRegex(evidence_terms, r"\b(?:taste|judgment)\b")
        self.assertIn("human_judgment_terms", ontology)
        self.assertTrue(
            {"human_taste", "human_judgment", "accountable_input"}.issubset(
                {item["id"] for item in ontology["human_judgment_terms"]}
            )
        )

    def test_glossary_keeps_human_judgment_outside_evidence_flow(self):
        text = (ROOT / "docs" / "GLOSSARY.md").read_text(encoding="utf-8")
        evidence_flow_line = next(
            line for line in text.splitlines() if line.startswith("| Evidence Flow |")
        )

        self.assertNotIn(
            "decision impact, and human judgment", evidence_flow_line.lower()
        )
        self.assertIn(
            "human judgment is recorded separately as accountable input",
            evidence_flow_line.lower(),
        )
        self.assertIn("| Human judgment |", text)

    def test_ontology_validates_against_canonical_schema(self):
        validator = Draft202012Validator(load_json("schemas/ontology.schema.json"))
        errors = sorted(
            validator.iter_errors(load_json("knowledge/ontology.json")), key=str
        )

        self.assertEqual([], errors)

    def test_ontology_schema_rejects_unexpected_stable_fields(self):
        schema = load_json("schemas/ontology.schema.json")
        ontology = load_json("knowledge/ontology.json")
        ontology["flows"][0]["unexpected"] = "not stable"

        self.assertFalse(Draft202012Validator(schema).is_valid(ontology))

    def test_ux3_docs_keep_human_judgment_outside_evidence_sources(self):
        text = (ROOT / "docs" / "UX3.md").read_text(encoding="utf-8")

        self.assertNotIn("| Human judgment |", text)
        self.assertNotIn("human-owned", text)
        self.assertIn("Human taste and judgment are separately recorded", text)

    def test_rules_file_contains_exact_required_rule_ids(self):
        rules = load_json("knowledge/rules.json")

        self.assertEqual(REQUIRED_RULES, {item["rule_id"] for item in rules["rules"]})
        self.assertEqual(21, len(rules["rules"]))

    def test_new_distilled_rules_trace_to_original_ux3_chapters(self):
        rules_by_id = {
            item["rule_id"]: item for item in load_json("knowledge/rules.json")["rules"]
        }

        for rule_id, chapter_ids in NEW_RULE_SOURCE_CHAPTERS.items():
            with self.subTest(rule_id=rule_id):
                self.assertIn(rule_id, rules_by_id)
                if rule_id not in rules_by_id:
                    continue
                source_text = " ".join(rules_by_id[rule_id]["source"])
                for chapter_id in chapter_ids:
                    self.assertIn(f"UX3 chapter {chapter_id}", source_text)

    def test_distilled_rule_sources_resolve_through_checked_in_manifest(self):
        manifest = load_json("knowledge/source-chapters.json")
        self.assertEqual(
            "fabf929c6fe03b67edfd25be8b79991da5056578c7a7fabbd3b709b4a88f50d2",
            manifest["source_sha256"],
        )
        self.assertEqual(
            {
                "schema_version",
                "corpus_id",
                "source_document",
                "source_sha256",
                "source_note",
                "chapters",
            },
            set(manifest),
        )
        chapter_ids = {item["chapter_id"] for item in manifest["chapters"]}
        expected_chapter_ids = set().union(*NEW_RULE_SOURCE_CHAPTERS.values())
        self.assertEqual(expected_chapter_ids, chapter_ids)
        self.assertEqual(len(chapter_ids), len(manifest["chapters"]))

        rules_by_id = {
            item["rule_id"]: item for item in load_json("knowledge/rules.json")["rules"]
        }
        for rule_id in NEW_RULE_SOURCE_CHAPTERS:
            source_text = " ".join(rules_by_id[rule_id]["source"])
            cited = set(re.findall(r"UX3 chapter (\d-\d+)", source_text))
            with self.subTest(rule_id=rule_id):
                self.assertEqual(NEW_RULE_SOURCE_CHAPTERS[rule_id], cited)
                self.assertTrue(cited.issubset(chapter_ids))

    def test_new_distilled_rules_include_family_specific_operational_language(self):
        rules_by_id = {
            item["rule_id"]: item for item in load_json("knowledge/rules.json")["rules"]
        }
        operational_fields = [
            "trigger",
            "must_inspect",
            "must_do",
            "must_not_do",
            "evidence_required",
            "counter_signal",
            "human_boundary",
            "stop_condition",
            "output_requirement",
        ]

        for rule_id, probes in NEW_RULE_TOKEN_PROBES.items():
            with self.subTest(rule_id=rule_id):
                self.assertIn(rule_id, rules_by_id)
                if rule_id not in rules_by_id:
                    continue
                rule_text = " ".join(
                    value
                    for field in operational_fields
                    for value in rules_by_id[rule_id][field]
                ).lower()
                for probe in probes:
                    self.assertIn(probe, rule_text)

    def test_new_distilled_rules_are_conditional_not_always_on(self):
        rules_by_id = {
            item["rule_id"]: item for item in load_json("knowledge/rules.json")["rules"]
        }
        for rule_id in NEW_RULE_SOURCE_CHAPTERS:
            with self.subTest(rule_id=rule_id):
                self.assertEqual("conditional", rules_by_id[rule_id]["strength"])

    def test_human_factors_trigger_requires_material_risk(self):
        rules_by_id = {
            item["rule_id"]: item for item in load_json("knowledge/rules.json")["rules"]
        }
        trigger = " ".join(
            rules_by_id["ux3.rule.human_factors_load"]["trigger"]
        ).lower()
        self.assertIn("material", trigger)
        self.assertNotIn("multi-step", trigger)

    def test_value_market_path_is_distinct_from_false_pmf(self):
        rules_by_id = {
            item["rule_id"]: item for item in load_json("knowledge/rules.json")["rules"]
        }
        self.assertIn("ux3.rule.value_market_path", rules_by_id)
        self.assertIn("ux3.rule.false_product_market_fit", rules_by_id)
        self.assertNotIn("ux3.rule.value_market_fit", rules_by_id)
        value_rule_text = " ".join(
            value
            for field in ["trigger", "must_do", "must_not_do", "output_requirement"]
            for value in rules_by_id["ux3.rule.value_market_path"][field]
        ).lower()
        self.assertIn("pre-fit", value_rule_text)
        self.assertIn("false_product_market_fit", value_rule_text)
        self.assertIn("value_market_path_record", value_rule_text)

    def test_human_agent_interaction_composes_canonical_risk_records(self):
        rules_by_id = {
            item["rule_id"]: item for item in load_json("knowledge/rules.json")["rules"]
        }
        interaction = rules_by_id["ux3.rule.human_agent_interaction"]
        composition_text = " ".join(
            interaction["must_do"]
            + interaction["must_not_do"]
            + interaction["output_requirement"]
        ).lower()
        self.assertIn("authority_boundary_ref", composition_text)
        self.assertIn("high_risk_action_bundle_ref", composition_text)
        self.assertIn("do not duplicate", composition_text)

        output_text = " ".join(interaction["output_requirement"]).lower()
        self.assertIn("recovery_surface", output_text)
        self.assertNotIn("recovery_path", output_text)

    def test_research_validity_composes_canonical_evidence_records(self):
        rules_by_id = {
            item["rule_id"]: item for item in load_json("knowledge/rules.json")["rules"]
        }
        research = rules_by_id["ux3.rule.research_validity"]
        composition_text = " ".join(
            research["must_do"]
            + research["must_not_do"]
            + research["output_requirement"]
        ).lower()
        for reference in [
            "evidence_receipt_ids",
            "behavior_signal_refs",
            "subjective_signal_refs",
            "counter_signal_refs",
            "decision_impact_ref",
        ]:
            self.assertIn(reference, composition_text)
        self.assertIn("do not duplicate", composition_text)
        output_text = " ".join(research["output_requirement"]).lower()
        self.assertNotIn("attitude_signal,", output_text)
        self.assertNotIn("behavior_signal,", output_text)

    def test_rules_validate_against_decision_rule_schema(self):
        schema_validator = Draft202012Validator(
            load_json("schemas/decision-rule.schema.json")
        )
        rules = load_json("knowledge/rules.json")

        for rule in rules["rules"]:
            with self.subTest(rule_id=rule["rule_id"]):
                errors = sorted(schema_validator.iter_errors(rule), key=str)
                self.assertEqual([], errors)
                self.assertTrue(rule["trigger"])
                self.assertTrue(rule["evidence_required"])
                self.assertTrue(rule["counter_signal"])
                self.assertTrue(rule["human_boundary"])
                self.assertTrue(rule["stop_condition"])
                self.assertTrue(rule["output_requirement"])


if __name__ == "__main__":
    unittest.main()
