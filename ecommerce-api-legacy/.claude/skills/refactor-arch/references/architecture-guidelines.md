# Referência — Guidelines de Arquitetura MVC alvo (Fase 3)

O alvo é **MVC** com camadas de responsabilidade única, aplicável a qualquer
stack. A regra de ouro: **cada camada só conhece a de baixo; a requisição flui
Route → Controller → Service/Model → DB, e a resposta volta pelo mesmo caminho.**

## Estrutura de diretórios alvo

```
src/                      (ou raiz, conforme a convenção da stack)
├── config/               # configuração e segredos (via env), constantes
│   └── settings.*        # lê variáveis de ambiente; NADA hardcoded
├── models/               # acesso a dados / entidades, um por domínio
│   ├── <dominio>_model.* # ex: produto_model, usuario_model
│   └── ...
├── services/             # (opcional) regra de negócio pura e reutilizável
│   └── <dominio>_service.*
├── controllers/          # orquestram request→service/model→response
│   ├── <dominio>_controller.*
│   └── ...
├── views/  ou  routes/   # roteamento: mapeia URL/método → controller
│   └── routes.*
├── middlewares/          # error handler, auth, logging (cross-cutting)
│   └── error_handler.*
└── app.*                 # composition root / entry point
```

> Em APIs sem interface visual, a camada **View** é o **roteamento**
> (`routes/`), que também formata a resposta HTTP (JSON). Isso é MVC aplicado a
> APIs: a "view" é a representação da resposta.

## Responsabilidades por camada

### Model (dados)
- Representa uma entidade e **encapsula o acesso a dados** dela.
- Contém as queries (parametrizadas!) ou o mapeamento ORM.
- **Não** conhece HTTP (nada de `request`/`response`).
- Serialização deve **omitir campos sensíveis** (nunca expor senha).

### Service (regra de negócio) — opcional mas recomendado
- Regra de negócio pura: cálculos, orquestração de múltiplos models,
  validações de domínio, efeitos colaterais (email/notificação) isolados.
- Não conhece HTTP. Recebe dados, devolve dados/erros de domínio.
- É onde vai a lógica que **hoje está inflando os controllers**.

### Controller (orquestração)
- Recebe dados já extraídos da requisição, chama service/model, monta a resposta.
- **Fino**: sem SQL, sem regra de negócio pesada, sem cálculo de desconto.
- Traduz resultado/erro de domínio em status HTTP.

### View / Routes (roteamento)
- Mapeia método+caminho → controller. **Sem lógica de negócio.**
- Faz binding de parâmetros/body e devolve a resposta serializada.

### Middlewares (cross-cutting)
- **Error handler centralizado**: um único ponto que captura exceções e devolve
  o formato de erro padronizado + status correto (substitui os try/except
  repetidos em cada handler).
- Auth, CORS, logging estruturado.

### Config (configuração)
- Toda credencial/segredo vem de **variável de ambiente** com default seguro
  para dev. Nenhum segredo commitado.
- Flags como `DEBUG` controladas por ambiente.
- Constantes de domínio (status válidos, faixas de preço, limites) centralizadas.

### Composition root (entry point)
- Um único `app.*` que: cria o app, lê a config, **conecta as camadas**
  (instancia models/services, injeta nos controllers, registra rotas e o error
  handler) e sobe o servidor. É o único lugar que "sabe" como tudo se liga.

## Princípios SOLID aplicados

- **SRP** — cada arquivo/classe tem uma responsabilidade (o oposto da God Class).
- **OCP** — novos domínios entram como novos módulos, sem reescrever os antigos.
- **DIP** — controllers dependem de abstrações (services/repos injetados), não de
  implementações concretas importadas no meio do código.
- **DRY** — serialização/validação/regra compartilhada vive em um só lugar.

## Regras de preservação (não quebrar o contrato)

- **Mesmos endpoints, métodos e formatos de resposta.** Um cliente existente não
  deve perceber a refatoração.
- Exceção: endpoints que são **findings CRITICAL de segurança** (SQL arbitrário,
  reset destrutivo sem auth) devem ser **removidos ou protegidos** — documente
  a mudança no relatório e no resumo da Fase 3.
- Seeds/dados iniciais e nomes de tabela permanecem, salvo necessidade explícita.

## Adaptação ao nível de organização (calibra a intervenção)

- **Monolito desestruturado** → criar toda a árvore acima e migrar o código.
- **Parcialmente organizado** (já tem `models/`, `routes/`) → **adicionar** o que
  falta (`config/`, `controllers/`, `services/`, `middlewares/`) e mover a regra
  de negócio das rotas para controllers/services. **Não recriar** o que já está
  correto.
