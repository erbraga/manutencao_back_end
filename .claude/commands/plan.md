---
description: Converte uma spec aprovada em um plano de tarefas pequenas e verificáveis
argument-hint: [caminho da spec, ex: docs/specs/2026-07-30-assinaturas.md]
---

Leia a spec em "$ARGUMENTS" e o `CLAUDE.md` do projeto.

Transforme a spec em um plano de implementação com tarefas pequenas e
ordenadas. Para cada tarefa, indique:
- Arquivo(s) afetado(s)
- O que muda, em uma frase
- Como validar (comando de teste, migration a rodar, etc.)

Regras:
- Não escreva código nesta etapa, apenas o plano.
- Se a spec tiver "Decisões em aberto" não resolvidas, pare e pergunte antes
  de continuar — não assuma a resposta.
- Adicione o plano ao final do próprio arquivo da spec, em uma seção
  "## Plano de Implementação".
- Ao terminar, pare e aguarde minha aprovação antes de implementar.
