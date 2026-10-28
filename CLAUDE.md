# Regras do projeto

## Git

- Todo commit deve ser feito na branch `develop`.
- Única exceção: o primeiro commit da `main`, que cria a estrutura mínima do repositório. Depois dele, a `develop` deve ser criada a partir da `main`.
- A `main` só recebe Pull Requests. Nunca faça commit ou push direto nela.
- Todo commit deve seguir o padrão de commits semânticos (Conventional Commits), escrito em inglês. Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Idioma

- Nomes de arquivos e pastas: sempre em **inglês**.
- Conteúdo de agentes, skills, hooks, comentários, variáveis e palavras-chave: sempre em **inglês**.
- Conteúdo de arquivos `.md` (exceto agentes e skills) e de interfaces lidas por humanos: em **português (BR)**.
- Responda ao usuário sempre em português (BR).

## Kit de mockup

Este projeto produz **protótipos HTML simples** (HTML + CSS + JS + JSON) para validar visual e fluxo antes de qualquer código de produto. Não é o sistema final.

### Regras de ouro

1. **Siga as convenções.** Elas estão em `docs/conventions.md` (importado abaixo). Não peça ao usuário para explicar padrões de novo: leia e aplique.
2. **Mínimo de lógica.** O mockup lê JSON, junta, filtra e navega. Nada de gravar dados, regra de negócio ou bibliotecas externas.
3. **Dados coerentes entre telas.** Tudo que aparece em mais de uma tela vem de `mockup/data/*.json` (tabelas declaradas em `schema.json`).
4. **Cada tela nasce ligada às outras** (entrada e saída) e reaproveita componentes de `components.css`. Sem tela com cara diferente das demais.
5. **Contexto antes de tela.** Se `docs/context.md` ainda não foi preenchido, não invente o produto: sugira `/new-mockup`.
6. **Não invente.** O que o usuário não disse fica "não informado" ou vira pergunta; nunca preencha com suposição como se fosse requisito.

### Como trabalhar

- Projeto novo: `/new-mockup`. Tela nova: `/new-screen <o que ela mostra>`. Conferir tudo: `/validate-mockup`.
- Para várias telas independentes, delegue ao agente `mockup-builder`.
- Ver no navegador: `python3 mockup/serve.py` e abrir http://localhost:5173 (precisa de servidor; `file://` não carrega os JSON).
- Os hooks já validam sozinhos: após editar arquivos em `mockup/` (regras de cada arquivo) e ao fim do turno (consistência geral). Se um hook reportar erro, corrija na origem; não desative a regra.

## Contexto e convenções

@docs/context.md
@docs/conventions.md
