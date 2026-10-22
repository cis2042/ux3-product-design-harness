# UX3 Product Design Harness

Un jugement produit vérifiable par machine pour orienter la direction, la
construction, le lancement et l'apprentissage auprès des utilisateurs.

<!-- locale-selector -->
## Lire en / Travailler en

**Read in:** [English](../../README.md) | [繁體中文](../zh-TW/README.md) |
[简体中文](../zh-CN/README.md) | [日本語](../ja/README.md) |
[한국어](../ko/README.md) | [Español](../es/README.md) |
[Français](README.md) | [Deutsch](../de/README.md) |
[Português](../pt/README.md)

**Work in:** copiez cette invocation dans la session de l'agent.

```text
Use UX3 Product Design Harness for this repository.
Working language: fr.
Review this product decision before implementation: <decision>.
```

La référence technique complète reste la version anglaise :
[canonical English README](../../README.md) et
[English handbook](../../docs/HARNESS.md).

![Couverture Product Design Harness](../../assets/product-design-harness-cover.svg)

UX3 Product Design Harness est la couche de jugement du cycle produit. Elle
évalue le premier "pourquoi construire cela", progresse de la spécification à la construction, au lancement, aux tests utilisateurs et à l'analyse des retours,
puis produit un avis vérifiable : `continue`, `verify` ou `stop_reframe`.

Elle est indépendante du framework : prompts, JSON Schemas, fichiers de connaissance et
définitions d'agents s'intègrent à tout environnement. Aucun serveur ni SDK n'est requis.
Les personnes entrent par le site et le manuel ; les agents installent le bundle
complet `skills/product-design-harness/`, puis utilisent `llms.txt`,
prompts, schemas, règles et exemples de référence. Les deux utilisent le même
UX3 Decision Kernel et le même contrat canonique.

<!-- where-it-sits -->
## Où il se situe

Les coding harnesses sécurisent le comment avec tests, types et CI. Product Design Harness
sécurise le pourquoi et l'après. Ce n'est pas une phase avant le développement, mais la
couche de jugement qui accompagne tout le cycle produit.

![Position du Product Design Harness](../../assets/process-comparison.svg)

## Alignement Autonome Multi-Agents (Autonomous Multi-Agent Alignment)

Au sein des équipes de développement multi-agents (1 Integrator coordinateur + N Workers exécutants + 1 QC Auditor auditeur indépendant), ce harness sert de constitution de limites lisible par machine :
- **Voie Rapide Sans Blocage (Zero-Stall Fast Path)** : Les tâches de routine (90%) contournent entièrement les portes d'évaluation, avec zéro latence et zéro blocage.
- **Décision System One en Moins d'une Seconde (Sub-Second System One Gating)** : `scripts/jev_gate.py` évalue l'intention, les niveaux de preuve et les jugements des trois voies en moins de 300 ms sans générer de prose superflue.
- **Rétention de Contexte Sans Perte (Lossless Context Retention)** : Le verrouillage des limites (`may_do` et `must_not_do`) conserve fidèlement les contraintes négatives sur de longues sessions multi-tours.

Consultez [Multi-Agent Alignment](../../docs/MULTI-AGENT-ALIGNMENT.md) pour découvrir l'architecture, les contrats de rôles et les validations pilotes.

<!-- why-install -->
## Pourquoi l'installer

Les regles de decision sont imposees par la machine, pas par la prose. Une review mal formee, un combined verdict qui contredit ses lane verdicts, une execution boundary dont may_do repete une entree de must_not_do, ou un verdict qui depasse son evidence tier, echouent a la validation avant publication.

