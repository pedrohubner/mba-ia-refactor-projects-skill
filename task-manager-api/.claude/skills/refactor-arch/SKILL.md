---
name: refactor-arch
description: >-
  Audita e refatora qualquer codebase para o padrão MVC, de forma agnóstica de
  tecnologia (Python/Flask, Node.js/Express, e outros). Executa três fases
  sequenciais — Análise, Auditoria (com relatório e confirmação humana
  obrigatória) e Refatoração validada. Use quando o usuário invocar
  "/refactor-arch", pedir para auditar arquitetura, detectar code smells /
  anti-patterns, ou reestruturar um projeto legado para Model-View-Controller.
---

# refactor-arch — Auditoria e Refatoração Arquitetural

Você é um **arquiteto de software especialista** em auditar projetos legados e
refatorá-los para o padrão **MVC (Model-View-Controller)**. Esta skill é
**agnóstica de tecnologia**: os sinais de detecção e as transformações valem
para qualquer linguagem/framework. Você **descobre** a stack antes de agir —
nunca assume.

Execute **três fases sequenciais**. Nunca pule uma fase. **Nunca modifique
arquivos antes da confirmação humana no fim da Fase 2.**

## Arquivos de referência (leia sob demanda)

| Arquivo | Quando ler |
|---|---|
| `references/project-analysis.md` | Fase 1 — heurísticas de detecção de linguagem, framework, banco e mapeamento de arquitetura |
| `references/anti-patterns-catalog.md` | Fase 2 — catálogo de anti-patterns, sinais de detecção, severidade e APIs deprecated |
| `references/report-template.md` | Fase 2 — formato exato do relatório de auditoria |
| `references/architecture-guidelines.md` | Fase 3 — regras do padrão MVC alvo (responsabilidades de cada camada) |
| `references/refactoring-playbook.md` | Fase 3 — padrões de transformação antes/depois por anti-pattern |

---

## FASE 1 — ANÁLISE DO PROJETO

**Objetivo:** detectar a stack e mapear a arquitetura atual, sem julgar ainda.

1. Leia `references/project-analysis.md`.
2. Liste os arquivos do projeto (ignore `node_modules/`, `.venv/`, `.git/`,
   `__pycache__/`, `dist/`, `build/`, `.claude/`).
3. Detecte, usando as heurísticas do arquivo de referência:
   - **Linguagem** (por extensão + manifesto de dependências)
   - **Framework** e sua **versão** (pelo manifesto: `requirements.txt`,
     `package.json`, etc.)
   - **Dependências** relevantes
   - **Domínio** da aplicação (a partir de nomes de tabelas, rotas, entidades)
   - **Arquitetura atual** (monolítica em N arquivos? camadas parciais?)
   - **Banco de dados** e **tabelas/entidades**
   - **Nº de arquivos-fonte** e **LOC aproximado**
4. Imprima o resumo **exatamente** neste formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework> <versão>
Dependencies:  <deps relevantes>
Domain:        <descrição do domínio>
Architecture:  <descrição da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas/entidades>
================================
```

Depois de imprimir, siga direto para a Fase 2.

---

## FASE 2 — AUDITORIA

**Objetivo:** cruzar o código contra o catálogo de anti-patterns e produzir um
relatório revisável. **Esta fase é read-only.**

1. Leia `references/anti-patterns-catalog.md` e `references/report-template.md`.
2. Percorra **todos** os arquivos-fonte. Para cada anti-pattern do catálogo,
   procure os **sinais de detecção**. Registre cada achado com:
   - **Severidade** (CRITICAL / HIGH / MEDIUM / LOW) conforme o catálogo
   - **Nome** do anti-pattern
   - **Arquivo e linha(s) exatos**
   - **Descrição** objetiva do que foi encontrado
   - **Impacto** concreto
   - **Recomendação** de correção
3. Inclua obrigatoriamente a checagem de **APIs deprecated** (seção própria no
   catálogo).
4. Ordene os findings por severidade: **CRITICAL → HIGH → MEDIUM → LOW**.
5. Gere o relatório **seguindo `references/report-template.md`** e salve em
   `reports/audit-project-N.md` (N = número do projeto; se desconhecido, use o
   nome do diretório). Imprima também o cabeçalho e o resumo no terminal.
6. **PARE e peça confirmação explícita** antes de qualquer edição:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

   - Só avance para a Fase 3 se a resposta for afirmativa (`y`/`sim`).
   - Se `n`, encerre deixando apenas o relatório gerado.

> **Requisito mínimo:** ≥ 5 findings e ≥ 1 CRITICAL ou HIGH. Se não atingir,
> revise o código com mais cuidado antes de apresentar o relatório.

---

## FASE 3 — REFATORAÇÃO

**Objetivo:** reestruturar para MVC eliminando os findings, e **validar** que a
aplicação continua funcionando.

1. Leia `references/architecture-guidelines.md` e
   `references/refactoring-playbook.md`.
2. **Preserve o comportamento externo:** mesmos endpoints, mesmos métodos HTTP,
   mesmos formatos de request/response. Refatoração muda a estrutura interna,
   não o contrato — a menos que um finding CRITICAL de segurança exija (ex:
   remover endpoint de SQL arbitrário; nesse caso, documente a remoção).
3. Crie a estrutura de diretórios MVC descrita nas guidelines
   (`config/`, `models/`, `views/` ou `routes/`, `controllers/`,
   `middlewares/`, e um entry point / composition root claro).
4. Aplique os padrões do playbook para cada anti-pattern encontrado:
   extrair configuração/segredos, quebrar God Class por domínio, mover regra de
   negócio dos controllers para services/models, parametrizar SQL, centralizar
   error handling, eliminar estado global mutável, resolver N+1, trocar APIs
   deprecated, remover código morto/duplicado.
5. **Adapte-se ao contexto:** um monolito de 4 arquivos exige reconstrução
   completa; um projeto já parcialmente em camadas exige melhorias cirúrgicas
   (não recrie o que já está correto). Detecte o nível de organização na Fase 1
   e calibre a intervenção.
6. **VALIDE** o resultado — é obrigatório:
   - A aplicação **inicia sem erros** (faça o boot).
   - **Todos os endpoints originais respondem** (teste com curl/requests os
     principais caminhos: GET de listagem, POST de criação, health, etc.).
   - **Zero anti-patterns remanescentes** dos que foram corrigidos.
7. Imprima o resumo final:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<árvore da nova estrutura>

Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Princípios transversais

- **Descobrir, não presumir.** Sempre reconfirme a stack pelo manifesto.
- **Um finding = uma correção rastreável.** Todo finding do relatório deve ter
  uma transformação correspondente na Fase 3.
- **Segurança primeiro.** Credenciais hardcoded, SQL Injection e endpoints
  perigosos são sempre CRITICAL e devem ser eliminados.
- **Comportamento preservado, estrutura transformada.**
