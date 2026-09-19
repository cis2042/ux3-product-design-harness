# UX3 Product Design Harness

Un juicio de producto verificable por máquina para orientar la dirección, la
construcción, la salida al mercado y el aprendizaje con usuarios.

<!-- locale-selector -->
## Leer en / Trabajar en

**Read in:** [English](../../README.md) | [繁體中文](../zh-TW/README.md) |
[简体中文](../zh-CN/README.md) | [日本語](../ja/README.md) |
[한국어](../ko/README.md) | [Español](README.md) |
[Français](../fr/README.md) | [Deutsch](../de/README.md) |
[Português](../pt/README.md)

**Work in:** copia esta invocación en la sesión del agente.

```text
Use UX3 Product Design Harness for this repository.
Working language: es.
Review this product decision before implementation: <decision>.
```

La referencia técnica completa sigue siendo la versión en inglés:
[canonical English README](../../README.md) y
[English handbook](../../docs/HARNESS.md).

![Portada de Product Design Harness](../../assets/product-design-harness-cover.svg)

UX3 Product Design Harness es la capa de criterio del ciclo de producto. Evalúa
el primer "por qué construir esto", avanza desde la especificación, la construcción, el lanzamiento, las pruebas con usuarios y el análisis de comentarios,
y devuelve un dictamen verificable: `continue`, `verify` o `stop_reframe`.

Es independiente del framework: prompts, JSON Schemas, archivos de conocimiento y
definiciones de agentes se conectan a cualquier entorno. No necesita servidor ni SDK.
Las personas entran por el sitio y el manual; los agentes instalan el bundle
completo `skills/product-design-harness/` y luego usan `llms.txt`,
prompts, schemas, reglas y ejemplos de referencia. Ambos comparten el mismo
UX3 Decision Kernel y el mismo contrato canónico.

<!-- where-it-sits -->
## Dónde se sitúa

Los coding harnesses protegen el cómo con pruebas, tipos y CI. Product Design Harness
protege el porqué y lo que ocurre después. No es una fase previa al desarrollo, sino
la capa de criterio que acompaña todo el ciclo de producto.

![Posición de Product Design Harness](../../assets/process-comparison.svg)

## Alineación Autónoma de Múltiples Agentes (Autonomous Multi-Agent Alignment)

En equipos de desarrollo multiagente (1 Integrator coordinador + N Workers ejecutores + 1 QC Auditor auditor independiente), este harness actúa como la constitución de límites legible por máquina:
- **Vía Rápida Sin Bloqueos (Zero-Stall Fast Path)**: Las tareas rutinarias (90%) omiten completamente las puertas de revisión, con cero latencia y cero bloqueos.
- **Evaluación System One en Menos de un Segundo (Sub-Second System One Gating)**: `scripts/jev_gate.py` evalúa la intención, los niveles de evidencia y los dictámenes de tres carriles en menos de 300 ms sin redactar texto explicativo.
- **Retención de Contexto Sin Pérdidas (Lossless Context Retention)**: El bloqueo de límites (`may_do` y `must_not_do`) conserva las restricciones negativas intactas a lo largo de sesiones extensas de múltiples turnos.

Consulte [Multi-Agent Alignment](../../docs/MULTI-AGENT-ALIGNMENT.md) para conocer la arquitectura, los contratos de roles y las validaciones piloto.

<!-- why-install -->
## Por qué instalarlo

Las reglas de decision se imponen por maquina, no por prosa. Una review mal formada, un combined verdict que contradice sus lane verdicts, una execution boundary cuyo may_do repite una entrada de must_not_do, o un verdict que excede su evidence tier, fallan la validacion antes de publicarse.

