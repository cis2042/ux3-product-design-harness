# UX3 Product Design Harness

Eine maschinenprüfbare Produktbeurteilung für Richtung, Umsetzung, Einführung
und Lernen aus Nutzerfeedback.

<!-- locale-selector -->
## Lesen in / Arbeiten in

**Read in:** [English](../../README.md) | [繁體中文](../zh-TW/README.md) |
[简体中文](../zh-CN/README.md) | [日本語](../ja/README.md) |
[한국어](../ko/README.md) | [Español](../es/README.md) |
[Français](../fr/README.md) | [Deutsch](README.md) |
[Português](../pt/README.md)

**Work in:** Diese Anweisung in die Agentensitzung kopieren.

```text
Use UX3 Product Design Harness for this repository.
Working language: de.
Review this product decision before implementation: <decision>.
```

Die vollständige technische Referenz bleibt die englische Fassung:
[canonical English README](../../README.md) und
[English handbook](../../docs/HARNESS.md).

![Product Design Harness Titelbild](../../assets/product-design-harness-cover.svg)

UX3 Product Design Harness ist die Beurteilungsschicht im Produktzyklus. Sie
prüft das erste "warum bauen", begleitet von der Spezifikation über die Umsetzung, die Einführung, Nutzertests und die Auswertung von Rückmeldungen,
und liefert eine maschinenprüfbare Beurteilung: `continue`, `verify` oder
`stop_reframe`.

Sie ist framework-unabhängig: Prompts, JSON Schemas, Wissensdateien und Agentendefinitionen
lassen sich in jede Laufzeit einbinden. Server und SDK sind nicht erforderlich. Menschen
nutzen Website und Handbuch; Agenten installieren das vollständige Bundle
`skills/product-design-harness/` und nutzen dann `llms.txt`, Prompts,
Schemas, Regeln und Referenzbeispiele. Beide folgen demselben UX3 Decision Kernel und Vertrag.

<!-- where-it-sits -->
## Wo es einzuordnen ist

Coding Harnesses sichern mit Tests, Typen und CI das Wie. Product Design Harness sichert
das Warum und das Danach. Es ist keine Phase vor der Umsetzung, sondern die
Beurteilungsschicht über den gesamten Produktzyklus.

![Position des Product Design Harness](../../assets/process-comparison.svg)

## Autonome Multi-Agenten-Ausrichtung (Autonomous Multi-Agent Alignment)

In Multi-Agenten-Entwicklungsteams (1 Integrator Koordinator + N Workers Ausführende + 1 QC Auditor unabhängiger Prüfer) dient dieser Harness als maschinenlesbare Grenzverfassung:
- **Zero-Stall Schnellpfad (Zero-Stall Fast Path)**: Routineaufgaben (90%) umgehen die Prüfgates vollständig, ohne Latenz und ohne Blockieren.
- **Sub-Sekunden System One Entscheidung (Sub-Second System One Gating)**: `scripts/jev_gate.py` bewertet Intention, Evidenzstufen und die drei Spururteile in unter 300 ms, ohne Prosa zu generieren.
- **Verlustfreie Kontexterhaltung (Lossless Context Retention)**: Durch Grenzverriegelungen (`may_do` und `must_not_do`) bleiben negative Einschränkungen auch über lange, mehrstufige Sitzungen vollständig erhalten.

Ausführliche Informationen zu Architektur, Rollenverträgen und Pilotvalidierungen finden Sie unter [Multi-Agent Alignment](../../docs/MULTI-AGENT-ALIGNMENT.md).

<!-- why-install -->
## Warum installieren

Die Entscheidungsregeln werden maschinell erzwungen, nicht durch Prosa. Eine fehlgeformte Review, ein Combined Verdict im Widerspruch zu seinen Lane Verdicts, eine Execution Boundary, deren may_do einen must_not_do-Eintrag wiederholt, oder ein Verdict jenseits seines Evidence Tiers scheitern an der Validierung, bevor sie ausgeliefert werden.

