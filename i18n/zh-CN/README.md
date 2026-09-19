# UX3 Product Design Harness

用机器可检查的方式，为产品方向、构建、上线和反馈循环做判断。

<!-- locale-selector -->
## 阅读语言 / 工作语言

**Read in:** [English](../../README.md) | [繁體中文](../zh-TW/README.md) |
[简体中文](README.md) | [日本語](../ja/README.md) |
[한국어](../ko/README.md) | [Español](../es/README.md) |
[Français](../fr/README.md) | [Deutsch](../de/README.md) |
[Português](../pt/README.md)

**Work in:** 复制这段到 agent session。

```text
Use UX3 Product Design Harness for this repository.
Working language: zh-CN.
Review this product decision before implementation: <decision>.
```

完整技术参考以英文为准：[canonical English README](../../README.md) 与
[English handbook](../../docs/HARNESS.md)。

![Product Design Harness 封面](../../assets/product-design-harness-cover.svg)

UX3 Product Design Harness 是产品循环的判断层。它从「为什么要做」
开始把关，并覆盖规格、构建、上线、用户测试和反馈整理，
最后返回机器可检查的判断：`continue`、`verify` 或
`stop_reframe`。

它不绑定框架：prompt、JSON Schema、知识文件与 agent 定义可接入任何 agent runtime。
它没有 server 或 SDK；`jsonschema` 供 `scripts/check_review.py` 与
`scripts/validate.py` 验证输出与 repo 契约。人类入口是网站与 handbook；
agent 安装 `skills/product-design-harness/` 完整 bundle，再使用
`llms.txt`、prompts、schemas、rules 与 golden examples。
两者共用 UX3 Decision Kernel 和 canonical review contract。

<!-- where-it-sits -->
## 它位于哪里

Coding harness 用测试、类型与 CI 保护“怎么做”；Product Design Harness 保护
“为什么做”与“做完后如何判断”。它不是开发前的单一阶段，而是贯穿产品循环的判断层。

![Product Design Harness 的位置](../../assets/process-comparison.svg)

## 自主多 Agent 对齐 (Autonomous Multi-Agent Alignment)

在多 Agent 开发团队（1 Integrator 主控 + N Workers 执行者 + 1 QC Auditor 独立质检）中，本 harness 作为机器可读的边界宪法：
- **零停滞快速通道 (Zero-Stall Fast Path)**：例行任务（90%）完全绕过审查闸门，零阻塞、零延迟。
- **亚秒级 System One 判定 (Sub-Second System One Gating)**：`scripts/jev_gate.py` 在 300ms 内评估意图、证据等级与三轨裁决，不生成冗长散文。
- **无损上下文记忆保存 (Lossless Context Retention)**：边界锁定（`may_do` 与 `must_not_do`）跨多轮对话完整保留负向约束。

详细架构、角色契约与验证案例请参阅 [Multi-Agent Alignment](../../docs/MULTI-AGENT-ALIGNMENT.md)。

<!-- why-install -->
## 为什么安装

决策规则由机器强制,不是散文。格式错误的 review、与 lane 裁决矛盾的 combined verdict、may_do 与 must_not_do 出现同一条目的 execution boundary、或超出 evidence tier 授权的裁决,都会在出货前被验证挡下。

