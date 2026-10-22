# UX3 Product Design Harness

Julgamento de produto verificável por máquina em todo o ciclo: direção, construção, lançamento e feedback dos usuários.

<!-- locale-selector -->
## Idioma de Leitura / Idioma de Trabalho

**Read in:** [English](../../README.md) | [繁體中文](../zh-TW/README.md) |
[简体中文](../zh-CN/README.md) | [日本語](../ja/README.md) |
[한국어](../ko/README.md) | [Español](../es/README.md) |
[Français](../fr/README.md) | [Deutsch](../de/README.md) |
[Português](README.md)

**Work in:** copie esta invocação para a sessão do agente.

```text
Use UX3 Product Design Harness for this repository.
Working language: pt.
Review this product decision before implementation: <decision>.
```

A referência técnica completa permanece na versão em inglês:
[canonical English README](../../README.md) e
[English handbook](../../docs/HARNESS.md).

![Capa do Product Design Harness](../../assets/product-design-harness-cover.svg)

O UX3 Product Design Harness é a camada de julgamento para todo o ciclo de produto.
Ele avalia o primeiro "por que construir isso", acompanha a especificação, a construção, o lançamento, os testes de usuário e a digestão de feedback,
e retorna um veredito verificável por máquina: `continue`, `verify` ou `stop_reframe`.

É independente de framework: prompts, JSON Schemas, arquivos de conhecimento e
definições de agentes conectam-se a qualquer ambiente de execução. Não há servidor nem SDK.
A única dependência é `jsonschema`, usada por `scripts/check_review.py` e `scripts/validate.py` para validar saídas de revisão e contratos do repositório.

As pessoas entram pelo site e manual; os agentes instalam o pacote completo
em `skills/product-design-harness/`, e usam `llms.txt`,
prompts, schemas, regras e exemplos de referência. Ambos compartilham o mesmo
UX3 Decision Kernel e o mesmo contrato canônico.

<!-- where-it-sits -->
## Onde se Posiciona

Coding harnesses tornaram os agentes executores confiáveis: testes, tipos e CI protegem
o como. Nada protegia o porquê ou o depois. Este harness não é uma fase
antes da construção; é a camada de julgamento que opera em todo o ciclo.

![Posição do Product Design Harness](../../assets/process-comparison.svg)

## Alinhamento Autônomo Multi-Agente (Autonomous Multi-Agent Alignment)

Em equipes de desenvolvimento multi-agente (1 Integrator coordenador + N Workers executores + 1 QC Auditor auditor independente), este harness serve como a constituição de limites legível por máquina:
- **Caminho Rápido Sem Bloqueio (Zero-Stall Fast Path)**: Tarefas rotineiras (90%) contornam completamente os gates de revisão, com zero latência e zero bloqueio.
- **Decisão System One em Sub-Segundo (Sub-Second System One Gating)**: `scripts/jev_gate.py` avalia intenção, níveis de evidência e vereditos de 3 vias em menos de 300ms, sem gerar prosa explicativa.
- **Retenção de Contexto Sem Perdas (Lossless Context Retention)**: Bloqueios de limites (`may_do` e `must_not_do`) preservam restrições negativas intactas em sessões extensas de múltiplos turnos.

Consulte [Multi-Agent Alignment](../../docs/MULTI-AGENT-ALIGNMENT.md) para detalhes de arquitetura, contratos de papéis e validações piloto.

<!-- why-install -->
## Por Que Instalar

As regras de decisão são aplicadas por máquina, não por prosa. Uma revisão malformada, um combined verdict que contradiz seus lane verdicts, uma execution boundary cujo may_do repete uma entrada de must_not_do, ou um veredito que ultrapassa seu evidence tier falham na validação antes do envio.

