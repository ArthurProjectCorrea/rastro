# Convenções do mockup

Fonte única das regras. O objetivo é um protótipo **simples, rápido e consistente**: validar visual e fluxo, com o mínimo de lógica. O que for regra mecânica é conferido por `python3 .claude/hooks/validate.py --all`.

## 0. Idioma e nomes

- Nomes de arquivos, pastas, ids, classes CSS, chaves JSON, atributos `data-*`, variáveis e comentários de código: **inglês**.
- O que a pessoa lê na tela (títulos, rótulos, botões, mensagens) e os valores dos dados de exemplo: **português (BR)**.

## 1. Estrutura

```
mockup/
├── index.html            índice das telas (lê screens.json)
├── serve.py              servidor local (os JSON não carregam por file://)
├── screens.json          registro: project + lista de screens (id, title, file, menu, description)
├── css/   tokens.css  base.css  components.css
├── js/    app.js  index.js  screens/<id>.js
├── data/  schema.json  <table>.json ...
└── screens/ <id>.html
```

Uma tela = `screens/<id>.html` + (se tiver dados) `js/screens/<id>.js` + uma linha em `screens.json`. `id` em kebab-case (`order-new`) e igual ao `data-screen` do `<body>`.

## 2. HTML

- Estrutura fixa de toda tela: copie uma tela existente (mesmo `<head>`, os 3 CSS, `app.js`, depois o JS da tela).
- `<body data-screen="<id>" data-layout="app|center">`. `app` = menu lateral + topo montados pelo `app.js` (exige sessão). `center` = conteúdo centralizado (login).
- O conteúdo vai em `<main class="content">`. Não escreva menu/topo na mão.
- Proibido: `<style>`, `style="..."`, `onclick=...`, `<script>` com código. Ações simuladas: `data-action="toast" data-message="..." data-goto="other-screen.html"`.
- Links sempre relativos. Passar dado entre telas = querystring (`order.html?id=3`).

## 3. CSS

- Valores visuais (cor, fonte, espaço, raio, sombra) **só em `tokens.css`**. Nos outros arquivos, use `var(--...)`; nunca cor fixa e nunca variável que não exista.
- Reutilize `components.css` antes de criar algo novo. Componentes existentes: `button` (`--primary`, `--danger`), `card`, `page-header`, `table`, `badge` (`--ok|warning|error|neutral`), `field` (`__label`, `__control`, `__help`), `detail`, `empty`, `toast`, `error-banner`. Composição: `stack`, `row`, `grid`, `spacer`, `muted`.
- Componente novo: nome em inglês, estilo BEM simples (`block`, `block__part`, `block--variation`), em `components.css`, só com tokens, sem seletor por id.
- Cartão com conteúdo e título usa `card stack` (o espaçamento interno vem da `stack`); tabela dentro do cartão usa `card card--flush`.
- Mudar a cara do produto = editar `tokens.css`, nunca as telas.

## 4. Dados (JSON como tabelas)

- Cada tabela é `data/<table>.json`: lista de objetos, uma linha por registro. Nome da tabela no plural, snake_case, em inglês.
- Toda tabela declarada em `data/schema.json` com `columns` (`integer`, `number`, `text`, `date` AAAA-MM-DD, `boolean`; sufixo `?` = pode ser `null`) e `fk` (coluna → tabela).
- `id` inteiro, sequencial, nunca reutilizado. Chave estrangeira = `<entity>_id` apontando para o `id` de outra tabela. Sem nomes repetidos no lugar de ids.
- Valores fixos de domínio (status, perfil, tipo) viram **tabela própria** com `name` e, se tiver cor, `tone` (`ok|warning|error|neutral`). `Mock.badge(row)` usa isso.
- Tem que fazer sentido junto: o mesmo cliente aparece nas listas, no detalhe e no formulário. Dados de exemplo realistas e pequenos (3 a 10 linhas por tabela), com textos em português.
- Nunca dados fixos dentro de HTML ou JS.

## 5. Lógica mínima

Permitido: ler tabelas (`Mock.tables`), juntar por id (`Mock.byId`), filtrar, ordenar, contar, ler querystring (`Mock.param`), sessão simulada (`Mock.userId`, `Mock.signIn`), preencher selects (`Mock.options`).
Não permitido: gravar dados, validar regra de negócio, cálculo complexo, autenticação real, bibliotecas externas. Ação que "salva" só mostra aviso e volta (`data-action="toast"`).
`app.js` é só infraestrutura: não recebe regra de negócio nem dados. API: `json, tables, byId, param, esc, currency, date, badge, options, toast, userId, signIn, signOut, ready`.

## 6. Fluxo entre telas

- Toda tela nasce ligada: tem **entrada** (link/botão em outra tela ou item de menu) e **saída** (voltar ou próximo passo). Sem tela órfã, sem link morto.
- A **primeira** tela de `screens.json` é a entrada do fluxo (o índice usa ela no botão "Começar"). Registre o login (ou a tela inicial) primeiro.
- `menu: true` em `screens.json` só para navegação principal. Telas de detalhe/formulário ficam fora do menu.
- Padrão lista → detalhe (`?id=`) → ação/volta; formulário volta para a lista.
- Reaproveite as telas existentes como molde do mesmo tipo (lista, detalhe, formulário, painel) em vez de inventar layout.

## 7. Estados

Toda tela que lista ou busca dados trata o caso vazio (`.empty` com `hidden`). Detalhe com id inexistente mostra "não encontrado".

## 8. Tela pronta quando

1. `validate.py --all` passa.
2. Aberta em `python3 mockup/serve.py`, carrega sem erro no console e sem banner vermelho.
3. Dá para chegar nela e sair dela pelos links.
4. Parece da mesma família das outras (mesmos componentes, mesmos espaçamentos).