| Afirmación | Dónde verificarla |
|---|---|
| Todos los modos comparten `schemas/review-result.schema.json`, uno de los 18 JSON Schemas. | `schemas/review-result.schema.json` |
| El idioma de trabajo es explícito y los identificadores canónicos permanecen en inglés. | `schemas/session-config.schema.json` |
| Las definiciones UX3 y los rule IDs se cargan desde archivos legibles por máquina. | `knowledge/ontology.json`, `knowledge/rules.json` |
| 21 decision rule cards hacen operativo el kernel; seis conservan procedencia por capítulo. | `knowledge/rules.json`, `knowledge/source-chapters.json`, `docs/DECISION-RULES.md` |
| JSON Schema impone la estructura y los campos condicionales de cada verdict. | `schemas/review-result.schema.json`, `tests/test_contracts.py` |
| Los campos de verdict son excluyentes; `continue` no puede incluir `reframed_question`. | `tests/test_contracts.py` |
| Los campos challenge son obligatorios en challenge round y prohibidos en independent round. | `schemas/reviewer-verdict.schema.json` |
| Todo lane `stop_reframe` requiere `stop_reason_class`. | `schemas/reviewer-verdict.schema.json` |
| actor_boundary.target_population es la única fuente canónica de la población objetivo. | `schemas/actor-boundary.schema.json`, `schemas/review-result.schema.json`, `schemas/context-pack.schema.json` |
| `scripts/check_review.py` comprueba worst-verdict, weakest-flow y headline-tier tras el Schema. | `scripts/check_review.py`, `docs/CONTRACTS.md`, `tests/test_contracts.py` |
| Un evidence receipt exige provenance, freshness, counter-signal y tier de `t0` a `t4`. | `schemas/evidence.schema.json` |
| Una vez que una review declara una decision human-owned, la traza se impone en ambas direcciones: decision record id, accountable owner y reversal conditions. La declaracion misma es criterio del agente revisor y el schema no puede forzarla. | `schemas/human-decision.schema.json`, `schemas/review-result.schema.json` |
| Los verdicts estan acotados por el evidence tier: un headline tier `t0` fuerza `stop_reframe`, y `t1` nunca puede devolver `continue`. | `scripts/check_review.py`, `tests/test_semantic_guards.py` |
| Una council review con una challenge round vacia (cada challenge sin objetar a ningun lane) falla la validacion. | `scripts/check_review.py`, `tests/test_semantic_guards.py` |
| Los ejemplos de los tres modos validan contra el contrato canónico. | `examples/quick-gate-review.json`, `examples/standard-gate-review.json`, `examples/ux3-council-review.json` |

<!-- ux3-model -->
## Lo que el harness no puede imponer

Honestidad sobre el limite, porque los agentes evaluadores lo pondran a prueba:

- Valida la forma y la consistencia interna de los evidence receipts, no su veracidad. Un receipt fabricado con campos plausibles pasa.
- Impone la cadena de human-decision solo despues de que una review declara una decision como human-owned. Un agente que clasifica mal un caso human-owned como `none` no es detectado por el schema.
- Exige tres lane reviews pero no puede probar que se realizaron de forma independiente.

Todo lo que el harness si impone esta listado arriba y cubierto por tests.

## Modelo UX3

Tres flujos se revisan por separado y se interpretan en conjunto:

| Flow | Definición |
|---|---|
| User Flow | Quién usa el producto, quién queda afectado, qué intenta lograr y qué coste, fricción, riesgo o pérdida de control existe ahora. |
| Evidence Flow | Qué fuente, señal, interpretación, señal contraria e impacto en la decisión sostienen el siguiente paso. |
| Business Flow | Quién crea valor, quién lo recibe, quién paga, quién decide, quién opera, quién absorbe riesgo y si el intercambio puede seguir siendo viable y legítimo. |

Cuatro intersecciones:

| Intersección | Canonical id | Significado |
|---|---|---|
| User Flow + Evidence Flow | `user_evidence` | Situated Understanding: separa opinión, comportamiento, alternativa ya usada, simulación y la evidencia que todavía falta. |
| Evidence Flow + Business Flow | `evidence_business` | Viable Learning: conecta la señal con consecuencias de negocio, coste oculto, retención y criterios de fallo. |
| User Flow + Business Flow | `user_business` | Sustainable Value Exchange: compara el beneficio del usuario, el coste para el usuario, la captura de valor del negocio y la equidad del intercambio. |
| Center | `ux3_decision_kernel` | UX3 Decision Kernel: Validate, Reduce, Gate y Emit producen un resultado acotado. |

UX3 Decision Kernel no promedia puntuaciones de los carriles ni inventa una
cuarta opinión. Valida los contratos, reduce al dictamen más severo, gestiona
la incertidumbre y las decisiones humanas explícitas, y emite el resultado
canónico de revisión.

