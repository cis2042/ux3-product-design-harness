# UX3 Product Design Harness: Canonical Answers

These answers are the concise public description of UX3. They match the FAQ
shown on the project website. Last reviewed: 2026-07-11.

## What is the UX3 Product Design Harness?

UX3 Product Design Harness is an open, installable product judgment protocol
for AI-agent teams. Before design or implementation, it reviews a decision
across User Flow, Evidence Flow, and Business Flow, then returns one
contract-validated verdict.

Source: [UX3 model](https://github.com/cis2042/ux3-product-design-harness/blob/main/docs/UX3.md)

## How is UX3 different from a coding harness?

A coding harness checks whether software is built correctly. UX3 checks
whether the team should build the proposed direction, what evidence supports
it, who receives and pays for value, and where human judgment must remain
accountable.

Source: [Harness comparison](https://github.com/cis2042/ux3-product-design-harness/blob/main/docs/CODING-HARNESS-COMPARISON.md)

## When should an agent invoke UX3?

Invoke UX3 before a new or materially changed product direction, feature,
workflow, experiment, or costly irreversible commitment. Skip it for purely
mechanical execution that already has an approved boundary and valid context
pack.

Source: [Installable skill](https://github.com/cis2042/ux3-product-design-harness/blob/main/skills/product-design-harness/SKILL.md)

## What are the three UX3 flows?

User Flow identifies target populations, affected people, situations, tasks,
and desired outcomes. Evidence Flow tests claims with sources, signals,
counter-signals, and uncertainty. Business Flow identifies owners,
stakeholders, value exchange, costs, and durability.

Source: [Three-flow definitions](https://github.com/cis2042/ux3-product-design-harness/blob/main/docs/UX3.md)

## What verdicts can UX3 return?

UX3 returns continue, verify, or stop_reframe. Continue permits bounded
execution, verify requires specified evidence before proceeding, and
stop_reframe rejects the current framing and requires a better product
question.

Source: [Canonical contracts](https://github.com/cis2042/ux3-product-design-harness/blob/main/docs/CONTRACTS.md)

## How does UX3 handle evidence and uncertainty?

Evidence is graded from untraceable belief to durable behavioral and economic
proof. UX3 records provenance, freshness, counter-signals, and uncertainty,
then lets the weakest flow and worst verdict control the next action instead of
averaging scores.

Source: [Uncertainty model](https://github.com/cis2042/ux3-product-design-harness/blob/main/docs/UNCERTAINTY.md)

## What decisions must remain human-owned?

Taste, strategy, ethics, meaning, risk appetite, and final accountability
remain human-owned. An agent may analyze options and evidence, but an
accountable person records the decision, rationale, owner, and reversal
conditions.

Source: [Human judgment principles](https://github.com/cis2042/ux3-product-design-harness/blob/main/docs/PRINCIPLES.md)

## How does an agent install and use UX3?

Install UX3 with `npx skills add cis2042/ux3-product-design-harness -g -y`. Ask the
agent to review a product decision before implementation; the skill selects
Quick Gate, Standard Gate, or UX3 Council and emits the canonical review
contract.

Source: [Adoption guide](https://github.com/cis2042/ux3-product-design-harness/blob/main/docs/ADOPTION.md)

## What is an Agentic Design Process?

An Agentic Design Process treats AI agents as active participants across
product framing, research, ideation, prototyping, build, launch, and feedback.
UX3 gives those participants stage gates, evidence duties, execution
boundaries, and one shared review contract.

Source: [Full-loop harness](https://github.com/cis2042/ux3-product-design-harness/blob/main/docs/HARNESS.md)

## What does Designer-in-the-Loop mean?

Designer-in-the-Loop means a designer remains accountable for taste, problem
framing, trade-offs, ethics, meaning, and uncertainty while agents explore
options, retrieve evidence, and execute bounded work. It is a decision role,
not approval of every small task.

Source: [Human judgment principles](https://github.com/cis2042/ux3-product-design-harness/blob/main/docs/PRINCIPLES.md)