| Afirmação | Onde verificar |
|---|---|
| Um contrato canônico de máquina para todo modo de revisão: `schemas/review-result.schema.json` (JSON Schema draft 2020-12, um dos 18 schemas no repositório). | `schemas/review-result.schema.json` |
| Configuração explícita de idioma de trabalho enquanto identificadores canônicos permanecem em inglês. | `schemas/session-config.schema.json` |
| Definições canônicas de UX3 e rule IDs são carregadas de arquivos legíveis por máquina. | `knowledge/ontology.json`, `knowledge/rules.json` |
| 21 decision rule cards operacionalizam o kernel; seis mantêm proveniência por capítulo, incluindo `ux3.rule.human_agent_interaction` e `ux3.rule.motivation_ethics`. | `knowledge/rules.json`, `knowledge/source-chapters.json`, `docs/DECISION-RULES.md` |
| JSON Schema impõe o formato de saída e campos condicionais específicos de cada veredito. | `schemas/review-result.schema.json`, `tests/test_contracts.py` |
| Campos específicos de cada veredito são mutuamente exclusivos: um resultado `continue` não pode conter `reframed_question`. | `tests/test_contracts.py` |
| Campos de challenge round são proibidos em rodadas independentes e obrigatórios em rodadas de desafio. | `schemas/reviewer-verdict.schema.json` |
| Todo veredito de lane `stop_reframe` deve conter um `stop_reason_class` legível por máquina. | `schemas/reviewer-verdict.schema.json` |
| actor_boundary.target_population é a única fonte canônica da população-alvo em revisões e pacotes de contexto. | `schemas/actor-boundary.schema.json`, `schemas/review-result.schema.json`, `schemas/context-pack.schema.json` |
| `scripts/check_review.py` é o validador canônico obrigatório; ele aplica verificações de worst-verdict, weakest-flow e headline-tier após a validação do JSON Schema. | `scripts/check_review.py`, `docs/CONTRACTS.md`, `tests/test_contracts.py` |
| Recibos de evidência exigem provenance, freshness, counter-signal e um tier de `t0` a `t4`. | `schemas/evidence.schema.json` |
| Uma vez declarada uma decisão human-owned, o rastreamento é imposto em ambas as direções: decision record id, accountable owner e reversal conditions. A declaração em si é critério do agente revisor e não pode ser forçada por schema. | `schemas/human-decision.schema.json`, `schemas/review-result.schema.json` |
| Vereditos são limitados pelo tier de evidência: um headline tier `t0` força `stop_reframe`, e `t1` nunca pode retornar `continue`. | `schemas/review-result.schema.json`, `tests/test_semantic_guards.py` |
| Uma revisão de conselho com uma rodada de desafio vazia (cada desafio não contestando nada) falha na validação. | `scripts/check_review.py`, `tests/test_semantic_guards.py` |
| Exemplos de referência para os três modos validam contra o contrato canônico. | `examples/quick-gate-review.json`, `examples/standard-gate-review.json`, `examples/ux3-council-review.json` |

<!-- ux3-model -->
## O Que o Harness Não Pode Impor

Honestidade sobre os limites, pois agentes avaliadores irão testá-los:

- Valida o formato e a consistência interna dos recibos de evidência, não a veracidade. Um recibo forjado com campos plausíveis passará.
- Aplica o rastreamento de decisão humana apenas após uma revisão declarar a decisão como human-owned. Um agente que classifique incorretamente um caso human-owned como `none` não é capturado pelo schema.
- Exige três revisões de lane, mas não pode provar que foram realizadas de forma independente.

## Modelo UX3

![Modelo UX3](../../assets/ux3-model.svg)

Três fluxos são revisados separadamente e interpretados em conjunto:

| Fluxo | Definição |
|---|---|
| User Flow | Para quem é o produto, quem é impactado, o que tentam realizar e qual custo, atrito, risco ou perda de controle existe agora. |
| Evidence Flow | Qual fonte, sinal, interpretação, sinal contrário e impacto na decisão sustentam o próximo passo. |
| Business Flow | Quem cria valor, recebe valor, paga, decide, opera, absorve risco e se a troca pode permanecer viável e legítima. |

O UX3 opera com máxima força em quatro interseções:

| Interseção | Identificador canônico | Significado |
|---|---|---|
| User Flow + Evidence Flow | `user_evidence` | Entendimento Situado: separar opinião, comportamento, contorno, simulação e provas mais fortes ainda necessárias. |
| Evidence Flow + Business Flow | `evidence_business` | Aprendizado Viável: conectar sinais a consequências de negócios, custos ocultos, retenção e critérios de falha. |
| User Flow + Business Flow | `user_business` | Troca Sustentável de Valor: comparar ganho do usuário, custo do usuário, captura do negócio e justiça. |
| Centro | `ux3_decision_kernel` | UX3 Decision Kernel: Validar, Reduzir, Filtrar e Emitir um resultado delimitado. |

O UX3 Decision Kernel não calcula médias nem inventa uma quarta opinião. Ele valida contratos, reduz ao pior veredito, filtra incertezas e decisões de responsabilidade humana e emite o resultado de revisão canônico. Decisões sob responsabilidade humana são registradas; não são convertidas em pontuação de evidência.

![Interseções UX3](../../assets/intersections.svg)

<!-- review-modes -->
## Modos de Revisão

Inicie cada revisão em `prompts/start-review.md`; ele seleciona o menor modo responsável.

| Modo | Quando usar |
|---|---|
| Quick Gate | Alteração pequena, reversível e de baixo risco. |
| Standard Gate | Nova funcionalidade, fluxo de trabalho ou experimento. |
| UX3 Council | Alta incerteza, evidência externa, risco relevante, múltiplos revisores ou concessão sob julgamento humano. |

