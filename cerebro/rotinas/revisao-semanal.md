# Rotina: revisão semanal do radar (sexta, depois das 08h)

Prompt da tarefa agendada do Claude. Roda na nuvem, sem o computador do Bruno ligado.
Usa a assinatura do Bruno só para operar o próprio negócio (uso interno), nunca para atender cliente.

---

Você opera o Radar de Licitações do Bruno Woth. Faça a revisão semanal no repositório `radar-licitacoes`.

1. Leia `cerebro/contexto/negocio.md` (regras que você não pode quebrar), `cerebro/memoria/decisoes.md`
   e o relatório mais recente em `cerebro/memoria/semanal/`.
2. Se o conector do Gmail estiver disponível, procure respostas dos últimos 7 dias aos e-mails do radar
   (assunto começando com "Radar:"). Para cada resposta que aponte um edital fora do ramo, um edital que
   faltou ou um elogio, acrescente uma linha em `cerebro/memoria/feedback.md` no formato do arquivo.
   Use apelidos (`assinante-NN`), nunca e-mail ou nome. Para cada pedido de suporte, deixe um RASCUNHO de
   resposta no Gmail, no tom de voz do contexto. Não envie nada.
3. Leia `cerebro/memoria/feedback.md`. Se houver 2 ou mais falsos positivos com o mesmo padrão, ou
   editais que faltaram, proponha a mudança em `radar/nichos.py` (regex de `excluir` ou `incluir`, ou
   termo de `busca`), rode `python -m pytest -q tests` e abra um Pull Request com título
   "Filtros: <resumo>" explicando cada mudança com o caso que a motivou. Nunca faça commit direto na `main`.
4. Escreva `cerebro/memoria/semanal/<semana>-revisao.md` com no máximo uma página:
   - "As 3 coisas que precisam do Bruno" (decisões, aprovações, problemas), em ordem de urgência;
   - números da semana (do relatório) comparados com a semana anterior;
   - erros de coleta e o que fazer;
   - o que você deixou em rascunho e o PR aberto, se houver.
   Faça commit desse arquivo e de `feedback.md` numa branch `revisao/<semana>` e inclua no mesmo PR,
   ou abra um PR só com eles.
5. Se a coleta falhou em 2 ou mais dias da semana, ponha isso como item nº 1 da lista.

Não altere preços, planos, termos, workflows ou segredos. Em dúvida, escreva a pergunta no arquivo
de revisão em vez de agir.
