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
  - `README.md` — nova seção com os comandos de `docker build` e
    `docker run` (incluindo o volume para persistir `instance/`),
    para o avaliador subir o backend sem precisar montar o ambiente
    Python local.
- Fluxo principal (build e execução):
  1. `Dockerfile` usa a imagem base `python:3.12-slim` (alinhada à
     versão local, 3.12.3; sem fixar patch version para receber
     atualizações de segurança da imagem).
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
1. ~~Versão exata da imagem base~~ — **Resolvido:** `python:3.12-slim`.
2. ~~Porta do CMD gunicorn~~ — **Resolvido:** manter 5000 (padrão
   Flask, já documentado no README e usado pelo frontend). Se a porta
   5000 do host do avaliador estiver ocupada, isso se resolve no
   mapeamento do `docker run` (`-p <porta-livre>:5000`), sem alterar
   o container nem o frontend.
3. ~~Onde documentar o comando de build/run~~ — **Resolvido:** incluir
   no README já nesta mesma tarefa (`docker build`, `docker run -v ...`).
4. ~~`gunicorn` em `requirements.txt` único vs. `requirements-prod.txt`
   separado~~ — **Resolvido:** manter um único `requirements.txt`,
   consistente com a simplicidade já adotada no projeto (sem split de
   configuração dev/prod) e sem exigir passos extras do avaliador.

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

## Plano de Implementação

1. **Adicionar `gunicorn` a `requirements.txt`**
   - Arquivo(s): `requirements.txt`
   - Mudança: acrescentar a linha `gunicorn==<versão fixada>` (última
     estável compatível com Flask 3.1.2/Python 3.12).
   - Validar: `pip install -r requirements.txt` num venv local não gera
     erro; `python -c "import gunicorn"` funciona.

2. **Criar `.dockerignore`**
   - Arquivo(s): `.dockerignore` (novo, raiz do projeto)
   - Mudança: excluir `.venv/`, `__pycache__/`, `instance/`, `*.db`,
     `.git`, `docs/` do contexto de build.
   - Validar: `docker build .` (após a tarefa 3) não copia esses
     caminhos para dentro da imagem — checar com
     `docker run --rm <imagem> ls -la` que `.venv`/`instance` não
     aparecem.

3. **Criar o `Dockerfile`**
   - Arquivo(s): `Dockerfile` (novo, raiz do projeto)
   - Mudança: imagem base `python:3.12-slim`; copia `requirements.txt`
     e instala dependências antes de copiar o restante do código
     (cache de camada); expõe a porta 5000; `CMD` sobe a aplicação via
     `gunicorn --bind 0.0.0.0:5000 app:app`.
   - Validar: `docker build -t manutencao-api .` completa sem erro.

4. **Validar build e execução local do container**
   - Arquivo(s): nenhum (apenas execução/verificação)
   - Mudança: nenhuma mudança de código — é o checkpoint de validação
     da imagem gerada nas tarefas 1–3.
   - Validar:
     `docker run --rm -p 5000:5000 -v "$(pwd)/instance:/app/instance" manutencao-api`
     e então `curl http://127.0.0.1:5000/recuperar` retorna 200, e
     `http://127.0.0.1:5000/apidocs/` carrega a UI do Swagger.

5. **Validar persistência do SQLite via volume**
   - Arquivo(s): nenhum (apenas execução/verificação)
   - Mudança: nenhuma — checkpoint de validação do critério de aceite
     de persistência.
   - Validar: com o container da tarefa 4 rodando, criar um veículo via
     `POST /salvar-veiculo`; parar o container (`docker stop`); rodar
     de novo com o mesmo volume montado; `GET /recuperar` deve
     continuar retornando o veículo criado.

6. **Documentar Docker no README**
   - Arquivo(s): `README.md`
   - Mudança: nova seção "Como executar com Docker" com os comandos de
     `docker build` e `docker run` (incluindo o `-v` para persistir
     `instance/`), como alternativa ao setup manual com venv já
     documentado.
   - Validar: seguir os comandos exatamente como escritos no README, do
     zero (sem venv ativado), e confirmar que a API sobe e responde —
     esse é o teste que simula o avaliador.

Nenhuma tarefa altera models, então não há migration a gerar nesta
feature.