| 主张 | 验证位置 |
|---|---|
| 所有 review mode 共用 `schemas/review-result.schema.json`；repo 内共有 18 份 JSON Schema。 | `schemas/review-result.schema.json` |
| 工作语言明确设置，canonical identifiers 保持英文。 | `schemas/session-config.schema.json` |
| UX3 定义与 rule IDs 从机器文件载入。 | `knowledge/ontology.json`、`knowledge/rules.json` |
| 21 decision rule cards 将 kernel 变成可执行规则；六张保留章节来源，包括 `ux3.rule.human_agent_interaction` 与 `ux3.rule.motivation_ethics`。 | `knowledge/rules.json`、`knowledge/source-chapters.json`、`docs/DECISION-RULES.md` |
| JSON Schema 强制输出结构与各 verdict 的条件字段。 | `schemas/review-result.schema.json`、`tests/test_contracts.py` |
| Verdict 专属字段互斥；`continue` 不能带 `reframed_question`。 | `tests/test_contracts.py` |
| Challenge round 必须有 challenge 字段，independent round 禁止使用。 | `schemas/reviewer-verdict.schema.json` |
| 每个 `stop_reframe` lane verdict 必须有 `stop_reason_class`。 | `schemas/reviewer-verdict.schema.json` |
| actor_boundary.target_population 是 review 与 context pack 唯一的目标族群来源。 | `schemas/actor-boundary.schema.json`、`schemas/review-result.schema.json`、`schemas/context-pack.schema.json` |
| `scripts/check_review.py` 在 Schema 后检查 worst-verdict、weakest-flow 与 headline-tier。 | `scripts/check_review.py`、`docs/CONTRACTS.md`、`tests/test_contracts.py` |
| Evidence receipt 必须记录 provenance、freshness、counter-signal 与 `t0` 到 `t4` 的 tier。 | `schemas/evidence.schema.json` |
| 一旦 review 声明某决策为 human-owned,追踪链即被双向强制:decision record id、accountable owner 与 reversal conditions。声明本身是审查 agent 的判断,schema 无法强迫。 | `schemas/human-decision.schema.json`、`schemas/review-result.schema.json` |
| 裁决受 evidence tier 约束:headline tier 为 `t0` 时强制 `stop_reframe`,`t1` 永远不能返回 `continue`。 | `scripts/check_review.py`、`tests/test_semantic_guards.py` |
| council review 若 challenge round 形同虚设(每个 challenge 都未指向任何 lane),验证会失败。 | `scripts/check_review.py`、`tests/test_semantic_guards.py` |
| 三种 review mode 都有通过 canonical contract 的 golden examples。 | `examples/quick-gate-review.json`、`examples/standard-gate-review.json`、`examples/ux3-council-review.json` |

<!-- ux3-model -->
## 这个 harness 无法强制的事

对边界诚实,因为评估的 agent 一定会实测:

- 它验证 evidence receipt 的格式与内部一致性,不验证真伪。字段看似合理的捏造 receipt 会通过。
- 只有在 review 声明某决策为 human-owned 之后,human-decision 的追踪链才会被强制。把 human-owned 案例误分类为 `none` 的 agent,schema 抓不到。
- 它要求三条 lane review,但无法证明三者是独立完成的。

harness 真正强制的每一项都列在上方,且有测试覆盖。

## UX3 模型

三条 flow 分开审查，再一起解释：

| Flow | 定义 |
|---|---|
| User Flow | 谁使用、谁受影响、他们想完成什么，以及现在有什么成本、摩擦、风险或失控感。 |
| Evidence Flow | 哪个来源、信号、解释、反向信号和 decision impact 支持下一步。 |
| Business Flow | 谁创造价值、获得价值、付款、决策、运营、承担风险，以及交换是否可持续且正当。 |

四个交会面：

| 交会面 | Canonical id | 意义 |
|---|---|---|
| User Flow + Evidence Flow | `user_evidence` | Situated Understanding：区分意见、行为、替代做法、模拟和仍需补强的证据。 |
| Evidence Flow + Business Flow | `evidence_business` | Viable Learning：把信号连到商业后果、隐藏成本、留存和失败条件。 |
| User Flow + Business Flow | `user_business` | Sustainable Value Exchange：比较用户获得什么、付出什么、business 捕捉什么，以及交换是否公平。 |
| Center | `ux3_decision_kernel` | UX3 Decision Kernel：Validate、Reduce、Gate、Emit 一个有边界的结果。 |

UX3 Decision Kernel 不平均各审查线分数，也不制造第四种意见。它验证
contract、收敛到最严重的判断、处理不确定性与人类负责的判断，
然后产出 canonical review result。

