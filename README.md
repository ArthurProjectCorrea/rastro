# Rastro

Registro e consulta confiável do histórico de cada animal de uma criação: de onde veio, por onde passou, o que aconteceu com ele e com quem se relaciona (pais, crias e animais que conviveram com ele).

O contexto completo do produto está em [docs/context.md](docs/context.md).

## Primeiros passos

1. Clone o repositório:

   ```bash
   git clone <url-do-repositorio>
   cd rastro
   ```

2. Instale as dependências (isso também ativa os hooks do Git via Husky):

   ```bash
   npm install
   ```

3. Mude para a branch de desenvolvimento:

   ```bash
   git checkout develop
   ```

4. Siga as instruções de [CONTRIBUTING.md](CONTRIBUTING.md) para contribuir.

## Estrutura

| Caminho           | Descrição                                          |
| ----------------- | -------------------------------------------------- |
| `.claude/`        | Agente, skills e hooks do Claude Code (kit mockup) |
| `docs/`           | Contexto do produto e convenções do mockup         |
| `docs/mockup/`    | Protótipo HTML + CSS + JS + JSON                   |
| `CONTRIBUTING.md` | Guia de contribuição e padrão de commits           |
| `CLAUDE.md`       | Regras para o Claude Code                          |
| `LICENSE`         | Licença MIT                                        |

## Kit de mockup (Claude Code)

Constrói protótipos HTML simples para validar **visual e fluxo** antes de qualquer código de produto. O Claude já conhece os padrões, então você não explica tudo de novo a cada tela.

Requisitos: Claude Code e Python 3.8+ (sem instalar pacotes). Se `python3` não existir (comum no Windows), troque por `python` em `.claude/settings.json` e nos comandos abaixo.

1. Rode `claude` na pasta do projeto.
2. Digite `/new-mockup` (ou `/new-mockup Nome do produto`). Ele faz poucas perguntas, mostra as tabelas e telas que propõe, espera seu ok e só então cria.
3. Para ver: `python3 docs/mockup/serve.py` e abra http://localhost:5173 (não abre por duplo clique: os JSON precisam de servidor).

| Quero                   | Faço                                                            |
| ----------------------- | --------------------------------------------------------------- |
| Nova tela               | `/new-screen lista de animais com filtro por lote`              |
| Várias telas de uma vez | peça ao agente `mockup-builder`                                 |
| Conferir consistência   | `/validate-mockup` ou `python3 .claude/hooks/validate.py --all` |
| Mudar a cara do produto | editar só `docs/mockup/css/tokens.css`                          |

### Como o mockup é organizado

```
docs/
├── context.md            o produto (preenchido pelo /new-mockup, carregado em toda sessão)
├── conventions.md        as regras (fonte única)
├── templates/            telas-molde guardadas após o /new-mockup
└── mockup/
    ├── index.html        índice das telas
    ├── screens.json      registro das telas (a primeira é a entrada do fluxo) e nome do projeto
    ├── css/              tokens.css (único lugar de cores/espaços), base.css, components.css
    ├── js/               app.js (infraestrutura), screens/<id>.js (um por tela)
    ├── data/             schema.json + uma tabela por arquivo (.json), ligadas por <entity>_id
    └── screens/          uma página HTML por tela
```

### O que faz cada peça

- **Skills**: `/new-mockup` (entrevista, contexto, modelagem, criação), `/new-screen` (procedimento de uma tela ligada ao fluxo), `/validate-mockup`.
- **Agente `mockup-builder`**: constrói telas em contexto isolado, com o procedimento da `new-screen` embutido.
- **Hooks** (`.claude/settings.json`):
  - início da sessão: resumo de telas e tabelas existentes;
  - depois de editar arquivo em `docs/mockup/`: confere as regras daquele arquivo (sem `style=`, sem cor fora do `tokens.css`, tabelas conforme o schema...);
  - ao fim do turno: confere o conjunto (chaves estrangeiras, telas registradas, links) e bloqueia **uma vez** se algo estiver quebrado.

### Limites (de propósito)

O mockup não grava dados, não valida regra de negócio e não usa bibliotecas. Botões de "salvar" só mostram um aviso e voltam à lista. Se precisar disso, já é o sistema de verdade.

## Versionamento

Cada commit na `main` gera automaticamente uma nova versão (tag e release no GitHub), seguindo o [Versionamento Semântico](https://semver.org/lang/pt-BR/) calculado a partir dos commits semânticos.

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE).
