# UX3 Product Design Harness

用機器可檢查的方式，替產品方向、建置、上線與回饋迴圈做判斷。

<!-- locale-selector -->
## 閱讀語言 / 工作語言

**Read in:** [English](../../README.md) | [繁體中文](README.md) |
[简体中文](../zh-CN/README.md) | [日本語](../ja/README.md) |
[한국어](../ko/README.md) | [Español](../es/README.md) |
[Français](../fr/README.md) | [Deutsch](../de/README.md) |
[Português](../pt/README.md)

**Work in:** 複製這段到 agent session。

```text
Use UX3 Product Design Harness for this repository.
Working language: zh-TW.
Review this product decision before implementation: <decision>.
```

完整技術參考以英文為準：[canonical English README](../../README.md) 與
[English handbook](../../docs/HARNESS.md)。

![Product Design Harness 封面](../../assets/product-design-harness-cover.svg)

UX3 Product Design Harness 是產品迴圈的判斷層。它不只在建置前問
「為什麼要做」，也一路覆蓋規格、建置、上線、使用者測試與回饋整理，
最後產出機器可檢查的判定：`continue`、
`verify` 或 `stop_reframe`。

它不綁定框架：prompt、JSON Schema、知識檔與 agent 定義可接入任何
agent runtime。它沒有 server 或 SDK；唯一依賴是 `jsonschema`，供
`scripts/check_review.py` 與 `scripts/validate.py` 驗證 review 輸出與 repo 契約。

同一套知識有兩個入口：人類閱讀專案網站與 handbook；agent 安裝
`skills/product-design-harness/` 完整 bundle，再讀取 `llms.txt`、
prompts、schemas、rules 與 golden examples。
兩個入口共用同一個 UX3 Decision Kernel 與 canonical review contract。

<!-- where-it-sits -->
## 它位於哪裡

Coding harness 透過測試、型別與 CI 讓 agent 成為可靠的執行者，保護的是
「怎麼做」。Product Design Harness 保護「為什麼做」與「做完之後如何判斷」。
它不是開發前的一個階段，而是貫穿整個產品迴圈的判斷層。

![Product Design Harness 的位置](../../assets/process-comparison.svg)

## 自主多 Agent 對齊 (Autonomous Multi-Agent Alignment)

在多 Agent 開發團隊（1 Integrator 主控 + N Workers 執行者 + 1 QC Auditor 獨立質檢）中，本 harness 作為機器可讀的邊界憲法：
- **零停滯快速通道 (Zero-Stall Fast Path)**：例行任務（90%）完全繞過審查閘門，零阻塞、零延遲。
- **次秒級 System One 判定 (Sub-Second System One Gating)**：`scripts/jev_gate.py` 在 300ms 內評估意圖、證據等級與三軌裁決，不生成冗長散文。
- **無損上下文記憶保存 (Lossless Context Retention)**：邊界鎖定（`may_do` 與 `must_not_do`）跨多輪對話完整保留負向約束。

詳細架構、角色契約與驗證案例請參閱 [Multi-Agent Alignment](../../docs/MULTI-AGENT-ALIGNMENT.md)。

<!-- why-install -->
## 為什麼安裝

決策規則由機器強制,不是散文。格式錯誤的 review、與 lane 裁決矛盾的 combined verdict、may_do 與 must_not_do 出現同一條目的 execution boundary、或超出 evidence tier 授權的裁決,都會在出貨前被驗證擋下。