<!-- review-modes -->
## Review 模式

所有 review 从 `prompts/start-review.md` 开始，选择最小但负责任的模式。

| Mode | 使用时机 |
|---|---|
| Quick Gate | 小型、可逆、低风险变更。 |
| Standard Gate | 新功能、workflow 或 experiment。 |
| UX3 Council | 高 uncertainty、外部证据、重大风险、多 reviewer，或 human-owned trade-off。 |

六个 gates 是 Stage、User Flow、Evidence Flow、Business Flow、Council、Human Judgment；它们分别检查阶段、用户、证据、商业、审议和人的责任。

<!-- live-coding-quickstart -->
## 安装、验证与 Live Coding 边界

直接安装到支持的 agent 环境：

```text
npx skills add cis2042/product-design-harness -g -y
```

检查并验证完整 repo：

```text
git clone <repo-url> product-design-harness
cd product-design-harness
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/validate.py
.venv/bin/python scripts/check_review.py examples/quick-gate-review.json
```

使用 repo server 预览网站与 UTF-8 文档：

```text
.venv/bin/python scripts/serve.py
```

导入 agent 时，加载 `skills/product-design-harness/SKILL.md`，并保留
同层的 `resources/`；再依次使用 `resources/schemas/session-config.schema.json`、
`resources/knowledge/ontology.json`、`resources/knowledge/rules.json`、
`resources/prompts/start-review.md`。所有输出都要用
`resources/schemas/review-result.schema.json` 验证。

Live-coding handoff boundary：review 不是 implementation。`verify`
只授权 exact proof step；`continue` 加上有效的
`templates/context-pack.md` 才授权在 execution boundary 内实现；
`stop_reframe` 会阻止实现并要求重写产品问题。

<!-- working-language -->
## 工作语言

阅读语言和工作语言是两件事。`working_language` 控制人类可读的 prompt、
问题、解释、摘要和 free-text output fields。

它不翻译 JSON property names、enum values、rule IDs、schema IDs、file
paths、evidence IDs，或 canonical verdicts：`continue`、`verify`、
`stop_reframe`。

```json
{
  "working_language": "zh-CN",
  "canonical_identifiers": "en",
  "fallback_language": "en"
}
```

不支持的工作语言要 fallback 到 English。翻译若与英文 kernel 冲突，以英文规则为准。

<!-- canonical-contracts -->
## Canonical contracts

| Path | 用途 |
|---|---|
| `skills/product-design-harness/SKILL.md` | 可安装的 skill entrypoint，包含完整 runtime resources。 |
| `llms.txt` | 机器可读的 repo 索引。 |
| `schemas/session-config.schema.json` | `working_language`、`canonical_identifiers`、`fallback_language`。 |
| `schemas/review-result.schema.json` | `continue`、`verify`、`stop_reframe` 的 canonical review result。 |
| `knowledge/ontology.json` | User Flow、Evidence Flow、Business Flow、intersections 与 human judgment terms。 |
| `knowledge/rules.json` | 21 张 canonical rule cards，包含 `ux3.rule.actor_boundary`。 |
| `knowledge/source-chapters.json` | 教材章节 manifest 与来源 checksum。 |
| `prompts/start-review.md` | Review entry 与 mode selector。 |
| `templates/context-pack.md` | 只有 `continue` 后才创建的 handoff artifact。 |
| `docs/HARNESS.md` | 英文完整 handbook。 |
| `docs/UX3.md` | UX3 model、intersections、UX3 Decision Kernel。 |
| `docs/ADOPTION.md` | 安装与集成指南。 |
| `docs/CONTRACTS.md` | 输出字段与 weakest-flow 逻辑。 |
| `press-kit/PRESS-KIT.md` | 给任何要对外介绍这个 harness 的人:社群字卡与谈话要点。 |

UX3 Product Design Harness 不保证产品成功；它确保每个 build decision 在执行前说明
证据、最弱的 flow、取舍与负责的人类 owner。