Os seis gates são Stage, User Flow, Evidence Flow, Business Flow, Council e Human Judgment. Consulte `docs/OPERATING-PROTOCOL.md`.

<!-- live-coding-quickstart -->
## Instalar, Verificar e Passar o Bastão

Instale a Skill diretamente em ambientes de agentes compatíveis:

```text
npx skills add cis2042/ux3-product-design-harness -g -y
```

Para inspecionar e verificar o repositório completo localmente:

```text
git clone <repo-url> product-design-harness
cd product-design-harness
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/validate.py
.venv/bin/python scripts/check_review.py examples/quick-gate-review.json
```

Visualize o site e a documentação UTF-8 com o servidor do repositório:

```text
.venv/bin/python scripts/serve.py
```

Em seguida, integre ao seu agente:

1. Carregue `skills/product-design-harness/SKILL.md` como skill do harness ou instrução do sistema. Seu diretório `resources/` deve permanecer ao lado.
2. Carregue `resources/schemas/session-config.schema.json`, `resources/knowledge/ontology.json`, `resources/knowledge/rules.json` e `resources/prompts/start-review.md`.
3. Valide cada saída de revisão com `resources/scripts/check_review.py`; o JSON Schema valida formato e condicionais, enquanto `check_review.py` também verifica as regras de weakest-flow e headline-tier.
4. Compare suas primeiras saídas com `resources/examples/quick-gate-review.json`, `resources/examples/standard-gate-review.json` e `resources/examples/ux3-council-review.json`.

Limite de live-coding: revisão e implementação são separadas. `verify` autoriza apenas o passo exato de comprovação. `continue` somado a um `templates/context-pack.md` válido autoriza a implementação dentro do limite de execução delimitado. `stop_reframe` bloqueia a implementação e exige uma melhor pergunta de produto.

<!-- working-language -->
## Idioma de Trabalho

Idioma de leitura e idioma de trabalho são escolhas separadas. `working_language` controla prompts, perguntas, explicações, resumos e campos de saída em texto livre legíveis por humanos.

Não traduz nomes de propriedades JSON, valores de enum, IDs de regras, IDs de schema, caminhos de arquivo, IDs de evidência ou vereditos canônicos: `continue`, `verify`, `stop_reframe`.

A configuração de sessão mantém identificadores de máquina em inglês:

```json
{
  "working_language": "pt",
  "canonical_identifiers": "en",
  "fallback_language": "en"
}
```

Se o idioma solicitado não for suportado, use o inglês e declare o fallback. Se uma tradução entrar em conflito com o kernel em inglês, a regra em inglês prevalece e a tradução é marcada para correção.

<!-- canonical-contracts -->
## Contratos Canônicos

| Caminho | Finalidade |
|---|---|
| `skills/product-design-harness/SKILL.md` | Ponto de entrada instalável da skill; inclui todos os recursos de runtime. |
| `llms.txt` | Índice legível por máquina do repositório. |
| `schemas/session-config.schema.json` | Contrato de idioma de trabalho; `working_language`, `canonical_identifiers` e `fallback_language`. |
| `schemas/review-result.schema.json` | Resultado canônico de revisão para `continue`, `verify` e `stop_reframe`. |
| `knowledge/ontology.json` | Fluxos canônicos de UX3, interseções, atores, stakeholders e termos de julgamento humano. |
| `knowledge/rules.json` | 21 rule cards canônicos, incluindo `ux3.rule.actor_boundary`, com trigger, evidence, counter-signal, human boundary, stop condition e output; cards recém-destilados citam capítulos de origem. |
| `knowledge/source-chapters.json` | Manifesto de capítulos e checksum de origem para a proveniência recém-destilada. |
| `prompts/start-review.md` | Prompt de entrada de revisão e seletor de modo. |
| `templates/context-pack.md` | Artefato de handoff criado apenas após `continue`. |
| `docs/HARNESS.md` | Manual completo em inglês. |
| `docs/UX3.md` | Modelo UX3, interseções e o UX3 Decision Kernel. |
| `docs/ADOPTION.md` | Guia de instalação e integração para equipes de agentes. |
| `docs/CONTRACTS.md` | Campos de saída e lógica de weakest-flow. |
| `press-kit/PRESS-KIT.md` | Cartões para redes sociais e tópicos de discussão para apresentação do harness. |

O UX3 Product Design Harness não promete bons resultados. Ele garante que cada decisão de construção declare sua evidência, seu fluxo mais fraco, suas concessões e seu responsável humano antes do início da execução.
