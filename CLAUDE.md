# CLAUDE.md — Instruções do Projeto

## Sobre o projeto
`manutencao-api` — API REST para gestão de manutenções de veículos,
desenvolvida como parte da entrega final do módulo de Desenvolvimento
Full Stack Básico (PUC Rio). É o backend de um MVP cujo frontend (SPA)
já existe em repositório separado e consome esta API via HTTP.

O objetivo declarado (`requisitos back-end.md`) é migrar/organizar essa
API para um formato de microserviços, com um repositório GitHub público
por componente. Este repositório é o componente de **backend/API**.

Sem integração com IA no produto final — o Claude Code é usado apenas
como ferramenta de desenvolvimento.

## Stack
- Linguagem: Python 3
- Framework web: Flask (não Django, não FastAPI)
- ORM: Flask-SQLAlchemy + Flask-Migrate (Alembic) para migrations
- Documentação de API: Flasgger (Swagger/OpenAPI), exposta em `/apidocs/`
- CORS: flask-cors (hoje liberado para `*` em todas as rotas — revisar
  antes de produção)
- Banco de dados: SQLite (`manutencao.db`) — não há split dev/prod ainda
- gerenciador de dependências: pip / `requirements.txt`

## Estrutura atual do código
Projeto ainda é um único módulo, sem blueprints nem separação em pacotes:
- `app.py` — toda a aplicação Flask: configuração, inicialização do
  Swagger/CORS/DB e todas as rotas.
- `models.py` — models SQLAlchemy: `Veiculos` e `Itens` (item de
  manutenção, com FK `veiculo` para `Veiculos`). Nomenclatura de
  models/campos em português.
- `database.py` — instância única do `SQLAlchemy()` (`db`), importada
  por `models.py` e `app.py` para evitar import circular.
- Cada model tem um método `to_dict()` manual para serialização — não
  há schema/serializer dedicado (ex: Marshmallow, Pydantic).
- IDs são inteiros autoincrementais (`db.Integer, primary_key=True`),
  usados diretamente nas URLs (`/alterar-item/<int:id>`). Não há
  padrão de identificador público (UUID) neste projeto.

## Rotas existentes hoje
- `GET /recuperar` — retorna todos os veículos e itens cadastrados.
- `POST /salvar-item` — cria item de manutenção.
- `PUT /alterar-item/<id>` — altera item de manutenção.
- `DELETE /deletar-item/<id>` — remove item de manutenção.
- `POST /salvar-veiculo` — cria veículo.
- `PUT /alterar-veiculo/<id>` — altera veículo.
- `DELETE /deletar-veiculo/<id>` — remove veículo.
- `GET /apidocs/` — UI Swagger gerada pelo Flasgger.

Convenção de nomes de rota: verbo em português + entidade, em
kebab-case, sem prefixo `/api` (ex: `/salvar-item`, `/alterar-veiculo/<id>`).
Seguir esse padrão ao adicionar rotas novas, a menos que a spec decida
mudar isso explicitamente (ex: ao introduzir versionamento de API).

## Requisitos do trabalho acadêmico (`requisitos back-end.md`)
Fonte da verdade para o que ainda falta implementar. Resumo do que já
está atendido e do que está pendente:

**Atendido:**
- API REST em Flask com rotas GET, POST, PUT e DELETE.
- Documentação Swagger via Flasgger (`/apidocs/`).

**Pendente / débito técnico conhecido:**
- Dockerfile para o componente (Requisito 3) — não existe ainda.
- Funcionalidades extras além do CRUD básico — autenticação,
  ordenação, filtros, paginação (Requisito 4) — não implementadas.
- Consumo da API externa **BrasilAPI** (brasilapi.com.br) para busca na
  tabela FIPE (Requisito 7) — não implementado. Importante: a resposta
  deve ser tratada e devolvida pela própria API deste projeto, sem
  redirecionar o cliente para a BrasilAPI (Requisito 8).
- Documentar na API/README a licença, cadastro (se necessário) e rotas
  usadas da BrasilAPI (Requisito 8).
- README com fluxograma/imagem da arquitetura da aplicação (Requisito 2)
  — README atual não tem imagem de arquitetura.
- Repositório público próprio no GitHub para este componente, separado
  do frontend (Requisito 10).