| Affirmation | Où la vérifier |
|---|---|
| Tous les modes partagent `schemas/review-result.schema.json`, l'un des 18 JSON Schemas. | `schemas/review-result.schema.json` |
| La langue de travail est explicite et les identifiants canoniques restent en anglais. | `schemas/session-config.schema.json` |
| Les définitions UX3 et rule IDs proviennent de fichiers lisibles par machine. | `knowledge/ontology.json`, `knowledge/rules.json` |
| 21 decision rule cards rendent le kernel opératoire ; six gardent une provenance par chapitre. | `knowledge/rules.json`, `knowledge/source-chapters.json`, `docs/DECISION-RULES.md` |
| JSON Schema impose la forme et les champs conditionnels de chaque verdict. | `schemas/review-result.schema.json`, `tests/test_contracts.py` |
| Les champs propres aux verdicts sont exclusifs ; `continue` interdit `reframed_question`. | `tests/test_contracts.py` |
| Les champs challenge sont requis en challenge round et interdits en independent round. | `schemas/reviewer-verdict.schema.json` |
| Chaque lane `stop_reframe` exige `stop_reason_class`. | `schemas/reviewer-verdict.schema.json` |
| actor_boundary.target_population est l'unique source canonique de la population cible. | `schemas/actor-boundary.schema.json`, `schemas/review-result.schema.json`, `schemas/context-pack.schema.json` |
| `scripts/check_review.py` contrôle worst-verdict, weakest-flow et headline-tier après le Schema. | `scripts/check_review.py`, `docs/CONTRACTS.md`, `tests/test_contracts.py` |
| Un evidence receipt exige provenance, freshness, counter-signal et tier de `t0` à `t4`. | `schemas/evidence.schema.json` |
| Des qu'une review declare une decision human-owned, la trace est imposee dans les deux sens: decision record id, accountable owner et reversal conditions. La declaration elle-meme releve de l'agent examinateur et ne peut pas etre forcee par le schema. | `schemas/human-decision.schema.json`, `schemas/review-result.schema.json` |
| Les verdicts sont bornes par l'"'"'evidence tier: un headline tier `t0` force `stop_reframe`, et `t1` ne peut jamais renvoyer `continue`. | `scripts/check_review.py`, `tests/test_semantic_guards.py` |
| Une council review dont la challenge round est vide (chaque challenge n'"'"'objecte a aucun lane) echoue a la validation. | `scripts/check_review.py`, `tests/test_semantic_guards.py` |
| Les exemples des trois modes valident le contrat canonique. | `examples/quick-gate-review.json`, `examples/standard-gate-review.json`, `examples/ux3-council-review.json` |

<!-- ux3-model -->
## Ce que le harness ne peut pas imposer

Honnetete sur la limite, car les agents evaluateurs la testeront:

- Il valide la forme et la coherence interne des evidence receipts, pas leur verite. Un receipt fabrique avec des champs plausibles passe.
- Il n'impose la chaine human-decision qu'apres qu'une review a declare une decision human-owned. Un agent qui classe a tort un cas human-owned comme `none` n'est pas detecte par le schema.
- Il exige trois lane reviews mais ne peut pas prouver qu'elles ont ete menees independamment.

Tout ce que le harness impose reellement est liste ci-dessus et couvert par des tests.

## Modèle UX3

Trois flux sont examinés séparément puis interprétés ensemble :

| Flow | Définition |
|---|---|
| User Flow | Qui utilise le produit, qui est concerné, ce que ces personnes cherchent à accomplir, et quels coûts, frictions, risques ou pertes de contrôle existent aujourd'hui. |
| Evidence Flow | Quelle source, signal, interprétation, signal contraire et impact sur la décision soutiennent l'étape suivante. |
| Business Flow | Qui crée la valeur, qui la reçoit, qui paie, qui décide, qui opère, qui absorbe le risque, et si l'échange reste viable et légitime. |

Quatre intersections :

| Intersection | Canonical id | Sens |
|---|---|---|
| User Flow + Evidence Flow | `user_evidence` | Situated Understanding : distinguer opinion, comportement, solution de contournement, simulation et preuve encore manquante. |
| Evidence Flow + Business Flow | `evidence_business` | Viable Learning : relier le signal aux conséquences business, aux coûts cachés, à la rétention et aux critères d'échec. |
| User Flow + Business Flow | `user_business` | Sustainable Value Exchange : comparer le gain utilisateur, le coût utilisateur, la capture de valeur par l'entreprise et l'équité de l'échange. |
| Center | `ux3_decision_kernel` | UX3 Decision Kernel : Validate, Reduce, Gate et Emit produisent un résultat borné. |

UX3 Decision Kernel ne fait pas la moyenne des scores de voie et n'invente pas
une quatrième opinion. Il valide les contrats, réduit au verdict le plus
sévère, encadre l'incertitude et les décisions explicitement humaines, puis
émet le résultat de revue canonique.

<!-- review-modes -->
## Modes de revue

Toute revue commence dans `prompts/start-review.md`, qui choisit le plus petit
mode responsable.

| Mode | Quand l'utiliser |
|---|---|
| Quick Gate | Changement limité, réversible et peu risqué. |
| Standard Gate | Nouvelle fonctionnalité, parcours de travail ou expérience. |
| UX3 Council | Forte incertitude, preuve externe, risque significatif, plusieurs relecteurs ou arbitrage relevant d'une personne responsable. |

Les six portes sont Stage, User Flow, Evidence Flow, Business Flow, Council et Human Judgment ; elles séparent étape, utilisateur, preuve, activité, délibération et responsabilité humaine.

<!-- live-coding-quickstart -->
## Installation, vérification et limite de programmation

Installation directe dans les environnements d'agents compatibles :

```text
npx skills add cis2042/ux3-product-design-harness -g -y
```

Pour inspecter et vérifier le repo complet :

```text
git clone <repo-url> product-design-harness
cd product-design-harness
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/validate.py
.venv/bin/python scripts/check_review.py examples/quick-gate-review.json
```

Prévisualisez le site et la documentation UTF-8 avec le serveur du repo :

```text
.venv/bin/python scripts/serve.py
```

Pour le connecter à un agent, chargez `skills/product-design-harness/SKILL.md`
et conservez son répertoire `resources/`, puis utilisez
`resources/schemas/session-config.schema.json`, `resources/knowledge/ontology.json`,
`resources/knowledge/rules.json`, `resources/prompts/start-review.md`. Chaque sortie est validée
avec `resources/schemas/review-result.schema.json`.

Limite de transmission vers la programmation : la revue n'est pas une
implémentation. `verify` n'autorise que l'étape exacte de preuve. `continue`
avec un `templates/context-pack.md` valide autorise l'implémentation dans le
périmètre d'exécution défini. `stop_reframe` bloque l'implémentation et demande
une meilleure question produit.

<!-- working-language -->
## Langue de travail

La langue de lecture et la langue de travail sont séparées. `working_language`
contrôle les consignes, questions, explications, résumés et champs de texte
libre lisibles par des humains.

Ne traduisez pas JSON property names, enum values, rule IDs, schema IDs, file
paths, evidence IDs, ni les verdicts canoniques : `continue`, `verify`,
`stop_reframe`.

```json
{
  "working_language": "fr",
  "canonical_identifiers": "en",
  "fallback_language": "en"
}
```

Si la langue demandée n'est pas prise en charge, utilisez English comme
fallback. Si une traduction contredit le English kernel, la règle anglaise
prévaut.

<!-- canonical-contracts -->
## Canonical contracts

| Path | Usage |
|---|---|
| `skills/product-design-harness/SKILL.md` | Point d'entrée installable avec toutes les ressources d'exécution. |
| `llms.txt` | Index du repo lisible par machine. |
| `schemas/session-config.schema.json` | `working_language`, `canonical_identifiers`, `fallback_language`. |
| `schemas/review-result.schema.json` | Résultat canonique de revue pour `continue`, `verify`, `stop_reframe`. |
| `knowledge/ontology.json` | User Flow, Evidence Flow, Business Flow, intersections et human judgment terms. |
| `knowledge/rules.json` | 21 canonical rule cards, dont `ux3.rule.actor_boundary`. |
| `knowledge/source-chapters.json` | Manifeste des chapitres et checksum de provenance. |
| `prompts/start-review.md` | Entrée de revue et sélecteur de mode. |
| `templates/context-pack.md` | Artefact de transmission créé seulement après `continue`. |
| `docs/HARNESS.md` | Manuel complet en anglais. |
| `docs/UX3.md` | UX3 model, intersections, UX3 Decision Kernel. |
| `docs/ADOPTION.md` | Guide d'installation et d'intégration. |
| `docs/CONTRACTS.md` | Champs de sortie et logique weakest-flow. |
| `press-kit/PRESS-KIT.md` | Cartes sociales et points cles pour presenter le harness. |

UX3 Product Design Harness ne promet pas le succès. Il exige que chaque build decision indique
ses preuves, son flux le plus faible, son arbitrage et son responsable humain avant exécution.
