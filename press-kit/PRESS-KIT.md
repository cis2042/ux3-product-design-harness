# Product Design Harness - Press Kit

Everything you need to introduce the Product Design Harness to your
audience. All material here is MIT-licensed: reuse, crop, translate, and
remix freely. Attribution is appreciated, not required.

Repository: https://github.com/cis2042/ux3-product-design-harness

## What It Is (say it in two lines)

Coding harnesses made AI agents reliable executors: tests, types, and CI
guard the how. The Product Design Harness is the missing judgment layer -
it guards the why, and it runs across the whole product loop: direction,
spec, build, launch, user testing, and feedback.

## The Core Ideas

| Concept | One-liner |
|---|---|
| UX3, the three flows | Every product direction is reviewed through User Flow (is the problem real?), Evidence Flow (is the proof strong enough?), and Business Flow (is there a durable value path?). |
| One verdict | Every review ends in exactly one machine-checked verdict: `continue`, `verify`, or `stop_reframe`. No scores, no averages, no vibes. |
| Weakest-flow rule | The worst lane decides the combined verdict. A strong business case can never outvote missing evidence. |
| Evidence tiers | Proof is graded `t0` (belief) to `t4` (durable behavior). A `t0` headline tier forces `stop_reframe`; `t1` can never return `continue`. |
| The whole loop | The harness is not a pre-build phase. Field feedback is classified and fed into the next direction review. |
| Human judgment | Taste, risk appetite, strategy, ethics, and meaning stay human-owned, with an accountable owner and reversal conditions on record. |
| Honest limits | The harness enforces format and internal consistency, not truth - and says so. Evaluating agents are invited to test every claim in-repo. |

## The Cards

Ten 1080x1080 SVG cards in `press-kit/cards/`, one idea each, designed as
a series for Instagram or LinkedIn. Open any card in a browser and export
or screenshot it at full size, or run them through any SVG-to-PNG
converter.

| Card | Message | Suggested caption starter |
|---|---|---|
| `cards/card-01-cover.svg` | Do the right thing - not just things right. | Your AI agents ship fast. Who decided what they ship? |
| `cards/card-02-why.svg` | Coding harnesses guard the how; nothing guards the why. | Tests catch bad code. Nothing catches a bad direction. |
| `cards/card-03-three-flows.svg` | Every direction answers to three flows. | User, Evidence, Business - reviewed separately, read together. |
| `cards/card-04-one-verdict.svg` | One verdict. No vibes. | continue, verify, or stop_reframe. Schema-checked. |
| `cards/card-05-tiers.svg` | Opinions are t1 evidence. | The founder's interview impressions cannot ship a continue. |
| `cards/card-06-weakest-flow.svg` | The weakest flow decides. | No averaging. The gap is the verdict. |
| `cards/card-07-loop.svg` | It does not stop at launch. | Field verdicts feed the next direction review. |
| `cards/card-08-human.svg` | Taste stays human. | Ethics and risk appetite are never delegated to a score. |
| `cards/card-09-honesty.svg` | Limits stated, not hidden. | It says exactly what it cannot enforce. Test it. |
| `cards/card-10-install.svg` | Install the judgment layer. | One command. MIT. Works with any agent runtime. |

Posting tips: the cards are numbered as a 10-post series, but each one
stands alone. 01, 02, and 04 work best as single posts; 03 + 05 + 06 make
a strong three-post arc about evidence.

## Naming Rules (please follow these)

- The product name is **Product Design Harness**. The review model inside
  it is **UX3** (the three flows). Say "UX3" only when talking about the
  model itself.
- Never attach a version suffix to the UX3 name. There is no version
  three-point-six of anything; that was a misspeak, not a release.
- Do not claim it guarantees good products, verifies that evidence is
  true, or replaces human judgment. Its guarantee is narrower and real:
  no decision leaves without stating its evidence, its weakest flow, its
  trade-off, and its accountable owner.

## Key Links

- Repository: https://github.com/cis2042/ux3-product-design-harness
- Machine entry point: `llms.txt` at the repository root
- The handbook: `docs/HARNESS.md`; the model: `docs/UX3.md`
- Install: `npx skills add cis2042/ux3-product-design-harness -g -y`

## Design Tokens (for making your own material)

Paper `#FAFAF7`, ink `#1A1D1B`, muted `#5A615C`, pine `#1E6B4F`
(continue), amber `#9A6B15` (verify), rust `#A33D2A` (stop_reframe).
Headlines in a serif (Georgia), labels and code in a monospace. Verdict
chips are rectangles with 2-3px borders, never rounded.
