# Revisão semanal 2026-W48 (sexta, 27/11/2026)

Feita pela tarefa agendada do Claude às 11:40 UTC. Fontes: relatório `2026-W48` (gerado localmente às 11:36 UTC,
porque o job de sexta 07:41 ainda não tinha rodado), `execucoes.jsonl`, `data/editais.db`, logs do GitHub Actions e
Gmail (7 dias).

## As 3 coisas que precisam do Bruno (ordem de urgência)

1. **Terceira semana sem nenhum e-mail enviado: falta decidir a LGPD e depois cadastrar os segredos.** No log de 26/11
   os 7 segredos (`SMTP_*`, `EMAIL_FROM`, `LINK_ASSINATURA`, `ASSINANTES_JSON`) continuam em branco, e o job fica verde
   porque `enviar.py` cai em modo ensaio. O que trava é a mesma decisão das semanas W46 e W47: o repo é público e a
   tabela `envios` (hoje com 0 linhas) gravaria o e-mail do assinante em texto puro. Escolha **(a) repo privado** ou
   **(b) hash do e-mail em `envios`** (mudança de código, via PR). Responda "a" ou "b" num dos PRs de revisão e eu
   preparo o resto.
2. **A coleta está ficando lenta e cada vez mais atrasada.** Duração da coleta: 15 → 16 → 11 → 24 → 37 → 33 → **61 min**
   (26/11). O limite do job é 90 min, e semana passada o máximo foi 45. O horário de início também piorou: agendado
   para 06h17, começou entre **13h47 e 18h25** de Brasília (a W47 ficava entre 12h49 e 16h36). Na prática o "alerta das
   06h17" chegaria no fim da tarde. Duas perguntas: (i) posso propor um PR com gatilho externo chamando
   `workflow_dispatch` no horário? (mexe no workflow, só com seu ok); (ii) quer que eu investigue se a API do PNCP
   ficou mais lenta ou se a varredura está paginando demais? Se passar de 90 min o job é cortado e o dia fica sem coleta.
3. **3 PRs de revisão sem resposta (#1 de 13/11, #2 de 20/11, e o desta semana) e a pergunta do filtro "evento"
   continua aberta.** Números desta semana: dos **119** editais novos de eventos/AV, **74 (62%) entram só pela palavra
   "evento"**. Desses, **35** têm termo do ramo (estruturas, tendas, trio elétrico, artistas, áudio, painel) e **39 (33%
   do total)** são ruído: buffet, marmitex, padaria, brinquedos de Natal, medalhas, uniformes, ambulância/UTI,
   bombeiro civil, segurança desarmada, seguro veicular, plano de saúde. A proposta segue a mesma da W47: excluir esses
   termos só quando não houver som/palco/show/telão/estrutura no objeto. Sem feedback de assinante a rotina não abre PR
   de filtro sozinha; diga "sim" e eu abro. Também pode fazer o merge (ou fechar) os PRs #1 e #2 para não acumular.

## Números da semana

| | W47 (20/11) | W48 (27/11) |
| --- | --- | --- |
| Coletas (7d) · com erro | 7 · 0 | 7 · 0 |
| Eventos/AV abertos | 336 | 320 |
| Eventos/AV novos SP / MG | 60 / 77 | 51 / 68 |
| Software/TI abertos | 437 | 349 |
| Software/TI novos SP / MG | 82 / 52 | 69 / 43 |
| E-mails enviados | 0 | 0 |

Novos por dia (todos os nichos): 83 (20/11) · 0 · 0 · 29 · 103 · 88 · 119. Os dois zeros são sábado e domingo depois
do **feriado de 20/11 (Consciência Negra)**: só 1 edital novo tem data de publicação 20/11. Não é falha de coleta.
Semana curta, então todos os nichos caíram um pouco. Eventos/AV ficou em 119 novos (o `negocio.md` previa ~83; a
diferença é o ruído do item 3). Software/TI abertos caíram de novo (437 → 349): 203 encerraram na semana e entraram 112.
Parece a carga inicial de 06/11 se esgotando, não perda de coleta. O número estável deve ficar perto de 300.

## Erros de coleta e o que fazer

- Nenhuma falha nos 7 dias (20/11 a 26/11). O risco agora é tempo (item 2), não erro.
- Continua valendo a sugestão da W46: gravar o erro em `execucoes.jsonl` antes de sair, para que um timeout de 90 min
  apareça no relatório. É mudança de código; só faço com seu ok.
- O relatório de sexta (07:41) também atrasa. Gerei o desta semana localmente e **não** o incluí no PR, para não
  conflitar com o arquivo que o bot vai gravar na `main`.

## O que ficou em rascunho / PR

- Gmail: nenhuma resposta a e-mails "Radar:" nos últimos 7 dias (ninguém recebeu nada ainda). **0 rascunhos.**
- `feedback.md`: sem linhas novas.
- PR desta semana: só esta página (`revisao/2026-W48`). Os PRs #1 (W46) e #2 (W47) continuam abertos.
