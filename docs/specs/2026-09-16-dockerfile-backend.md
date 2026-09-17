# Dockerfile para o backend (manutencao-api) — Spec

**Criado em:** 2026-09-16
**Status:** Rascunho

## Problema
O projeto não possui nenhum Dockerfile. O Requisito 3 de
`requisitos back-end.md` exige "um Dockerfile para cada componente
desenvolvido com todo o processo de implementação da solução em um
contêiner Docker". Hoje a aplicação só roda via `flask run` ou
`python app.py` (`app.run(debug=True)`) num ambiente virtual local —
não há forma de buildar/rodar este backend em container.

Levantamento do código atual relevante para essa spec:
- `app.py` cria `app = Flask(__name__)` no nível do módulo e configura
  `SQLALCHEMY_DATABASE_URI = 'sqlite:///manutencao.db'` (caminho
  relativo). Na prática, isso resolve para
  `instance/manutencao.db` — confirmado que o arquivo já existe em
  `instance/manutencao.db` (12KB), criado pelo Flask no primeiro
  `db.create_all()`.
- `if __name__ == '__main__': app.run(debug=True)` só roda quando o
  arquivo é executado diretamente; um servidor WSGI como gunicorn pode
  importar `app:app` sem passar por esse bloco.
- `requirements.txt` não tem gunicorn nem nenhum servidor WSGI de
  produção — só Flask + extensões (Flasgger, flask-cors,
  Flask-SQLAlchemy, Flask-Migrate/Alembic).
- Não há `.dockerignore`, `wsgi.py`, nem variáveis de ambiente/config
  lidas de `.env` — toda configuração está hardcoded em `app.py`.
- `.gitignore` já ignora `__pycache__/` e `.venv`.
- Python local é 3.12.3 (sem `.python-version`/`runtime.txt` fixando
  isso hoje).

## Objetivo
Permitir buildar e rodar o backend `manutencao-api` em um container
Docker, de forma reproduzível, usando um servidor WSGI de produção em
vez de `app.run(debug=True)`, atendendo o Requisito 3.

## Fora de escopo
- Dockerfile do frontend/SPA (é um repositório separado, fora deste
  projeto).
- `docker-compose.yml` para orquestrar múltiplos componentes/serviços
  — esta spec cobre só o Dockerfile deste backend.
- Troca de SQLite por outro banco (Postgres etc.) — fica para uma spec
  futura, se necessário.
- Autenticação, paginação, filtros, integração com BrasilAPI/FIPE
  (Requisitos 4, 7, 8) — specs separadas.
- Pipeline de CI/CD que builda a imagem automaticamente.

## Proposta
- Models afetados/criados: nenhum.
- Arquivos novos:
  - `Dockerfile` na raiz do projeto.
  - `.dockerignore` na raiz (excluindo `.venv/`, `__pycache__/`,
    `instance/`, `*.db`, `.git`, `docs/`).
- Arquivos alterados:
  - `requirements.txt` — adicionar `gunicorn` como dependência de
    produção.
- Fluxo principal (build e execução):
  1. `Dockerfile` usa uma imagem base `python:3.12-slim` (alinhada à
     versão local, 3.12.3).
  2. Copia `requirements.txt` primeiro e roda `pip install` (para
     aproveitar cache de camada do Docker antes de copiar o resto do
     código).
  3. Copia o restante do código da aplicação para dentro da imagem.
  4. Expõe a porta 5000 (porta padrão do Flask, já usada no
     desenvolvimento local).
  5. `CMD` roda a aplicação via `gunicorn` apontando para `app:app`,
     em vez de `flask run`/`app.run(debug=True)` (inadequado para
     produção: single-threaded, reloader, debug ligado).
  6. Banco SQLite (`instance/manutencao.db`) persiste via volume
     montado no diretório `instance/` do container, para que os dados
     não se percam ao recriar o container.
- Casos de borda relevantes:
  - Primeira execução do container: `instance/` pode não existir ainda
    dentro do volume — `db.create_all()` (já presente em `app.py`, no
    `with app.app_context()`) precisa continuar rodando no startup
    para criar o schema se o volume estiver vazio.
  - Se o volume não for montado, o banco fica apenas dentro do
    container e se perde ao removê-lo — isso deve ficar documentado
    no README (fora do escopo desta spec, mas relevante como aviso).

## Decisões em aberto
1. **Versão exata da imagem base**: usar `python:3.12-slim` (mais
   próxima da versão local 3.12.3) ou fixar `python:3.12.3-slim`?
2. **Nome/porta do CMD gunicorn**: manter porta 5000 (padrão Flask) ou
   usar 8000 (mais comum em imagens gunicorn)? Isso também afeta o que
   o frontend/SPA espera ao consumir a API.
3. **Onde documentar o comando de build/run** (`docker build`,
   `docker run -v ...`): já incluir no README neste momento, ou tratar
   como tarefa separada do plano desta mesma feature?
4. Confirmar se `gunicorn` pode ser adicionado a `requirements.txt`
   diretamente ou se deve ficar num `requirements-prod.txt` separado
   do ambiente de desenvolvimento local (o projeto hoje só tem um
   único `requirements.txt`).

## Critérios de aceite
- Existe um `Dockerfile` na raiz do projeto que builda com sucesso
  (`docker build .`) sem erros.
- O container, ao rodar (`docker run`), sobe a API respondendo nas
  rotas existentes (ex: `GET /recuperar` retorna 200) e expõe
  `/apidocs/`.
- A aplicação roda via `gunicorn` dentro do container — `app.run(debug=True)`
  não é usado no caminho de execução em container.
- Dados gravados no SQLite sobrevivem a um `docker stop` + `docker run`
  novamente (volume funcionando).
- `.dockerignore` evita copiar `.venv/`, `__pycache__/` e o banco local
  de desenvolvimento para dentro da imagem.
- `requirements.txt` inclui `gunicorn` com versão fixada.

---
*Depois de aprovada, esta spec vira a base do PLANO — não escrever
código antes disso.*
