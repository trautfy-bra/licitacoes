# Revisão semanal 2026-W47 (sexta, 20/11/2026)

Feita pela tarefa agendada do Claude às 11:40 UTC. Fontes: relatório `2026-W47` (gerado localmente às 11:36 UTC,
porque o job de sexta 07:41 ainda não tinha rodado), `execucoes.jsonl`, execuções do GitHub Actions e Gmail (7 dias).

## As 3 coisas que precisam do Bruno (ordem de urgência)

1. **Decidir a LGPD: repositório privado ou hash do e-mail.** É a mesma pergunta da semana passada e ainda trava o
   lançamento. O repo é público, `data/editais.db` vai para o GitHub todo dia e a tabela `envios` gravaria o e-mail do
   assinante em texto puro. Hoje ela tem 0 linhas, então nada vazou. Opções: (a) repo privado (o Actions grátis dá
   2.000 min/mês e a coleta usa 20 a 45 min/dia, ou seja, 600 a 1.400 min/mês, cabe mas com pouca folga);
   (b) gravar hash do e-mail em `envios` (mudança de código, via PR). Responda no PR e eu preparo a mudança.
2. **Segunda semana sem nenhum e-mail enviado: os segredos do Actions continuam vazios.** No log de 19/11 os 7 segredos
   (`SMTP_*`, `EMAIL_FROM`, `LINK_ASSINATURA`, `ASSINANTES_JSON`) aparecem em branco, e o job fica verde porque
   `enviar.py` cai em modo ensaio. Cadastre em Settings → Secrets and variables → Actions → *Repository secrets*,
   depois de decidir o item 1.
3. **Responder às 2 perguntas abertas no PR #1 (está sem resposta desde 13/11):**
   - *Filtro "evento":* dos 137 editais novos de eventos/AV na semana, **96 (70%) entram só pela palavra "evento"**.
     Parte é do ramo ("locação de equipamentos para eventos", "produção de eventos"), mas pelo menos **44 são ruído
     claro**: marmitex, lanches, coffee break, buffet, troféus, brinquedos, arbitragem, uniformes, fretamento.
     Proposta: excluir esses termos **só quando não houver** som/palco/show/telão/estrutura no objeto. Uma exclusão
     simples cortaria também 3 editais que têm termo do ramo (ex.: "locação de estruturas para eventos (palcos...)"). Sem feedback de
     assinante a rotina não abre PR de filtro; diga "sim" e eu abro.
   - *Horário:* a coleta agendada para 06h17 começou entre **12h49 e 16h36** de Brasília todos os dias. Quer um gatilho
     externo chamando `workflow_dispatch`? Mexe no workflow, então só com seu ok.

## Números da semana

| | W46 (13/11) | W47 (20/11) |
| --- | --- | --- |
| Coletas (7d) · com erro | 7 · 0 | 7 · 0 |
| Eventos/AV abertos | 348 | 336 |
| Eventos/AV novos SP / MG | 251 / 236* | 60 / 77 |
| Software/TI abertos | 633 | 437 |
| Software/TI novos SP / MG | 513 / 603* | 82 / 52 |
| E-mails enviados | 0 | 0 |

\* W46 ainda contava a carga inicial de 06/11. W47 é a primeira semana "limpa": 137 novos em eventos/AV (acima dos ~83
previstos em `negocio.md`, por causa do ruído do item 3). Novos por dia (todos os nichos): 96 · 54 · 0 (feriado 15/11)
· 47 · 100 · 101 · 120. Software/TI abertos caíram 31% (633 → 437), provavelmente editais encerrando; vale acompanhar.

## Erros de coleta e o que fazer

- Nenhuma falha nos 7 dias (13/11 a 19/11). Duração estável: 20 a 45 min (limite 90). Nada a fazer agora.
- Continua valendo a sugestão da W46: gravar o erro em `execucoes.jsonl` antes de sair, para uma falha como a de 10/11
  aparecer no relatório. É mudança de código; só faço com seu ok.
- O relatório de sexta (07:41) também atrasa como a coleta. Gerei o desta semana localmente e **não** o incluí no PR,
  para não conflitar com o arquivo que o bot vai gravar na `main` mais tarde.

## O que ficou em rascunho / PR

- Gmail: nenhuma resposta a e-mails "Radar:" (nenhum assinante recebeu nada ainda). **0 rascunhos.**
- `feedback.md`: sem linhas novas.
- PR desta semana: só esta página (`revisao/2026-W47`). O PR #1 (W46) continua aberto; pode juntar os dois ou fechar o #1.
