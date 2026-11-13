# Revisão semanal 2026-W46 (sexta, 13/11/2026)

Feita pela tarefa agendada do Claude às 11:40 UTC. Fontes: relatório `2026-W46.md`, `execucoes.jsonl`,
execuções do GitHub Actions e caixa do Gmail (últimos 7 dias).

## As 3 coisas que precisam do Bruno (ordem de urgência)

1. **Decidir a LGPD antes de ligar o envio.** O repositório é **público** e `data/editais.db` é versionado.
   A tabela `envios` grava o e-mail do assinante em texto puro, e o workflow faz commit do banco todo dia.
   No primeiro envio real, os e-mails dos assinantes ficam públicos no GitHub. Opções: (a) tornar o repo privado
   (cuidado: Actions privado tem 2.000 min/mês grátis e a coleta já usa 30–60 min/dia, ou seja, 900–1.800 min/mês);
   (b) gravar um hash do e-mail em `envios` em vez do e-mail (mudança de código, via PR). Qual você prefere?
2. **Nenhum e-mail saiu nesta semana: os segredos do GitHub estão vazios.** No log da execução de 12/11, os 7
   segredos (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `EMAIL_FROM`, `LINK_ASSINATURA`,
   `ASSINANTES_JSON`) aparecem em branco (segredo cadastrado aparece como `***`). A chave SMTP `radar-github`
   foi criada na Brevo em 11/11, mas não chegou ao repositório. Cadastre em Settings → Secrets and variables →
   Actions → *Repository secrets* (não em Variables nem em Environment). Sem SMTP, `enviar.py` cai em modo
   ensaio e o job fica verde, por isso nada acusou erro. Faça isso depois de resolver o item 1.
3. **A coleta não roda às 06h17 e já falhou uma vez.** As execuções agendadas começam com 6 a 10 horas de atraso
   (entre 12h39 e 16h50 de Brasília). Hoje, às 08h40 de Brasília, ainda não tinha rodado. Em 10/11 a coleta falhou
   depois de 63 min e o erro não ficou registrado. A promessa de "e-mail às 06h17" não está sendo cumprida.
   Quer que eu proponha um gatilho externo (ex.: um cron chamando `workflow_dispatch`)? Isso mexe no workflow,
   então só faço com o seu ok.

## Números da semana

| | W45 (06/11) | W46 (11/11) | Hoje (13/11, recalculado) |
| --- | --- | --- | --- |
| Coletas registradas (7d) | 1 | 4 | 6 (falha de 10/11 não aparece) |
| Eventos/AV abertos | 311 | 284 | 344 |
| Software/TI abertos | 1.097 | 708 | 659 |
| E-mails enviados | 0 | 0 | 0 |

- A coluna "Novos (7d)" do relatório ainda inclui a carga inicial de 06/11 (1.800 editais) e por isso está inflada.
  Novos de fato desde 07/11: **eventos/AV 90 em SP e 66 em MG**; software/TI 56 em SP e 43 em MG.
- Ritmo diário de novos: 92 · 1 · 54 · (falha) · 177 · 171.

## Erros de coleta e o que fazer

- **10/11:** job falhou no passo "Coletar" após 63 min (o limite é 90). O log não está mais disponível. Como
  `coletar.py` só grava em `execucoes.jsonl` quando termina, o relatório mostra "com erro: 0".
  Sugestão: gravar o erro antes de sair (try/finally) para a falha aparecer no relatório.
- **Duração subindo:** 13 → 14 → 28 → 45 min por rodada. Acompanhar; se passar de 75 min, o timeout de 90 vai cortar.

## Filtros (observação, sem PR)

Não há feedback de assinante (nenhuma resposta a "Radar:" no Gmail), então não abri PR de filtro, como manda a rotina.
Na amostra dos 344 editais de eventos/AV abertos, **111 (~1/3) entram só pela palavra "evento"**, sem termo do ramo:
buffet, kits lanche, troféus, hospedagem, brinquedos, bolos, arbitragem. Para uma locadora de som, isso é ruído.
Proposta para você aprovar: exigir "evento" junto de som/luz/palco/estrutura/show/organização, ou excluir
`buffet|alimenta|lanche|trofeu|medalha|hospedagem|brinquedo`. Se disser sim, abro o PR na próxima revisão.

## O que ficou em rascunho / PR

- Rascunhos no Gmail: **0** (nenhum pedido de suporte, nenhum assinante ativo).
- `feedback.md`: sem linhas novas.
- PR: só com esta página (`revisao/2026-W46`).
