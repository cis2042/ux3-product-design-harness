# UX3 Product Design Harness

プロダクトの方向性、実装、ローンチ、フィードバック循環を、機械で検証できる判断にします。

<!-- locale-selector -->
## 読む言語 / 作業する言語

**Read in:** [English](../../README.md) | [繁體中文](../zh-TW/README.md) |
[简体中文](../zh-CN/README.md) | [日本語](README.md) |
[한국어](../ko/README.md) | [Español](../es/README.md) |
[Français](../fr/README.md) | [Deutsch](../de/README.md) |
[Português](../pt/README.md)

**Work in:** この呼び出しを agent session に貼り付けます。

```text
Use UX3 Product Design Harness for this repository.
Working language: ja.
Review this product decision before implementation: <decision>.
```

完全な技術参照は英語が正です：[canonical English README](../../README.md) と
[English handbook](../../docs/HARNESS.md)。

![Product Design Harness 表紙](../../assets/product-design-harness-cover.svg)

UX3 Product Design Harness はプロダクトループの判断レイヤーです。
「なぜ作るのか」から始め、仕様、実装、公開、ユーザーテスト、
フィードバック整理までを扱い、機械で確認できる判定：
`continue`、`verify`、`stop_reframe` を返します。

prompt、JSON Schema、知識ファイル、agent 定義で構成され、特定の framework、
server、SDK に依存しません。人はサイトと handbook、agent は
`skills/product-design-harness/` の完全な bundle を install してから
`llms.txt`、prompts、schemas、rules、golden examples を使い、
どちらも同じ UX3 Decision Kernel と canonical review contract に従います。

<!-- where-it-sits -->
## この Harness の位置

Coding harness はテスト、型、CI で「どう作るか」を守ります。Product Design Harness
は「なぜ作るか」と「作った後にどう判断するか」を守る、ループ全体の判断レイヤーです。

![Product Design Harness の位置](../../assets/process-comparison.svg)

## 自律型マルチ Agent アライメント (Autonomous Multi-Agent Alignment)

マルチ Agent 開発チーム（1 Integrator 統括 + N Workers 実行者 + 1 QC Auditor 独立監査）において、本 harness は機械可読な境界憲法として機能します：
- **Zero-Stall ファストパス (Zero-Stall Fast Path)**：日常的な保守タスク（90%）はレビューゲートを完全バイパスし、待機時間・ブロッキングをゼロにします。
- **1秒未満の System One 判定 (Sub-Second System One Gating)**：`scripts/jev_gate.py` が意図、エビデンス階層、3-lane 裁定を 300ms 未満で評価し、不要な散文を生成しません。
- **無損失コンテキスト保持 (Lossless Context Retention)**：境界ロック（`may_do` と `must_not_do`）により、複数ターンのセッションでも制約事項を完全に維持します。

アーキテクチャ、ロール契約、パイロット検証の詳細は [Multi-Agent Alignment](../../docs/MULTI-AGENT-ALIGNMENT.md) を参照してください。

<!-- why-install -->
## インストールする理由

判定ルールは散文ではなく機械で強制される。形式不正な review、lane の判定と矛盾する combined verdict、may_do と must_not_do に同一項目を持つ execution boundary、evidence tier の権限を超える verdict は、出荷前に検証で弾かれる。