| 主張 | 驗證位置 |
|---|---|
| 所有 review mode 共用一份 canonical machine contract：`schemas/review-result.schema.json`；repo 內共有 18 份 JSON Schema。 | `schemas/review-result.schema.json` |
| 工作語言明確設定，canonical identifiers 維持英文。 | `schemas/session-config.schema.json` |
| Canonical UX3 定義與 rule IDs 從機器檔案載入。 | `knowledge/ontology.json`、`knowledge/rules.json` |
| 21 decision rule cards 將 kernel 轉為可執行規則；其中六張保留章節來源，包括 `ux3.rule.human_agent_interaction` 與 `ux3.rule.motivation_ethics`。 | `knowledge/rules.json`、`knowledge/source-chapters.json`、`docs/DECISION-RULES.md` |
| JSON Schema 強制輸出結構與各 verdict 的條件欄位。 | `schemas/review-result.schema.json`、`tests/test_contracts.py` |
| Verdict 專屬欄位互斥；`continue` 不能帶有 `reframed_question`。 | `tests/test_contracts.py` |
| Challenge round 必須有 challenge 欄位；independent round 禁止使用。 | `schemas/reviewer-verdict.schema.json` |
| 每個 `stop_reframe` lane verdict 都必須有可機讀的 `stop_reason_class`。 | `schemas/reviewer-verdict.schema.json` |
| actor_boundary.target_population 是 review 與 context pack 唯一的 canonical 目標族群來源。 | `schemas/actor-boundary.schema.json`、`schemas/review-result.schema.json`、`schemas/context-pack.schema.json` |
| `scripts/check_review.py` 是必要的 canonical validator，Schema 驗證後再檢查 worst-verdict、weakest-flow 與 headline-tier。 | `scripts/check_review.py`、`docs/CONTRACTS.md`、`tests/test_contracts.py` |
| Evidence receipt 必須記錄 provenance、freshness、counter-signal 與 `t0` 到 `t4` 的 tier。 | `schemas/evidence.schema.json` |
| 一旦 review 宣告某決策為 human-owned,追蹤鏈即被雙向強制:decision record id、accountable owner 與 reversal conditions。宣告本身是審查 agent 的判斷,schema 無法強迫。 | `schemas/human-decision.schema.json`、`schemas/review-result.schema.json` |
| 裁決受 evidence tier 約束:headline tier 為 `t0` 時強制 `stop_reframe`,`t1` 永遠不能回傳 `continue`。 | `scripts/check_review.py`、`tests/test_semantic_guards.py` |
| council review 若 challenge round 形同虛設(每個 challenge 都未指向任何 lane),驗證會失敗。 | `scripts/check_review.py`、`tests/test_semantic_guards.py` |
| 三種 review mode 都有通過 canonical contract 的 golden examples。 | `examples/quick-gate-review.json`、`examples/standard-gate-review.json`、`examples/ux3-council-review.json` |

<!-- ux3-model -->
## 這個 harness 無法強制的事

對邊界誠實,因為評估的 agent 一定會實測:

- 它驗證 evidence receipt 的格式與內部一致性,不驗證真偽。欄位看似合理的捏造 receipt 會通過。
- 只有在 review 宣告某決策為 human-owned 之後,human-decision 的追蹤鏈才會被強制。把 human-owned 案例誤分類為 `none` 的 agent,schema 抓不到。
- 它要求三條 lane review,但無法證明三者是獨立完成的。

harness 真正強制的每一項都列在上方,且有測試覆蓋。

## UX3 模型

三條 flow 分開審查，再一起解讀：

| Flow | 定義 |
|---|---|
| User Flow | 誰使用、誰受影響、他們想完成什麼，以及現在有什麼成本、摩擦、風險或失控感。 |
| Evidence Flow | 哪個來源、訊號、解讀、反向訊號與 decision impact 支持下一步。 |
| Business Flow | 誰創造價值、取得價值、付款、決策、營運、承擔風險，以及交換是否可持續且正當。 |

四個交會面：

| 交會面 | Canonical id | 意義 |
|---|---|---|
| User Flow + Evidence Flow | `user_evidence` | Situated Understanding：分清意見、行為、替代做法、模擬與仍需補強的證據。 |
| Evidence Flow + Business Flow | `evidence_business` | Viable Learning：把訊號連到商業後果、隱藏成本、留存與失敗條件。 |
| User Flow + Business Flow | `user_business` | Sustainable Value Exchange：比較使用者得到什麼、付出什麼、business 捕捉什麼，以及交換是否公平。 |
| Center | `ux3_decision_kernel` | UX3 Decision Kernel：Validate、Reduce、Gate、Emit 一個有邊界的結果。 |

UX3 Decision Kernel 不平均各審查線分數，也不創造第四種意見。它驗證
contract、收斂到最嚴重的判定、處理不確定性與人類負責的判斷，
然後產出 canonical review result。

<!-- review-modes -->
## Review 模式

所有 review 從 `prompts/start-review.md` 開始，選擇最小但負責任的模式。

