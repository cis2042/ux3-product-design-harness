import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from scripts import check_review, validate


ROOT = Path(__file__).resolve().parents[1]

CANONICAL_FIELDS = {
    "schema_version",
    "session_config",
    "review_id",
    "product_direction",
    "mode",
    "stage",
    "actor_boundary",
    "product_organization",
    "stakeholder_effects",
    "human_judgment_boundary",
    "unresolved_assumptions",
    "combined_verdict",
    "weakest_flow",
    "strongest_signal",
    "riskiest_claim",
    "main_uncertainty",
    "confidence_level",
    "evidence_tier",
    "main_trade_off",
    "human_owned_decision",
    "human_decision_record_id",
    "evidence_receipt_ids",
    "reviews",
    "next_smallest_action",
    "execution_boundary",
    "human_approval_gates",
    "high_risk_actions",
    "stop_conditions",
    "context_pack_required",
}


def load_json(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def contract_validator(relative_path):
    schema = load_json(relative_path)
    resources = []
    for schema_name in [
        "session-config.schema.json",
        "evidence.schema.json",
        "actor-boundary.schema.json",
    ]:
        schema_path = ROOT / "schemas" / schema_name
        if not schema_path.exists():
            continue
        external_schema = json.loads(schema_path.read_text(encoding="utf-8"))
        resource = Resource.from_contents(external_schema)
        resources.extend(
            [
                (external_schema["$id"], resource),
                (schema_name, resource),
                (
                    f"https://cis2042.github.io/ux3-product-design-harness/schemas/{schema_name}",
                    resource,
                ),
            ]
        )
    registry = Registry().with_resources(resources)
    return Draft202012Validator(schema, registry=registry)


class HarnessContractTests(unittest.TestCase):
    def valid_product_brief(self):
        return {
            "schema_version": "2.1",
            "session_config": {
                "working_language": "en",
                "canonical_identifiers": "en",
                "fallback_language": "en",
            },
            "product_direction": "Clarify the empty-state action on the setup page.",
            "accountable_owner": "Product owner",
            "stage": "prototype",
            "actor_boundary": {
                "target_population": ["New workspace admins"],
                "operator": "Workspace admin",
                "beneficiary": "Workspace team",
                "machine_actor": "Not applicable",
                "affected_people": ["Invited team members"],
                "excluded_groups": ["Existing configured workspaces"],
            },
            "business_boundary": {
                "product_organization": "Example Product Co.",
                "project_owner": "Activation team",
                "issuer": "Example Product Co.",
                "customers": ["Workspace buyers"],
                "buyers": ["Workspace admins"],
                "operators": ["Support team"],
                "partners": ["Not applicable"],
                "funders": ["Not applicable"],
                "platforms": ["Web app"],
                "regulators": ["Not applicable"],
                "externality_bearers": ["Invited team members"],
                "decision_authority": "Product owner",
                "value_exchange": "Admins complete setup and teams reach value faster.",
            },
            "human_judgment_boundary": {
                "human_owned_decisions": ["Final copy tone"],
                "machine_supported_inputs": ["Support notes and session replays"],
                "not_mechanized": ["Taste and brand judgment"],
                "approval_gates": [self.named_human_gate()],
            },
            "unresolved_assumptions": [
                "Whether copy or missing product guidance causes the hesitation."
            ],
            "execution_boundary": {
                "may_do": ["Draft one copy-only change."],
                "must_not_do": ["Change layout, permissions, or data handling."],
                "must_ask": [
                    "A material scope, risk, data, or stakeholder impact changes."
                ],
            },
            "problem_hypothesis": (
                "New workspace admins hesitate at the empty state because the "
                "next action is unclear."
            ),
            "current_evidence": [],
            "business_goal": "Improve first-action completion.",
            "constraints": ["Copy-only change"],
            "proposed_next_step": "Release one copy variant.",
            "known_risks": ["Copy may not address the real confusion."],
        }

    def named_human_gate(self):
        return {
            "gate_id": "product-owner-release-approval",
            "accountable_owner": "Product owner",
            "condition": "Before release to users.",
        }

    def test_required_review_artifacts_exist(self):
        required = [
            "agents/registry.json",
            "docs/ANTI-PATTERNS.md",
            "docs/CLAIMS.md",
            "docs/CONTRACTS.md",
            "examples/quick-gate-review.json",
            "examples/quick-context-pack.json",
            "examples/human-decision.json",
            "examples/evidence-response.json",
            "examples/ux3-council-review.json",
            "examples/stop-reframe-review.json",
            "examples/red-team-review.json",
            "schemas/evidence-request.schema.json",
            "schemas/evidence-response.schema.json",
            "schemas/red-team-review.schema.json",
        ]
        missing = [path for path in required if not (ROOT / path).is_file()]
        self.assertEqual([], missing)

    def test_canonical_review_schema_has_one_complete_contract(self):
        schema = load_json("schemas/review-result.schema.json")
        self.assertTrue(CANONICAL_FIELDS.issubset(set(schema["required"])))
        self.assertTrue(CANONICAL_FIELDS.issubset(set(schema["properties"])))
        verdicts = schema["properties"]["combined_verdict"]["enum"]
        self.assertEqual(["continue", "verify", "stop_reframe"], verdicts)

    def test_schema_inventory_has_exact_public_contract_count(self):
        schema_paths = sorted((ROOT / "schemas").glob("*.json"))
        self.assertEqual(18, len(schema_paths))

    def test_schema_readme_inventory_matches_schema_files(self):
        readme = (ROOT / "schemas" / "README.md").read_text(encoding="utf-8")
        documented = set(re.findall(r"`([^`]+\.json)`", readme))
        actual = {path.name for path in (ROOT / "schemas").glob("*.json")}

        self.assertEqual(actual, documented)

    def test_actor_boundary_schema_is_canonical_and_reused(self):
        actor_schema_path = ROOT / "schemas" / "actor-boundary.schema.json"
        self.assertTrue(actor_schema_path.is_file())

        actor_schema = load_json("schemas/actor-boundary.schema.json")
        self.assertEqual(
            [
                "target_population",
                "operator",
                "beneficiary",
                "machine_actor",
                "affected_people",
                "excluded_groups",
            ],
            actor_schema["required"],
        )
        self.assertFalse(actor_schema["additionalProperties"])

        for relative_path in [
            "schemas/product-brief.schema.json",
            "schemas/review-result.schema.json",
            "schemas/context-pack.schema.json",
        ]:
            with self.subTest(relative_path=relative_path):
                schema = load_json(relative_path)
                self.assertIn("actor_boundary", schema["required"])
                self.assertEqual(
                    "actor-boundary.schema.json",
                    schema["properties"]["actor_boundary"]["$ref"],
                )
                if relative_path in [
                    "schemas/review-result.schema.json",
                    "schemas/context-pack.schema.json",
                ]:
                    self.assertNotIn("target_population", schema["required"])
                    self.assertNotIn("target_population", schema["properties"])

    def test_review_and_context_use_actor_boundary_as_only_target_population_source(self):
        cases = [
            ("schemas/review-result.schema.json", "examples/quick-gate-review.json"),
            ("schemas/context-pack.schema.json", "examples/quick-context-pack.json"),
        ]
        for schema_path, example_path in cases:
            with self.subTest(schema_path=schema_path, example_path=example_path):
                validator = contract_validator(schema_path)
                artifact = load_json(example_path)

                self.assertNotIn("target_population", artifact)
                self.assertTrue(validator.is_valid(artifact))

                duplicate = json.loads(json.dumps(artifact))
                duplicate["target_population"] = duplicate["actor_boundary"][
                    "target_population"
                ]
                self.assertFalse(validator.is_valid(duplicate))

                missing_actor_target = json.loads(json.dumps(artifact))
                missing_actor_target["actor_boundary"].pop("target_population")
                self.assertFalse(validator.is_valid(missing_actor_target))

    def test_review_schema_leaves_semantic_weakest_flow_checks_to_check_review(self):
        schema = load_json("schemas/review-result.schema.json")
        conditional_rules = json.dumps(schema.get("allOf", []))

        self.assertNotIn("weakest_flow", conditional_rules)
        self.assertNotIn("evidence_tier", conditional_rules)

    def test_reviewer_contract_forces_a_challenge_round(self):
        schema = load_json("schemas/reviewer-verdict.schema.json")
        self.assertIn("review_round", set(schema["required"]))
        validator = Draft202012Validator(schema)
        base = {
            "reviewer": "user_flow",
            "review_round": "independent",
            "verdict": "verify",
            "strongest_signal": "s",
            "weakest_assumption": "w",
            "missing_evidence": "m",
            "disconfirming_evidence": "d",
            "evidence_tier": "t1",
            "confidence_level": "low",
            "stop_condition": "sc",
            "next_smallest_action": "n",
        }
        challenge_fields = {
            "objection_to": "business_flow",
            "counter_evidence": "c",
            "position_change": "unchanged",
        }
        # independent round: challenge fields are forbidden
        self.assertTrue(validator.is_valid(base))
        self.assertFalse(validator.is_valid({**base, **challenge_fields}))
        # challenge round: challenge fields are required
        challenge = {**base, "review_round": "challenge"}
        self.assertFalse(validator.is_valid(challenge))
        self.assertTrue(validator.is_valid({**challenge, **challenge_fields}))

    def test_evidence_required_free_text_fields_reject_empty_strings(self):
        schema = load_json("schemas/evidence.schema.json")
        validator = Draft202012Validator(schema)
        evidence = load_json("examples/evidence-response.json")["receipts"][0]

        for field in ["interpretation", "decision_impact", "counter_signal"]:
            with self.subTest(field=field):
                invalid = {**evidence, field: ""}
                self.assertFalse(validator.is_valid(invalid))

    def test_reviewer_required_free_text_fields_reject_empty_strings(self):
        schema = load_json("schemas/reviewer-verdict.schema.json")
        validator = Draft202012Validator(schema)
        verdict = {
            "reviewer": "user_flow",
            "review_round": "independent",
            "verdict": "verify",
            "strongest_signal": "s",
            "weakest_assumption": "w",
            "missing_evidence": "m",
            "disconfirming_evidence": "d",
            "evidence_tier": "t1",
            "confidence_level": "low",
            "stop_condition": "sc",
            "next_smallest_action": "n",
        }
        self.assertTrue(validator.is_valid(verdict))

        for field in [
            "strongest_signal",
            "weakest_assumption",
            "missing_evidence",
            "disconfirming_evidence",
            "stop_condition",
            "next_smallest_action",
        ]:
            with self.subTest(field=field):
                invalid = {**verdict, field: ""}
                self.assertFalse(validator.is_valid(invalid))

        challenge = {
            **verdict,
            "review_round": "challenge",
            "objection_to": "business_flow",
            "counter_evidence": "c",
            "position_change": "unchanged",
        }
        self.assertTrue(validator.is_valid(challenge))
        self.assertFalse(validator.is_valid({**challenge, "counter_evidence": ""}))

    def test_review_result_lane_free_text_fields_reject_empty_strings(self):
        validator = contract_validator("schemas/review-result.schema.json")
        review = load_json("examples/quick-gate-review.json")
        self.assertTrue(validator.is_valid(review))

        for field in [
            "strongest_signal",
            "weakest_assumption",
            "missing_evidence",
            "disconfirming_evidence",
            "stop_condition",
        ]:
            with self.subTest(field=field):
                invalid = json.loads(json.dumps(review))
                invalid["reviews"]["user"][field] = ""
                self.assertFalse(validator.is_valid(invalid))

    def test_stop_reason_class_is_required_on_stop(self):
        schema = load_json("schemas/reviewer-verdict.schema.json")
        validator = Draft202012Validator(schema)
        stop = {
            "reviewer": "evidence_flow",
            "review_round": "independent",
            "verdict": "stop_reframe",
            "strongest_signal": "s",
            "weakest_assumption": "w",
            "missing_evidence": "m",
            "disconfirming_evidence": "d",
            "evidence_tier": "t0",
            "confidence_level": "very_low",
            "stop_condition": "sc",
            "next_smallest_action": "n",
        }
        self.assertFalse(validator.is_valid(stop))
        self.assertTrue(
            validator.is_valid({**stop, "stop_reason_class": "core_evidence"})
        )

    def test_claim_contract_requires_dependency_edges(self):
        schema = load_json("schemas/claim.schema.json")
        required = set(schema["required"])
        self.assertTrue({"depends_on", "breaks_if_false"}.issubset(required))

    def test_evidence_contract_requires_provenance_and_freshness(self):
        schema = load_json("schemas/evidence.schema.json")
        required = set(schema["required"])
        expected = {
            "evidence_id",
            "source_id",
            "raw_artifact_uri",
            "signal_type",
            "evidence_tier",
            "collected_at",
            "source_last_verified_at",
            "max_staleness_days",
        }
        self.assertTrue(expected.issubset(required))

    def test_agent_registry_is_machine_readable(self):
        registry = load_json("agents/registry.json")
        ids = {agent["id"] for agent in registry["agents"]}
        self.assertEqual(
            {
                "claim_analyst",
                "user_flow_reviewer",
                "evidence_flow_reviewer",
                "business_flow_reviewer",
                "uncertainty_reviewer",
                "council_facilitator",
            },
            ids,
        )
        for agent in registry["agents"]:
            self.assertTrue((ROOT / agent["instructions"]).is_file())
            self.assertTrue((ROOT / agent["input_schema"]).is_file())
            self.assertTrue((ROOT / agent["output_schema"]).is_file())

    def test_json_examples_match_the_canonical_contract(self):
        schema = load_json("schemas/review-result.schema.json")
        validator = contract_validator("schemas/review-result.schema.json")
        for relative_path in [
            "examples/quick-gate-review.json",
            "examples/standard-gate-review.json",
            "examples/ux3-council-review.json",
            "examples/stop-reframe-review.json",
        ]:
            example = load_json(relative_path)
            validator.validate(example)

        contract_validator("schemas/context-pack.schema.json").validate(
            load_json("examples/quick-context-pack.json")
        )
        Draft202012Validator(
            load_json("schemas/human-decision.schema.json")
        ).validate(load_json("examples/human-decision.json"))

        evidence_schemas = [
            load_json("schemas/evidence.schema.json"),
            load_json("schemas/evidence-response.schema.json"),
        ]
        registry = Registry().with_resources(
            [
                (schema["$id"], Resource.from_contents(schema))
                for schema in evidence_schemas
            ]
        )
        Draft202012Validator(
            evidence_schemas[1], registry=registry
        ).validate(load_json("examples/evidence-response.json"))

        Draft202012Validator(
            load_json("schemas/red-team-review.schema.json")
        ).validate(load_json("examples/red-team-review.json"))

    def test_live_coding_chain_is_traceable_and_bounded(self):
        brief = load_json("examples/live-coding-product-brief.json")
        review = load_json("examples/live-coding-review.json")
        context_pack = load_json("examples/live-coding-context-pack.json")

        contract_validator("schemas/product-brief.schema.json").validate(brief)
        contract_validator("schemas/review-result.schema.json").validate(review)
        contract_validator("schemas/context-pack.schema.json").validate(context_pack)

        execution_boundary = {
            "may_do": [
                "Add one visible save-state label to the existing note editor header.",
                "Use the current save state already available to the editor UI.",
                "Add or preserve a measurement hook that can compare exit hesitation and save-state support-tag volume.",
            ],
            "must_not_do": ["expand scope or execute external irreversible actions"],
            "must_ask": ["new stakeholder, data, risk, or scope appears"],
        }
        for artifact in [brief, review, context_pack]:
            self.assertEqual(artifact["session_config"], review["session_config"])
            self.assertEqual(execution_boundary, artifact["execution_boundary"])

        self.assertEqual(review["review_id"], context_pack["review_id"])
        self.assertIn(review["review_id"], json.dumps(brief))
        self.assertEqual("continue", review["combined_verdict"])
        self.assertEqual("continue", context_pack["combined_verdict"])
        self.assertTrue(review["context_pack_required"])
        self.assertEqual([], review["high_risk_actions"])
        self.assertEqual([], context_pack["high_risk_actions"])

        evidence_ids = [receipt["evidence_id"] for receipt in brief["current_evidence"]]
        self.assertEqual(evidence_ids, review["evidence_receipt_ids"])
        self.assertEqual(evidence_ids, context_pack["evidence_snapshot_ids"])

        self.assertNotIn("target_population", review)
        self.assertNotIn("target_population", context_pack)
        self.assertEqual(
            brief["actor_boundary"]["target_population"],
            review["actor_boundary"]["target_population"],
        )
        self.assertEqual(
            review["actor_boundary"]["target_population"],
            context_pack["actor_boundary"]["target_population"],
        )
        self.assertEqual(brief["actor_boundary"], review.get("actor_boundary"))
        self.assertEqual(brief["actor_boundary"], context_pack.get("actor_boundary"))
        self.assertEqual(
            brief["actor_boundary"]["affected_people"],
            review["actor_boundary"]["affected_people"],
        )
        self.assertEqual(
            brief["actor_boundary"]["excluded_groups"],
            context_pack["actor_boundary"]["excluded_groups"],
        )
        self.assertEqual(
            {
                "organization": brief["business_boundary"]["product_organization"],
                "project_owner": brief["business_boundary"]["project_owner"],
                "issuer": brief["business_boundary"]["issuer"],
            },
            review["product_organization"],
        )
        self.assertEqual(
            review["product_organization"], context_pack["product_organization"]
        )
        self.assertEqual(
            review["stakeholder_effects"], context_pack["stakeholder_effects"]
        )
        self.assertEqual(
            brief["actor_boundary"]["affected_people"],
            [effect["stakeholder"] for effect in review["stakeholder_effects"]],
        )
        self.assertEqual(
            brief["unresolved_assumptions"], review["unresolved_assumptions"]
        )
        self.assertEqual(
            review["unresolved_assumptions"],
            context_pack["unresolved_assumptions"],
        )
        self.assertEqual(
            brief["human_judgment_boundary"], review["human_judgment_boundary"]
        )
        self.assertEqual(
            review["human_judgment_boundary"],
            context_pack["human_judgment_boundary"],
        )

    def test_live_coding_review_none_decision_has_no_residual_taste_gate(self):
        artifacts = [
            load_json("examples/live-coding-product-brief.json"),
            load_json("examples/live-coding-review.json"),
            load_json("examples/live-coding-context-pack.json"),
        ]
        review = artifacts[1]

        self.assertEqual("none", review["human_owned_decision"])
        self.assertIsNone(review["human_decision_record_id"])
        for artifact in artifacts:
            boundary = artifact["human_judgment_boundary"]
            self.assertEqual([], boundary["human_owned_decisions"])
            self.assertEqual([], boundary["not_mechanized"])
            self.assertEqual([], boundary["approval_gates"])

        combined_text = json.dumps(artifacts, ensure_ascii=False).lower()
        forbidden_phrases = [
            "final wording",
            "visual prominence",
            "brand tone",
            "taste",
            "human-owned call",
        ]
        for phrase in forbidden_phrases:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, combined_text)

    def test_product_brief_rejects_missing_session_config(self):
        validator = contract_validator("schemas/product-brief.schema.json")
        self.assertTrue(validator.is_valid(self.valid_product_brief()))

        product_brief = self.valid_product_brief()
        product_brief.pop("session_config")

        self.assertFalse(validator.is_valid(product_brief))

    def test_product_brief_rejects_empty_target_population(self):
        validator = contract_validator("schemas/product-brief.schema.json")
        self.assertTrue(validator.is_valid(self.valid_product_brief()))

        product_brief = self.valid_product_brief()
        product_brief["actor_boundary"]["target_population"] = []

        self.assertFalse(validator.is_valid(product_brief))

    def test_product_brief_rejects_missing_product_organization_or_issuer(self):
        validator = contract_validator("schemas/product-brief.schema.json")
        self.assertTrue(validator.is_valid(self.valid_product_brief()))

        missing_organization = self.valid_product_brief()
        missing_organization["business_boundary"].pop("product_organization")
        missing_issuer = self.valid_product_brief()
        missing_issuer["business_boundary"].pop("issuer")

        self.assertFalse(validator.is_valid(missing_organization))
        self.assertFalse(validator.is_valid(missing_issuer))

    def test_product_brief_rejects_missing_unresolved_assumptions(self):
        validator = contract_validator("schemas/product-brief.schema.json")
        self.assertTrue(validator.is_valid(self.valid_product_brief()))

        product_brief = self.valid_product_brief()
        product_brief.pop("unresolved_assumptions")

        self.assertFalse(validator.is_valid(product_brief))

    def test_product_brief_rejects_missing_execution_boundary_or_must_ask(self):
        validator = contract_validator("schemas/product-brief.schema.json")
        self.assertTrue(validator.is_valid(self.valid_product_brief()))

        missing_boundary = self.valid_product_brief()
        missing_boundary.pop("execution_boundary")
        missing_must_ask = self.valid_product_brief()
        missing_must_ask["execution_boundary"].pop("must_ask")

        self.assertFalse(validator.is_valid(missing_boundary))
        self.assertFalse(validator.is_valid(missing_must_ask))

    def test_product_brief_rejects_generic_human_approval_gate_strings(self):
        validator = contract_validator("schemas/product-brief.schema.json")
        self.assertTrue(validator.is_valid(self.valid_product_brief()))

        product_brief = self.valid_product_brief()
        product_brief["human_judgment_boundary"]["approval_gates"] = [
            "Product owner approves release"
        ]

        self.assertFalse(validator.is_valid(product_brief))

    def test_context_pack_rejects_high_risk_actions_without_approval_or_rollback(self):
        validator = contract_validator("schemas/context-pack.schema.json")
        self.assertTrue(validator.is_valid(self.valid_high_risk_context_pack()))

        missing_approval = self.valid_high_risk_context_pack()
        missing_approval["high_risk_actions"][0].pop("approval_gate")
        missing_rollback = self.valid_high_risk_context_pack()
        missing_rollback["high_risk_actions"][0].pop("rollback_plan")

        self.assertFalse(validator.is_valid(missing_approval))
        self.assertFalse(validator.is_valid(missing_rollback))

    def test_context_pack_rejects_generic_human_approval_gate_strings(self):
        validator = contract_validator("schemas/context-pack.schema.json")
        self.assertTrue(validator.is_valid(self.valid_context_pack()))

        context_pack = self.valid_context_pack()
        context_pack["human_approval_gates"] = ["Product owner approves release"]

        self.assertFalse(validator.is_valid(context_pack))

    def test_review_result_rejects_high_risk_actions_without_approval_or_rollback(self):
        validator = contract_validator("schemas/review-result.schema.json")
        review = self.valid_high_risk_review_result()
        self.assertTrue(validator.is_valid(review))

        missing_approval = self.valid_high_risk_review_result()
        missing_approval["high_risk_actions"][0].pop("approval_gate")
        missing_rollback = self.valid_high_risk_review_result()
        missing_rollback["high_risk_actions"][0].pop("rollback_plan")

        self.assertFalse(validator.is_valid(missing_approval))
        self.assertFalse(validator.is_valid(missing_rollback))

    def test_high_risk_may_do_requires_structured_risk_controls(self):
        review_validator = contract_validator("schemas/review-result.schema.json")
        context_validator = contract_validator("schemas/context-pack.schema.json")

        review = load_json("examples/quick-gate-review.json")
        review["execution_boundary"]["may_do"] = [
            "Change customer-facing permissions."
        ]
        review["high_risk_actions"] = []
        context_pack = self.valid_context_pack()
        context_pack["execution_boundary"]["may_do"] = [
            "Change customer-facing permissions."
        ]
        context_pack["high_risk_actions"] = []

        self.assertFalse(review_validator.is_valid(review))
        self.assertFalse(context_validator.is_valid(context_pack))

    def test_review_result_rejects_generic_human_approval_gate_strings(self):
        validator = contract_validator("schemas/review-result.schema.json")
        review = self.valid_high_risk_review_result()
        self.assertTrue(validator.is_valid(review))

        review["human_approval_gates"] = ["Product owner approves release"]
        review["high_risk_actions"][0]["approval_gate"] = "Product owner approval"

        self.assertFalse(validator.is_valid(review))

    def test_review_result_uses_session_config_schema_reference(self):
        schema = load_json("schemas/review-result.schema.json")

        self.assertEqual(
            "session-config.schema.json",
            schema["properties"]["session_config"]["$ref"],
        )
        self.assertNotIn("session_config", schema.get("$defs", {}))

    def test_templates_expose_task_3_contract_fields(self):
        product_brief = (ROOT / "templates/product-brief.md").read_text(
            encoding="utf-8"
        )
        gate_review = (ROOT / "templates/gate-review.md").read_text(encoding="utf-8")
        context_pack = (ROOT / "templates/context-pack.md").read_text(
            encoding="utf-8"
        )

        for text in [product_brief, gate_review, context_pack]:
            for required_text in [
                "schema_version | 2.1",
                "working_language",
                "Unresolved assumptions",
                "May do",
                "Must not do",
                "Must ask",
                "Named human approval gate",
                "Accountable owner",
                "Condition",
                "Rollback plan",
            ]:
                self.assertIn(required_text, text)

    def test_context_pack_rejects_missing_execution_boundary_must_ask(self):
        validator = contract_validator("schemas/context-pack.schema.json")
        context_pack = self.valid_context_pack()
        self.assertTrue(validator.is_valid(context_pack))

        context_pack["execution_boundary"].pop("must_ask", None)

        self.assertFalse(validator.is_valid(context_pack))

    def test_context_pack_rejects_unsupported_working_language(self):
        validator = contract_validator("schemas/context-pack.schema.json")
        context_pack = self.valid_context_pack()
        self.assertTrue(validator.is_valid(context_pack))

        context_pack["session_config"]["working_language"] = "xx"

        self.assertFalse(validator.is_valid(context_pack))

    def valid_high_risk_context_pack(self):
        context_pack = self.valid_context_pack()
        context_pack["high_risk_actions"] = [
            {
                "action": "Change customer-facing permissions.",
                "approval_gate": self.named_human_gate(),
                "rollback_plan": "Restore the prior permission rules.",
            }
        ]
        return context_pack

    def valid_high_risk_review_result(self):
        review = load_json("examples/ux3-council-review.json")
        review["human_approval_gates"] = [
            {
                "gate_id": "accountable-owner-customer-action-approval",
                "accountable_owner": "Named accountable owner",
                "condition": "Before any customer-facing execution.",
            }
        ]
        review["high_risk_actions"] = [
            {
                "action": "Execute customer-facing workflow actions.",
                "approval_gate": review["human_approval_gates"][0],
                "rollback_plan": "Stop the test and restore manual approval.",
            }
        ]
        return review

    def valid_context_pack(self):
        context_pack = load_json("examples/quick-context-pack.json")
        context_pack["schema_version"] = "2.1"
        context_pack["session_config"] = {
            "working_language": "en",
            "canonical_identifiers": "en",
            "fallback_language": "en",
        }
        context_pack["product_organization"] = {
            "organization": "Example Product Co.",
            "project_owner": "Activation team",
            "issuer": "Example Product Co.",
        }
        context_pack["stakeholder_effects"] = [
            {
                "stakeholder": "Invited team members",
                "effect": "Clearer setup can reduce delayed invitations.",
            }
        ]
        context_pack["human_judgment_boundary"] = {
            "human_owned_decisions": ["Final copy tone"],
            "machine_supported_inputs": ["Support notes", "Session replays"],
            "not_mechanized": ["Taste and brand judgment"],
            "approval_gates": [self.named_human_gate()],
        }
        context_pack["unresolved_assumptions"] = [
            "Whether copy or missing product guidance causes the hesitation."
        ]
        context_pack["execution_boundary"]["must_ask"] = [
            "A material scope, risk, data, or stakeholder impact changes."
        ]
        context_pack["high_risk_actions"] = []
        context_pack["human_approval_gates"] = [self.named_human_gate()]
        return context_pack

    def test_example_cross_references_resolve(self):
        quick_review = load_json("examples/quick-gate-review.json")
        context_pack = load_json("examples/quick-context-pack.json")
        evidence_response = load_json("examples/evidence-response.json")
        council_review = load_json("examples/ux3-council-review.json")
        human_decision = load_json("examples/human-decision.json")

        evidence_ids = {
            receipt["evidence_id"] for receipt in evidence_response["receipts"]
        }
        self.assertTrue(
            set(quick_review["evidence_receipt_ids"]).issubset(evidence_ids)
        )
        self.assertTrue(
            set(context_pack["evidence_snapshot_ids"]).issubset(evidence_ids)
        )
        self.assertEqual(
            council_review["human_decision_record_id"],
            human_decision["decision_id"],
        )

    def test_all_json_schemas_are_valid_draft_2020_12(self):
        for path in sorted((ROOT / "schemas").glob("*.json")):
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)

    def test_local_schema_references_exist(self):
        missing = []
        for path in sorted((ROOT / "schemas").glob("*.json")):
            schema = path.read_text(encoding="utf-8")
            for reference in re.findall(r'"\$ref"\s*:\s*"([^"]+)"', schema):
                if reference.startswith("#") or "://" in reference:
                    continue
                target = reference.split("#", 1)[0]
                if target and not (path.parent / target).is_file():
                    missing.append(f"{path.name}: {target}")
        self.assertEqual([], missing)

    def test_entrypoints_name_the_canonical_schema(self):
        for relative_path in [
            "README.md",
            "skills/product-design-harness/SKILL.md",
            "llms.txt",
        ]:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("schemas/review-result.schema.json", text, relative_path)

    def test_backticked_repository_paths_exist(self):
        missing = []
        known_dirs = [
            ROOT, ROOT / "schemas", ROOT / "templates", ROOT / "prompts",
            ROOT / "examples", ROOT / "docs", ROOT / "agents", ROOT / "adapters",
            ROOT / "scripts", ROOT / "tests", ROOT / "assets", ROOT / "i18n",
        ]
        for path in ROOT.rglob("*.md"):
            if not validate.should_check_repository_paths(path):
                continue
            text = path.read_text(encoding="utf-8")
            for token in validate.REPOSITORY_PATH_TOKEN.findall(text):
                candidates = [ROOT / token, path.parent / token]
                if token.startswith("resources/"):
                    candidates.append(validate.BUNDLE_ROOT / token)
                if not any(candidate.exists() for candidate in candidates):
                    missing.append(f"{path.relative_to(ROOT)}: {token}")
            for token in validate.BARE_FILE_TOKEN.findall(text):
                if "/" in token or not validate.should_check_bare_reference(token):
                    continue
                candidates = [path.parent / token] + [d / token for d in known_dirs]
                if not any(candidate.exists() for candidate in candidates):
                    missing.append(f"{path.relative_to(ROOT)}: {token}")
        self.assertEqual([], missing)

    def test_skill_description_is_trigger_only(self):
        text = (ROOT / "skills" / "product-design-harness" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        description = next(
            line.removeprefix("description: ").strip()
            for line in text.splitlines()
            if line.startswith("description: ")
        )
        self.assertTrue(description.startswith("Use when"))

    def test_public_release_is_vendor_neutral(self):
        terms = [
            "Co" + "dex",
            "Clau" + "de",
            "Open" + chr(65) + chr(73),
            "Anthro" + "pic",
        ]
        banned = re.compile(r"\b(?:" + "|".join(terms) + r")\b", re.IGNORECASE)
        findings = []
        for path in validate.iter_files():
            if path.suffix == ".pyc":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if banned.search(text):
                findings.append(str(path.relative_to(ROOT)))
        self.assertEqual([], findings)


    def test_combined_verdict_matches_lane_verdicts_in_schema(self):
        validator = contract_validator("schemas/review-result.schema.json")
        example = load_json("examples/quick-gate-review.json")

        broken = json.loads(json.dumps(example))
        for lane in ["user", "evidence", "business"]:
            broken["reviews"][lane]["verdict"] = "stop_reframe"
        self.assertFalse(validator.is_valid(broken))

        broken = json.loads(json.dumps(example))
        broken["reviews"]["evidence"]["verdict"] = "verify"
        self.assertFalse(validator.is_valid(broken))

    def test_verdict_exclusive_fields_are_rejected(self):
        validator = contract_validator("schemas/review-result.schema.json")
        continue_example = load_json("examples/quick-gate-review.json")
        verify_example = load_json("examples/standard-gate-review.json")

        for leaked_field in ["proof_step", "reframed_question"]:
            broken = json.loads(json.dumps(continue_example))
            broken[leaked_field] = "leaked"
            self.assertFalse(validator.is_valid(broken), leaked_field)

        broken = json.loads(json.dumps(verify_example))
        broken["reframed_question"] = "leaked"
        self.assertFalse(validator.is_valid(broken))

    WEAKEST_FLOW_SEVERITY = {"stop_reframe": 2, "verify": 1, "continue": 0}
    WEAKEST_FLOW_PRIORITY = {"evidence": 0, "user": 1, "business": 2}

    def expected_weakest_flow(self, reviews):
        def sort_key(lane):
            review = reviews[lane]
            return (
                -self.WEAKEST_FLOW_SEVERITY[review["verdict"]],
                review["evidence_tier"],
                self.WEAKEST_FLOW_PRIORITY[lane],
            )
        return sorted(reviews, key=sort_key)[0]

    def test_examples_follow_the_weakest_flow_algorithm(self):
        for relative_path in [
            "examples/quick-gate-review.json",
            "examples/standard-gate-review.json",
            "examples/ux3-council-review.json",
            "examples/stop-reframe-review.json",
        ]:
            example = load_json(relative_path)
            severities = [
                self.WEAKEST_FLOW_SEVERITY[lane["verdict"]]
                for lane in example["reviews"].values()
            ]
            expected_combined = ["continue", "verify", "stop_reframe"][max(severities)]
            self.assertEqual(
                expected_combined, example["combined_verdict"], relative_path
            )
            self.assertEqual(
                self.expected_weakest_flow(example["reviews"]),
                example["weakest_flow"],
                relative_path,
            )

    def test_repository_is_english_only(self):
        offenders = []
        for path in validate.iter_files():
            if path.suffix.lower() in validate.BINARY_ASSET_SUFFIXES:
                continue
            if validate.is_ascii_exempt_path(path):
                continue
            data = path.read_text(encoding="utf-8", errors="ignore")
            if any(ord(ch) > 127 for ch in data):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual([], offenders)


    def test_adversarial_payloads_are_rejected(self):
        validator = contract_validator("schemas/review-result.schema.json")
        quick = load_json("examples/quick-gate-review.json")
        council = load_json("examples/ux3-council-review.json")
        standard = load_json("examples/standard-gate-review.json")

        attacks = []
        a = json.loads(json.dumps(quick))
        a["council_record"] = council["council_record"]
        attacks.append(("council_record outside council mode", a))
        a = json.loads(json.dumps(quick))
        a["combined_verdict"] = "stop_reframe"
        a["context_pack_required"] = False
        a["reframed_question"] = "q"
        attacks.append(("combined stop without a stopping lane", a))
        a = json.loads(json.dumps(council))
        a["council_record"]["independent_review_ids"] = ["x", "x", "x"]
        attacks.append(("duplicate independent review ids", a))
        a = json.loads(json.dumps(council))
        a["council_record"]["challenges"][0]["objection_to"] = a[
            "council_record"
        ]["challenges"][0]["reviewer"]
        attacks.append(("self-objection in challenge round", a))
        a = json.loads(json.dumps(quick))
        a["execution_boundary"] = {"may_do": [], "must_not_do": []}
        attacks.append(("empty execution boundary", a))
        a = json.loads(json.dumps(quick))
        a["stop_conditions"] = ["", ""]
        attacks.append(("blank stop conditions", a))
        for name, payload in attacks:
            self.assertFalse(validator.is_valid(payload), name)

    def test_check_review_rejects_semantic_weakest_flow_and_tier_mismatches(self):
        quick = load_json("examples/quick-gate-review.json")
        standard = load_json("examples/standard-gate-review.json")

        weakest_flow_attack = json.loads(json.dumps(standard))
        weakest_flow_attack["weakest_flow"] = "user"
        tier_attack = json.loads(json.dumps(quick))
        tier_attack["evidence_tier"] = "t4"

        for name, payload in [
            ("weakest_flow points at a continue lane", weakest_flow_attack),
            ("headline tier above lane tiers", tier_attack),
        ]:
            with self.subTest(name=name):
                self.assertTrue(contract_validator("schemas/review-result.schema.json").is_valid(payload))
                self.assertNotEqual([], check_review.check(payload))

    def test_check_review_script_accepts_all_golden_examples(self):
        import subprocess
        import sys
        for relative_path in [
            "examples/quick-gate-review.json",
            "examples/standard-gate-review.json",
            "examples/ux3-council-review.json",
            "examples/stop-reframe-review.json",
            "examples/live-coding-review.json",
        ]:
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "check_review.py"),
                 str(ROOT / relative_path)],
                capture_output=True, text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)

    def test_ux3_has_no_version_suffix(self):
        pattern = re.compile(
            "UX3" + r"\.6" + "|" + "UX" + "36" + "|" + "ux" + "36",
            re.IGNORECASE,
        )
        self.assertIsNotNone(pattern.search("UX3" + ".6"))
        self.assertIsNotNone(pattern.search("UX" + "36"))
        self.assertIsNone(pattern.search("UX3"))

        def scan(root):
            findings = []
            scanned = []
            with patch.object(validate, "ROOT", root):
                for path in validate.iter_files():
                    if path.suffix == ".pyc":
                        continue
                    relative_path = str(path.relative_to(root))
                    scanned.append(relative_path)
                    if pattern.search(relative_path):
                        findings.append(relative_path)
                        continue
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    if pattern.search(text):
                        findings.append(relative_path)
            return findings, scanned

        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            scratch = (
                fixture_root
                / ".superpowers"
                / "sdd"
                / ("legacy-" + "UX3" + ".6.txt")
            )
            self.assertFalse(scratch.parent.exists())
            scratch.parent.mkdir(parents=True)
            scratch.write_text("review artifact", encoding="utf-8")

            design_doc = fixture_root / "docs" / "superpowers" / "plan.md"
            design_doc.parent.mkdir(parents=True)
            design_doc.write_text("design plan", encoding="utf-8")
            (fixture_root / "README.md").write_text("UX3", encoding="utf-8")

            fixture_findings, fixture_scanned = scan(fixture_root)
            self.assertNotIn(str(scratch.relative_to(fixture_root)), fixture_scanned)
            self.assertIn(
                str(design_doc.relative_to(fixture_root)), fixture_scanned
            )
            self.assertIn("README.md", fixture_scanned)
            self.assertEqual([], fixture_findings)

        self.assertFalse(fixture_root.exists())
        repository_findings, _ = scan(ROOT)
        self.assertEqual([], repository_findings)


if __name__ == "__main__":
    unittest.main()