| 主張 | 検証先 |
|---|---|
| 全 mode は 18 schema の一つである `schemas/review-result.schema.json` を共有する。 | `schemas/review-result.schema.json` |
| 作業言語を明示し、canonical identifiers は英語を維持する。 | `schemas/session-config.schema.json` |
| UX3 定義と rule IDs は機械可読ファイルから読み込む。 | `knowledge/ontology.json`、`knowledge/rules.json` |
| 21 decision rule cards が kernel を実行可能にし、六つの新規 rule は章単位の出典を持つ。 | `knowledge/rules.json`、`knowledge/source-chapters.json`、`docs/DECISION-RULES.md` |
| JSON Schema が出力形と verdict 条件を強制する。 | `schemas/review-result.schema.json`、`tests/test_contracts.py` |
| `continue` と `reframed_question` など verdict 固有フィールドは排他的である。 | `tests/test_contracts.py` |
| Challenge round のフィールドは challenge 時に必須、independent 時に禁止される。 | `schemas/reviewer-verdict.schema.json` |
| `stop_reframe` lane には `stop_reason_class` が必須である。 | `schemas/reviewer-verdict.schema.json` |
| actor_boundary.target_population が対象者の唯一の canonical source である。 | `schemas/actor-boundary.schema.json`、`schemas/review-result.schema.json`、`schemas/context-pack.schema.json` |
| `scripts/check_review.py` が worst-verdict、weakest-flow、headline-tier を検査する。 | `scripts/check_review.py`、`docs/CONTRACTS.md`、`tests/test_contracts.py` |
| Evidence receipt は provenance、freshness、counter-signal、`t0`〜`t4` tier を要求する。 | `schemas/evidence.schema.json` |
| review が決定を human-owned と宣言した時点で、decision record id・accountable owner・reversal conditions の双方向追跡が強制される。宣言そのものは審査 agent の判断であり、schema では強制できない。 | `schemas/human-decision.schema.json`、`schemas/review-result.schema.json` |
| verdict は evidence tier に拘束される: headline tier が `t0` なら `stop_reframe` を強制、`t1` は決して `continue` を返せない。 | `scripts/check_review.py`、`tests/test_semantic_guards.py` |
| challenge round が形骸化した council review(すべての challenge がどの lane にも異議を唱えない)は検証に失敗する。 | `scripts/check_review.py`、`tests/test_semantic_guards.py` |
| 三 mode の golden examples が canonical contract を通過する。 | `examples/quick-gate-review.json`、`examples/standard-gate-review.json`、`examples/ux3-council-review.json` |

<!-- ux3-model -->
## この harness が強制できないこと

評価する agent は必ず実際に試すため、境界について正直に:

- evidence receipt の形式と内部整合性を検証するのであって、真実性は検証しない。もっともらしいフィールドを持つ捏造 receipt は通過する。
- human-decision の追跡は、review が決定を human-owned と宣言した後にのみ強制される。human-owned の案件を `none` と誤分類する agent を schema は捕捉できない。
- 3 つの lane review を要求するが、それらが独立して行われたことは証明できない。

harness が実際に強制する項目はすべて上に列挙され、テストで担保されている。

## UX3 モデル

三つの flow を別々にレビューし、最後に合わせて解釈します。

| Flow | 定義 |
|---|---|
| User Flow | 誰が使い、誰が影響を受け、何を達成したいのか。現在のコスト、摩擦、リスク、制御不能感も見る。 |
| Evidence Flow | どの source、signal、interpretation、counter-signal、decision impact が次の一手を支えるのか。 |
| Business Flow | 誰が価値を作り、受け取り、支払い、決め、運用し、リスクを負うのか。交換が持続可能で正当かを見る。 |

四つの交点：

| 交点 | Canonical id | 意味 |
|---|---|---|
| User Flow + Evidence Flow | `user_evidence` | Situated Understanding：意見、行動、回避策、シミュレーション、追加で必要な証拠を分ける。 |
| Evidence Flow + Business Flow | `evidence_business` | Viable Learning：signal を事業上の帰結、隠れたコスト、retention、失敗条件につなげる。 |
| User Flow + Business Flow | `user_business` | Sustainable Value Exchange：user gain、user cost、business capture、公平性を比べる。 |
| Center | `ux3_decision_kernel` | UX3 Decision Kernel：Validate、Reduce、Gate、Emit で境界のある結果を出す。 |

UX3 Decision Kernel は各審査レーンの点数を平均せず、第四の意見も作りません。
contract を検証し、最も厳しい判定に収束し、不確実性と人間が責任を持つ判断を
gate し、canonical review result を出します。

<!-- review-modes -->
## Review モード