| Aussage | Prüfstelle |
|---|---|
| Alle Modi nutzen `schemas/review-result.schema.json`, eines von 18 JSON Schemas. | `schemas/review-result.schema.json` |
| Die Arbeitssprache ist explizit, kanonische Bezeichner bleiben Englisch. | `schemas/session-config.schema.json` |
| UX3-Definitionen und rule IDs werden aus maschinenlesbaren Dateien geladen. | `knowledge/ontology.json`, `knowledge/rules.json` |
| 21 decision rule cards operationalisieren den Kernel; sechs besitzen Kapitelprovenienz. | `knowledge/rules.json`, `knowledge/source-chapters.json`, `docs/DECISION-RULES.md` |
| JSON Schema erzwingt Form und bedingte Felder jedes Verdicts. | `schemas/review-result.schema.json`, `tests/test_contracts.py` |
| Verdict-spezifische Felder schließen sich aus; `continue` verbietet `reframed_question`. | `tests/test_contracts.py` |
| Challenge-Felder sind in challenge rounds Pflicht und in independent rounds verboten. | `schemas/reviewer-verdict.schema.json` |
| Jede `stop_reframe` lane benötigt `stop_reason_class`. | `schemas/reviewer-verdict.schema.json` |
| actor_boundary.target_population ist die einzige kanonische Quelle der Zielgruppe. | `schemas/actor-boundary.schema.json`, `schemas/review-result.schema.json`, `schemas/context-pack.schema.json` |
| `scripts/check_review.py` prüft worst-verdict, weakest-flow und headline-tier nach dem Schema. | `scripts/check_review.py`, `docs/CONTRACTS.md`, `tests/test_contracts.py` |
| Ein evidence receipt verlangt provenance, freshness, counter-signal und Tier `t0` bis `t4`. | `schemas/evidence.schema.json` |
| Sobald eine Review eine Entscheidung als human-owned deklariert, wird die Spur in beide Richtungen erzwungen: decision record id, accountable owner und reversal conditions. Die Deklaration selbst ist die Einschaetzung des pruefenden Agents und kann nicht per Schema erzwungen werden. | `schemas/human-decision.schema.json`, `schemas/review-result.schema.json` |
| Verdicts sind durch den Evidence Tier begrenzt: ein Headline-Tier `t0` erzwingt `stop_reframe`, und `t1` kann niemals `continue` zurueckgeben. | `scripts/check_review.py`, `tests/test_semantic_guards.py` |
| Eine Council Review mit leerer Challenge Round (kein Challenge widerspricht irgendeinem Lane) besteht die Validierung nicht. | `scripts/check_review.py`, `tests/test_semantic_guards.py` |
| Referenzbeispiele aller drei Modi bestehen den kanonischen Vertrag. | `examples/quick-gate-review.json`, `examples/standard-gate-review.json`, `examples/ux3-council-review.json` |

<!-- ux3-model -->
## Was der Harness nicht erzwingen kann

Ehrlichkeit ueber die Grenze, denn evaluierende Agents werden sie testen:

- Er validiert Form und innere Konsistenz von Evidence Receipts, nicht deren Wahrheit. Ein fabriziertes Receipt mit plausiblen Feldern besteht.
- Er erzwingt die Human-Decision-Kette erst, nachdem eine Review eine Entscheidung als human-owned deklariert hat. Einen Agent, der einen human-owned Fall als `none` fehlklassifiziert, faengt das Schema nicht.
- Er verlangt drei Lane Reviews, kann aber nicht beweisen, dass sie unabhaengig durchgefuehrt wurden.

Alles, was der Harness tatsaechlich erzwingt, steht oben und ist durch Tests abgedeckt.

## UX3 Modell

Drei Flüsse werden getrennt geprüft und gemeinsam interpretiert:

| Flow | Definition |
|---|---|
| User Flow | Wer das Produkt nutzt, wer betroffen ist, was erreicht werden soll und welche Kosten, Reibung, Risiken oder Kontrollverluste heute bestehen. |
| Evidence Flow | Welche Quelle, Signal, Interpretation, Gegensignal und Entscheidungswirkung den nächsten Schritt tragen. |
| Business Flow | Wer Wert schafft, wer Wert erhält, wer zahlt, wer entscheidet, wer betreibt, wer Risiko trägt und ob der Austausch tragfähig und legitim bleibt. |

Vier Schnittpunkte:

| Schnittpunkt | Canonical id | Bedeutung |
|---|---|---|
| User Flow + Evidence Flow | `user_evidence` | Situated Understanding: Meinung, Verhalten, bestehende Umgehung, Simulation und noch fehlende Evidenz trennen. |
| Evidence Flow + Business Flow | `evidence_business` | Viable Learning: Signal mit geschäftlicher Folge, versteckten Kosten, Bindung und Fehlerkriterien verbinden. |
| User Flow + Business Flow | `user_business` | Sustainable Value Exchange: Nutzergewinn, Nutzerkosten, Wertabschöpfung des Geschäfts und Fairness des Austauschs vergleichen. |
| Center | `ux3_decision_kernel` | UX3 Decision Kernel: Validate, Reduce, Gate und Emit erzeugen ein begrenztes Ergebnis. |

UX3 Decision Kernel bildet keinen Durchschnitt aus Spurwertungen und erfindet
keine vierte Meinung. Er validiert Verträge, reduziert auf die strengste
Beurteilung, steuert Unsicherheit und explizit menschliche Entscheidungen und
gibt das kanonische Prüfergebnis aus.

