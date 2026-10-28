# Guia de contribuição

Obrigado por contribuir! Leia este guia antes de abrir um PR.

## Fluxo de branches

- `main`: branch estável. **Só recebe Pull Requests**, nunca commits diretos.
- `develop`: branch de integração. Todo commit é feito aqui (ou em branches derivadas dela).
- Exceção única: o primeiro commit da `main`, que cria a estrutura mínima do repositório. A `develop` é criada a partir dele.

Fluxo normal:

1. Atualize a `develop` e trabalhe nela (ou em uma branch derivada, como `feat/nome-curto`).
2. Faça commits semânticos.
3. Abra um Pull Request de `develop` para `main`.
4. Ao fazer o merge na `main`, uma nova versão é publicada automaticamente.

## Commits semânticos (obrigatório)

**Sempre** use [Conventional Commits](https://www.conventionalcommits.org/pt-br/). O formato é:

```
<tipo>(<escopo opcional>): <descrição curta no imperativo>

<corpo opcional>

<rodapé opcional>
```

A mensagem de commit deve ser escrita em inglês.

| Tipo       | Quando usar                                  | Efeito na versão |
| ---------- | -------------------------------------------- | ---------------- |
| `feat`     | Nova funcionalidade                          | minor            |
| `fix`      | Correção de bug                              | patch            |
| `perf`     | Melhoria de desempenho                       | patch            |
| `docs`     | Mudanças apenas na documentação              | nenhum           |
| `style`    | Formatação, sem mudança de lógica            | nenhum           |
| `refactor` | Refatoração sem mudar comportamento          | nenhum           |
| `test`     | Adição ou ajuste de testes                   | nenhum           |
| `build`    | Mudanças no build ou dependências            | nenhum           |
| `ci`       | Mudanças em pipelines de CI/CD               | nenhum           |
| `chore`    | Tarefas gerais que não alteram código de uso | nenhum           |

Mudança incompatível (_breaking change_): adicione `!` após o tipo (`feat!: ...`) ou o rodapé `BREAKING CHANGE: ...`. Isso gera uma versão **major**.

Exemplos:

```
feat(auth): add login with email
fix(api): handle empty response body
docs: update getting started section
feat!: remove legacy endpoint
```

## Hooks do Git (Husky)

Após `npm install`, os hooks ficam ativos automaticamente:

- `pre-commit`: formata os arquivos em stage com o Prettier (via lint-staged).
- `commit-msg`: valida a mensagem com o commitlint. Commits fora do padrão semântico são rejeitados.

## Convenção de nomes e idioma

- Nomes de arquivos e pastas: sempre em **inglês**.
- Código, variáveis, comentários, palavras-chave, agentes, skills e hooks: sempre em **inglês**.
- Conteúdo de arquivos `.md` e textos de interface lidos por humanos: em **português (BR)**.

## Pull Requests

- O título do PR também segue o padrão de commits semânticos.
- Descreva o que mudou e por quê.
- Mantenha o PR focado em uma única mudança.
