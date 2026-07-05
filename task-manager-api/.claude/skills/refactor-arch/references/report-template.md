# Referência — Template do Relatório de Auditoria (Fase 2)

O relatório salvo em `reports/audit-project-N.md` **deve** seguir este formato.
Findings **ordenados por severidade** (CRITICAL → HIGH → MEDIUM → LOW). Cada
finding **precisa** ter arquivo e linha(s) exatos.

````markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <linguagem> + <framework> <versão>
Files:   <N> analyzed | ~<LOC> lines of code
Date:    <YYYY-MM-DD>

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>
Total: <total> findings

## Findings

### [CRITICAL] <Nome do anti-pattern> (<código, ex: C2>)
- **File:** `<arquivo>:<linha ou intervalo>`
- **Description:** <o que foi encontrado, objetivo>
- **Impact:** <consequência concreta>
- **Recommendation:** <como corrigir na Fase 3>

### [HIGH] <Nome do anti-pattern> (<código>)
- **File:** `<arquivo>:<linha>`
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...

### [MEDIUM] <Nome> (<código>)
- **File:** `<arquivo>:<linha>`
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...

### [LOW] <Nome> (<código>)
- **File:** `<arquivo>:<linha>`
- **Description:** ...
- **Impact:** ...
- **Recommendation:** ...

## Deprecated APIs
| API | File:Line | Replace with |
|---|---|---|
| <api> | `<arquivo>:<linha>` | <equivalente moderno> |

## Refactoring plan (preview da Fase 3)
- <resumo das transformações que serão aplicadas, mapeando finding → correção>

================================
Total: <total> findings
================================
````

## Regras de formatação

- Um bloco `###` por finding. Título: `[SEVERIDADE] Nome (código)`.
- Ordem estrita de severidade. Dentro da mesma severidade, agrupe por arquivo.
- O código (`C1`, `H2`, `M3`, `L4`) referencia o `anti-patterns-catalog.md`.
- Sempre inclua a seção **Deprecated APIs** (mesmo que diga "Nenhuma detectada").
- O resumo do topo deve bater com a contagem real dos findings.
- Após salvar o arquivo, imprima no terminal o cabeçalho + `## Summary` e faça a
  pergunta de confirmação da Fase 2.