| Mode | 使用時機 |
|---|---|
| Quick Gate | 小型、可逆、低風險變更。 |
| Standard Gate | 新功能、workflow 或 experiment。 |
| UX3 Council | 高 uncertainty、外部證據、重大風險、多 reviewer，或 human-owned trade-off。 |

六個 gates 是 Stage、User Flow、Evidence Flow、Business Flow、Council、Human Judgment；它們分開檢查階段、使用者、證據、商業、審議與人的責任。

<!-- live-coding-quickstart -->
## 安裝、驗證與 Live Coding 邊界

直接安裝到支援的 agent 環境：

```text
npx skills add cis2042/product-design-harness -g -y
```

若要檢查並驗證完整 repo：

```text
git clone <repo-url> product-design-harness
cd product-design-harness
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/validate.py
.venv/bin/python scripts/check_review.py examples/quick-gate-review.json
```

使用 repo server 預覽網站與 UTF-8 文件：

```text
.venv/bin/python scripts/serve.py
```

導入 agent 時：

1. 把 `skills/product-design-harness/SKILL.md` 載入為 harness skill 或 system instruction，並保留同層的 `resources/`。
2. 依序載入 `resources/schemas/session-config.schema.json`、`resources/knowledge/ontology.json`、`resources/knowledge/rules.json`、`resources/prompts/start-review.md`。
3. 每份輸出都用 `resources/scripts/check_review.py` 驗證；JSON Schema 檢查結構與條件，validator 另外檢查 weakest-flow 與 headline-tier。
4. 第一批輸出要和三份 golden review examples 比對。

Live-coding handoff boundary：review 不是 implementation。`verify`
只授權 exact proof step；`continue` 加上有效的
`templates/context-pack.md` 才授權在 execution boundary 內實作；
`stop_reframe` 會阻止實作並要求重寫產品問題。

<!-- working-language -->
## 工作語言

閱讀語言與工作語言是兩件事。`working_language` 控制人類可讀的 prompt、
問題、解釋、摘要與 free-text output fields。

它不翻譯 JSON property names、enum values、rule IDs、schema IDs、file
paths、evidence IDs，或 canonical verdicts：`continue`、`verify`、
`stop_reframe`。

```json
{
  "working_language": "zh-TW",
  "canonical_identifiers": "en",
  "fallback_language": "en"
}
```

不支援的工作語言要 fallback 到 English。翻譯若與英文 kernel 衝突，以英文規則為準。

<!-- canonical-contracts -->
## Canonical contracts

| Path | 用途 |
|---|---|
| `skills/product-design-harness/SKILL.md` | 可安裝的 skill entrypoint，包含完整 runtime resources。 |
| `llms.txt` | 機器可讀的 repo 索引。 |
| `schemas/session-config.schema.json` | `working_language`、`canonical_identifiers`、`fallback_language`。 |
| `schemas/review-result.schema.json` | `continue`、`verify`、`stop_reframe` 的 canonical review result。 |
| `knowledge/ontology.json` | User Flow、Evidence Flow、Business Flow、intersections 與 human judgment terms。 |
| `knowledge/rules.json` | 21 張 canonical rule cards，包含 `ux3.rule.actor_boundary`；每張都有 trigger、evidence、counter-signal、human boundary、stop condition 與 output。 |
| `knowledge/source-chapters.json` | 蒸餾教材的章節 manifest 與來源 checksum。 |
| `prompts/start-review.md` | Review entry 與 mode selector。 |
| `templates/context-pack.md` | 只有 `continue` 後才建立的 handoff artifact。 |
| `docs/HARNESS.md` | 英文完整 handbook。 |
| `docs/UX3.md` | UX3 model、intersections、UX3 Decision Kernel。 |
| `docs/ADOPTION.md` | 安裝與整合指南。 |
| `docs/CONTRACTS.md` | 輸出欄位與 weakest-flow 邏輯。 |
| `press-kit/PRESS-KIT.md` | 給任何要對外介紹這個 harness 的人:社群字卡與談話要點。 |

UX3 Product Design Harness 不保證產品一定成功。它保證每個 build decision 在開始
執行前，都清楚交代證據、最弱的 flow、取捨，以及負責的人類 owner。