<!-- review-modes -->
## Modos de revisión

Toda revisión empieza en `prompts/start-review.md`, que selecciona el modo
responsable más pequeño.

| Mode | Cuándo usarlo |
|---|---|
| Quick Gate | Cambio pequeño, reversible y de bajo riesgo. |
| Standard Gate | Nueva funcionalidad, flujo de trabajo o experimento. |
| UX3 Council | Alta incertidumbre, evidencia externa, riesgo relevante, varios revisores o una compensación que pertenece a una persona responsable. |

Las seis puertas son Stage, User Flow, Evidence Flow, Business Flow, Council y Human Judgment; juntas separan etapa, usuario, evidencia, negocio, deliberación y responsabilidad humana.

<!-- live-coding-quickstart -->
## Instalación, verificación y límite de programación

Instalación directa en entornos de agentes compatibles:

```text
npx skills add cis2042/product-design-harness -g -y
```

Para inspeccionar y verificar el repo completo:

```text
git clone <repo-url> product-design-harness
cd product-design-harness
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/validate.py
.venv/bin/python scripts/check_review.py examples/quick-gate-review.json
```

Previsualice el sitio y la documentación UTF-8 con el servidor del repo:

```text
.venv/bin/python scripts/serve.py
```

Para conectarlo a un agente, carga `skills/product-design-harness/SKILL.md`
y conserva su directorio `resources/`; después usa
`resources/schemas/session-config.schema.json`, `resources/knowledge/ontology.json`,
`resources/knowledge/rules.json`, `resources/prompts/start-review.md`. Cada salida se valida con
`resources/schemas/review-result.schema.json`.

Límite de entrega para programación: la revisión no es implementación.
`verify` autoriza solo el paso exacto de prueba. `continue` más un
`templates/context-pack.md` válido autoriza implementar dentro del límite de
ejecución definido. `stop_reframe` bloquea la implementación y pide una mejor
pregunta de producto.

<!-- working-language -->
## Idioma de trabajo

El idioma de lectura y el idioma de trabajo son opciones distintas.
`working_language` controla indicaciones, preguntas, explicaciones, resúmenes y
campos de texto libre legibles por humanos.

No traduce JSON property names, enum values, rule IDs, schema IDs, file paths,
evidence IDs ni los dictámenes canónicos: `continue`, `verify`, `stop_reframe`.

```json
{
  "working_language": "es",
  "canonical_identifiers": "en",
  "fallback_language": "en"
}
```

Si el idioma de trabajo no está soportado, usa English como fallback. Si una
traducción contradice el English kernel, prevalece la regla inglesa.

<!-- canonical-contracts -->
## Canonical contracts

| Path | Uso |
|---|---|
| `skills/product-design-harness/SKILL.md` | Punto de entrada instalable con todos los recursos de ejecución. |
| `llms.txt` | Índice del repo legible por máquina. |
| `schemas/session-config.schema.json` | `working_language`, `canonical_identifiers`, `fallback_language`. |
| `schemas/review-result.schema.json` | Resultado canónico de revisión para `continue`, `verify`, `stop_reframe`. |
| `knowledge/ontology.json` | User Flow, Evidence Flow, Business Flow, intersections y human judgment terms. |
| `knowledge/rules.json` | 21 canonical rule cards, incluido `ux3.rule.actor_boundary`. |
| `knowledge/source-chapters.json` | Manifiesto de capítulos y checksum de procedencia. |
| `prompts/start-review.md` | Entrada de revisión y selector de modo. |
| `templates/context-pack.md` | Artefacto de entrega creado solo después de `continue`. |
| `docs/HARNESS.md` | Manual completo en inglés. |
| `docs/UX3.md` | UX3 model, intersections, UX3 Decision Kernel. |
| `docs/ADOPTION.md` | Guía de instalación e integración. |
| `docs/CONTRACTS.md` | Campos de salida y lógica weakest-flow. |
| `press-kit/PRESS-KIT.md` | Tarjetas sociales y puntos clave para quien presente el harness. |

UX3 Product Design Harness no promete buenos resultados. Exige que cada build decision declare
su evidencia, flujo más débil, trade-off y responsable humano antes de ejecutarse.
