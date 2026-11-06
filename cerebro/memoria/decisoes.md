# Decisões

Registro em ordem cronológica, mais recente no fim. Uma linha por decisão: data, decisão, motivo.

- 2026-11-05 — Modelo escolhido: radar de licitações por nicho (custo zero, roda sozinho). Motivo: dados públicos, entrega 100% automatizável, concorrentes provam disposição a pagar.
- 2026-11-05 — Coleta pelo endpoint de busca do portal PNCP; API oficial `/contratacoes/proposta` como plano B. Motivo: a API oficial devolveu 429 com chamadas em sequência.
- 2026-11-05 — Fase 0 sem LLM no produto. IA paga (chave de API) só depois do 1º assinante pagante.
- 2026-11-06 — Nicho inicial: eventos, som e audiovisual em SP e MG (a confirmar pelo Bruno). Software e TI como segundo nicho.
- 2026-11-06 — Acrescentado o "cérebro" (contexto, memória, ação) para reduzir a revisão semanal e melhorar os filtros com o feedback dos assinantes.
- 2026-11-06 — Coleta diária passa a usar a API oficial de consulta do PNCP (`--modo varredura`). Motivo: no GitHub Actions (runner no Chile, rede Microsoft) a busca do portal recusa a conexão; a API oficial responde 200 (~10 s por página). A busca fica só para uso local.
