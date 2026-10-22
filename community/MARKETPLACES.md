# Marketplace publication

UX3 Product Design Harness is distributed from
https://github.com/cis2042/ux3-product-design-harness under the MIT license.
The installable skill remains named product-design-harness.

## Listing metadata

| Field | Value |
| --- | --- |
| Display name | UX3 Product Design Harness |
| Skill name | product-design-harness |
| Category | Product design / Product management |
| Description | Review product direction, features, experiments, launches, and feedback across User Flow, Evidence Flow, and Business Flow. Return a validated continue, verify, or stop_reframe verdict with an execution boundary and accountable human judgment. |
| Source | https://github.com/cis2042/ux3-product-design-harness |
| Skill directory | https://github.com/cis2042/ux3-product-design-harness/tree/main/skills/product-design-harness |
| Website | https://cis2042.github.io/ux3-product-design-harness/ |
| License | MIT |
| Tags | product-design, product-management, ux, evidence, decision-making, agent-skills |
| Dependencies | Python 3 and jsonschema from requirements-dev.txt for output validation; no hosted service or paid model is required. |

Install from the canonical repository:

```text
npx skills add cis2042/ux3-product-design-harness --skill product-design-harness
```

Example request:

```text
Use UX3 Product Design Harness. Working language: en.
Review whether we should launch this feature using the supplied user,
evidence, and business context. State the weakest flow and the bounded next action.
```

## Submission artifact

The Validate GitHub Actions workflow tests the repository, installs the complete
skill, validates an installed golden review, and uploads the
product-design-harness-marketplace artifact. Its ZIP contains the skill
entrypoint, MIT notice, and complete resources at the package root.
An artifact from a pull request is a review candidate; use the matching
successful main-branch workflow artifact for public submissions after merge.

## Target directories

| Directory | Official submission or indexing route |
| --- | --- |
| SkillsMP | Public GitHub indexing; inspect current source metadata with https://skillsmp.com/docs/api before claiming an updated listing. |
| skills.sh | https://skills.sh/docs/faq documents automatic discovery through real skills CLI installations. A repository rename can require the new source to be indexed separately. |
| skills.rest | https://skills.rest/contribute accepts a public GitHub repository or skill-folder URL for screening and indexing. |
| Skills Directory | https://app.skillsdirectory.com/submit requires sign-in and submission review. |
| LobeHub | https://lobehub.com/docs/usage/community/become-a-creator describes creator profile, Skills, and Submit Repository. |

These targets were selected from publicly stated catalog scale on 2026-10-23.
Counts have different scopes and are not an independently audited global ranking.
SkillHub and agentmods were also inspected; their observed skill counts were
smaller than these targets, so they are optional additional distribution channels.
A prepared package, submitted repository, search result, or HTTP 200 alone does
not establish publication. Verify a public detail page containing the actual
skill and a working source or installation route for every target.

## Repository rename

The GitHub repository moved from cis2042/product-design-harness to
cis2042/ux3-product-design-harness. GitHub redirects the old repository URL,
but the old GitHub Pages path returns 404. Published metadata, schema IDs,
installation commands, and bundled copies now use the renamed Pages and
repository URLs. Consumers that pin schema URLs should update the base to
https://cis2042.github.io/ux3-product-design-harness/schemas/.
The review fields, verdicts, and internal skill directory are unchanged.