Não presumir que um requisito foi implementado sem checar o código —
a lista acima reflete o estado no momento em que este CLAUDE.md foi
escrito e deve ser atualizada conforme os itens forem sendo entregues.

## Fluxo de trabalho obrigatório (Spec-Driven Development)

Antes de implementar qualquer feature não-trivial, siga estas 4 fases.
NÃO pule direto para escrever código.

1. **Explorar** — leia os arquivos relevantes (`app.py`, `models.py`,
   `database.py`) antes de propor qualquer mudança. Não assuma
   estrutura sem confirmar lendo o código.
2. **Especificar (spec)** — escreva um documento curto em
   `docs/specs/AAAA-MM-DD-nome-da-feature.md` descrevendo: o problema,
   o que muda, o que fica de fora do escopo, e decisões de design em
   aberto. Pare aqui e aguarde revisão antes de seguir.
3. **Planejar** — depois que a spec for aprovada, converta em um plano
   de tarefas pequenas e ordenadas, cada uma com arquivo(s) afetado(s)
   e como validar (comando de teste, migration, etc). Pare aqui e
   aguarde revisão antes de seguir.
4. **Implementar** — execute o plano tarefa por tarefa. Rode a
   aplicação e valide manualmente (ou via Swagger) antes de considerar
   uma tarefa concluída.

Use o template em `docs/specs/TEMPLATE.md` para novas specs. Os
comandos `/spec`, `/plan` e `/implementar` (`.claude/commands/`) seguem
essas fases.

## Convenções do projeto
- Models: nomenclatura em português, campos em `snake_case`
  (`intervalo_km`, `ultima_troca_data`). Sem model/mixin abstrato de
  timestamps — declarar campos manualmente quando necessário.
- Migrations: usar Flask-Migrate/Alembic (`flask db migrate` /
  `flask db upgrade`) para qualquer mudança de schema — não editar o
  SQLite diretamente nem recriar `db.create_all()` como forma de migrar
  dados existentes.
- Rotas: manter o padrão de nomenclatura em português já existente
  (verbo + entidade) e documentar toda rota nova com docstring no
  formato Flasgger (bloco YAML após `---`), igual às rotas existentes.
- Tratamento de erros: seguir o padrão já usado — capturar
  `NotFound` do `werkzeug.exceptions` em torno de `.query.get_or_404()`
  e devolver JSON com código de status apropriado (404, 500 em caso de
  violação de FK, etc).
- CORS liberado (`origins: "*"`) é aceitável em desenvolvimento; revisar
  antes de qualquer deploy real.

## Banco de dados
- SQLite local (`manutencao.db`), sem configuração de produção definida ainda. Se um requisito futuro exigir Postgres ou outro SGBD, tratar isso como uma decisão de spec, não como suposição.

## O que NÃO fazer
- Não implementar features fora do escopo da spec aprovada sem avisar.
- Não modificar arquivos de configuração de produção sem confirmação
  explícita (hoje não há esses arquivos, mas a regra vale ao criá-los).
- Não instalar novas dependências sem justificar a escolha.
- Não remover ou reescrever testes existentes para "fazer passar".
- Não redirecionar o cliente para a BrasilAPI ao implementar a busca
  FIPE — os dados devem ser buscados e tratados no backend (Requisito 8).

## Testes e validação
- Não há suíte de testes automatizada nem CI configurado neste projeto
  ainda. Ao adicionar testes, `django.test.TestCase` não se aplica —
  usar `pytest` ou `unittest` padrão do Python, justificando a escolha
  antes de adicionar como dependência nova.
- Antes de finalizar qualquer tarefa: rodar a aplicação localmente
  (`flask run` ou `python app.py`) e validar as rotas afetadas via
  `/apidocs/` ou uma requisição manual (curl/Postman).

## Estado atual / débitos técnicos conhecidos
- Sem Dockerfile (Requisito 3 pendente).
- Sem autenticação, paginação, filtros ou ordenação (Requisito 4
  pendente).
- Sem integração com a BrasilAPI / tabela FIPE (Requisito 7/8 pendente).
- Sem imagem de arquitetura no README (Requisito 2 pendente).
- Sem suíte de testes automatizada.
- CORS aberto para qualquer origem.
