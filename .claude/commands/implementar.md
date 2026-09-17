---
description: Executa o plano de uma spec já aprovada, tarefa por tarefa
argument-hint: [caminho da spec, ex: docs/specs/2026-07-30-assinaturas.md]
---

Leia a spec e o plano de implementação em "$ARGUMENTS", e o `CLAUDE.md`.

Execute o plano tarefa por tarefa, na ordem. Para cada tarefa:
1. Implemente apenas o que está descrito nela.
2. Rode a validação indicada (testes, `python manage.py check`, etc.).
3. Antes de ir para a próxima tarefa, mostre um resumo curto do que mudou.

Regras:
- Não implemente nada fora do escopo da spec sem avisar primeiro.
- Se uma tarefa exigir uma decisão não prevista no plano, pare e pergunte.
- Ao final de todas as tarefas, rode a suíte de testes completa e resuma o
  que foi entregue.