すべての review は `prompts/start-review.md` から開始し、最小で責任ある
mode を選びます。

| Mode | 使う場面 |
|---|---|
| Quick Gate | 小さく、可逆で、低リスクの変更。 |
| Standard Gate | 新機能、workflow、experiment。 |
| UX3 Council | 高い uncertainty、外部 evidence、意味のある risk、複数 reviewer、または human-owned trade-off。 |

六つの gate は Stage、User Flow、Evidence Flow、Business Flow、Council、Human Judgment です。段階、ユーザー、証拠、事業、審議、人間の責任を分けて確認します。

<!-- live-coding-quickstart -->
## インストール、検証、Live Coding 境界

対応 agent へ直接インストール：

```text
npx skills add cis2042/ux3-product-design-harness -g -y
```

repo 全体を検査する場合：

```text
git clone <repo-url> product-design-harness
cd product-design-harness
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/validate.py
.venv/bin/python scripts/check_review.py examples/quick-gate-review.json
```

repo server でウェブサイトと UTF-8 ドキュメントをプレビューします：

```text
.venv/bin/python scripts/serve.py
```

agent に接続するときは `skills/product-design-harness/SKILL.md` を読み込み、
同じ階層の `resources/` を保持します。その後
`resources/schemas/session-config.schema.json`、`resources/knowledge/ontology.json`、
`resources/knowledge/rules.json`、`resources/prompts/start-review.md` の順に使います。
すべての出力は `resources/schemas/review-result.schema.json` で検証します。

Live-coding handoff boundary：review は implementation ではありません。
`verify` は exact proof step だけを許可します。`continue` と有効な
`templates/context-pack.md` がそろって初めて execution boundary 内の
implementation が許可されます。`stop_reframe` は実装を止め、よりよいプロダクト問いを返すか要求します。

<!-- working-language -->
## 作業言語

読む言語と作業言語は別です。`working_language` は人間向けの prompt、
質問、説明、要約、free-text output fields を制御します。

翻訳しないもの：JSON property names、enum values、rule IDs、schema IDs、
file paths、evidence IDs、canonical verdicts：`continue`、`verify`、
`stop_reframe`。

```json
{
  "working_language": "ja",
  "canonical_identifiers": "en",
  "fallback_language": "en"
}
```

未対応の作業言語は English に fallback します。翻訳が English kernel と衝突した場合は英語ルールが優先です。

<!-- canonical-contracts -->
## Canonical contracts

| Path | 目的 |
|---|---|
| `skills/product-design-harness/SKILL.md` | 完全な runtime resources を含む installable skill entrypoint。 |
| `llms.txt` | 機械可読の repo index。 |
| `schemas/session-config.schema.json` | `working_language`、`canonical_identifiers`、`fallback_language`。 |
| `schemas/review-result.schema.json` | `continue`、`verify`、`stop_reframe` の canonical review result。 |
| `knowledge/ontology.json` | User Flow、Evidence Flow、Business Flow、intersections、human judgment terms。 |
| `knowledge/rules.json` | `ux3.rule.actor_boundary` を含む 21 の canonical rule cards。 |
| `knowledge/source-chapters.json` | 教材章の manifest と source checksum。 |
| `prompts/start-review.md` | Review entry と mode selector。 |
| `templates/context-pack.md` | `continue` 後だけ作る handoff artifact。 |
| `docs/HARNESS.md` | 英語の完全な handbook。 |
| `docs/UX3.md` | UX3 model、intersections、UX3 Decision Kernel。 |
| `docs/ADOPTION.md` | インストールと統合ガイド。 |
| `docs/CONTRACTS.md` | 出力フィールドと weakest-flow logic。 |
| `press-kit/PRESS-KIT.md` | harness を紹介する人のためのソーシャルカードとトーキングポイント。 |

UX3 Product Design Harness は成功を保証しません。各 build decision が実行前に evidence、
weakest flow、trade-off、責任を持つ human owner を示すことを強制します。