<!-- review-modes -->
## Review-Modi

Jede Prüfung startet in `prompts/start-review.md` und wählt den kleinsten
verantwortbaren Modus.

| Mode | Wann nutzen |
|---|---|
| Quick Gate | Kleine, reversible Änderung mit geringem Risiko. |
| Standard Gate | Neue Funktion, Arbeitsablauf oder Experiment. |
| UX3 Council | Hohe Unsicherheit, externe Evidenz, relevantes Risiko, mehrere Prüfer oder eine Abwägung, die bei einer verantwortlichen Person liegt. |

Die sechs Gates sind Stage, User Flow, Evidence Flow, Business Flow, Council und Human Judgment; sie trennen Phase, Nutzer, Evidenz, Geschäft, Beratung und menschliche Verantwortung.

<!-- live-coding-quickstart -->
## Installation, Prüfung und Programmiergrenze

Direkt in unterstützten Agentenumgebungen installieren:

```text
npx skills add cis2042/product-design-harness -g -y
```

Vollständiges Repo prüfen und validieren:

```text
git clone <repo-url> product-design-harness
cd product-design-harness
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/validate.py
.venv/bin/python scripts/check_review.py examples/quick-gate-review.json
```

Website und UTF-8-Dokumentation mit dem Repo-Server anzeigen:

```text
.venv/bin/python scripts/serve.py
```

Zur Einbindung in einen Agenten zuerst `skills/product-design-harness/SKILL.md`
laden und das zugehörige Verzeichnis `resources/` beibehalten, danach
`resources/schemas/session-config.schema.json`, `resources/knowledge/ontology.json`,
`resources/knowledge/rules.json`, `resources/prompts/start-review.md`. Jede Ausgabe wird mit
`resources/schemas/review-result.schema.json` validiert.

Grenze für die Übergabe an die Programmierung: Die Prüfung ist keine
Implementierung. `verify` erlaubt nur den exakt benannten Prüfschritt.
`continue` plus ein gültiges `templates/context-pack.md` erlaubt
Implementierung innerhalb der definierten Ausführungsgrenze. `stop_reframe`
blockiert die Implementierung und fordert eine bessere Produktfrage.

<!-- working-language -->
## Arbeitssprache

Lesesprache und Arbeitssprache sind getrennte Entscheidungen.
`working_language` steuert für Menschen lesbare Anweisungen, Fragen,
Erklärungen, Zusammenfassungen und Freitextfelder.

Nicht übersetzen: JSON property names, enum values, rule IDs, schema IDs,
file paths, evidence IDs und canonical verdicts: `continue`, `verify`,
`stop_reframe`.

```json
{
  "working_language": "de",
  "canonical_identifiers": "en",
  "fallback_language": "en"
}
```

Wenn die Arbeitssprache nicht unterstützt wird, English als fallback nutzen.
Wenn eine Übersetzung dem English kernel widerspricht, gilt die englische
Regel.

<!-- canonical-contracts -->
## Canonical contracts

| Path | Zweck |
|---|---|
| `skills/product-design-harness/SKILL.md` | Installierbarer Einstiegspunkt mit allen Laufzeitressourcen. |
| `llms.txt` | Maschinenlesbarer Repo-Index. |
| `schemas/session-config.schema.json` | `working_language`, `canonical_identifiers`, `fallback_language`. |
| `schemas/review-result.schema.json` | Kanonisches Prüfergebnis für `continue`, `verify`, `stop_reframe`. |
| `knowledge/ontology.json` | User Flow, Evidence Flow, Business Flow, intersections und human judgment terms. |
| `knowledge/rules.json` | 21 canonical rule cards einschließlich `ux3.rule.actor_boundary`. |
| `knowledge/source-chapters.json` | Kapitelmanifest und Herkunfts-Checksum. |
| `prompts/start-review.md` | Einstieg in die Prüfung und Modusauswahl. |
| `templates/context-pack.md` | Übergabeartefakt, das nur nach `continue` erstellt wird. |
| `docs/HARNESS.md` | Vollständiges englisches Handbuch. |
| `docs/UX3.md` | UX3 model, intersections, UX3 Decision Kernel. |
| `docs/ADOPTION.md` | Installations- und Integrationsanleitung. |
| `docs/CONTRACTS.md` | Ausgabefelder und weakest-flow Logik. |
| `press-kit/PRESS-KIT.md` | Social Cards und Kernbotschaften fuer alle, die den Harness vorstellen. |

UX3 Product Design Harness verspricht keinen Erfolg. Es verlangt vor der Ausführung von jeder
build decision Evidenz, schwächsten Flow, Abwägung und einen verantwortlichen Menschen.
