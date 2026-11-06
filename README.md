# Radar de Licitações (MVP, custo zero)

Todo dia às 06:17 (Brasília), um GitHub Action busca no PNCP os editais com proposta
aberta em SP e MG, classifica por nicho e manda a cada assinante só o que bate com o
perfil dele. Não usa LLM nesta fase.

```
radar/pncp.py      cliente PNCP (modo busca + varredura pela API oficial, com backoff para 429)
radar/nichos.py    nichos: termos de busca + regex de inclusão/exclusão
radar/coletar.py   grava/atualiza editais em data/editais.db (SQLite versionado no repo)
radar/enviar.py    e-mail diário (Pro) ou semanal com 3 itens (grátis); modo --ensaio grava HTML
.github/workflows/radar.yml   agenda diária, segredos via GitHub Secrets
radar/relatorio.py relatório semanal sem LLM e sem dados pessoais → cerebro/memoria/semanal/
cerebro/           "segundo cérebro" do negócio:
  contexto/        quem é o cliente, oferta, regras que nenhuma rotina quebra
  memoria/         decisões, feedback dos assinantes, log das coletas, relatórios semanais
  rotinas/         prompt da revisão semanal (tarefa agendada do Claude, sexta)
tests/             teste ponta a ponta sem rede
```

## Como o negócio roda sozinho
- **Todo dia 06:17:** GitHub Action coleta, envia e grava o log em `cerebro/memoria/execucoes.jsonl`.
  Se a busca do portal falhar, tenta a API oficial (plano B) e registra o erro.
- **Sexta 07:41:** GitHub Action gera o relatório da semana.
- **Sexta depois das 08h:** tarefa agendada do Claude lê contexto, relatório e respostas dos assinantes,
  registra o feedback, deixa rascunhos de suporte e abre um Pull Request com ajustes de filtro.
  Você revisa a página "3 coisas que precisam de você" e aprova ou não o PR.

## Rodar localmente
```
pip install -r requirements.txt
cp config/assinantes.exemplo.json config/assinantes.json   # edite com seu e-mail
python -m radar.coletar --ufs SP MG          # modo busca (padrão)
python -m radar.enviar --ensaio              # gera data/saida/*.html sem enviar
```

## Segredos do GitHub (Settings → Secrets and variables → Actions)
| Nome | O que é |
|---|---|
| SMTP_HOST / SMTP_PORT | ex.: smtp-relay.brevo.com / 587 (plano grátis: 300 e-mails/dia) |
| SMTP_USER / SMTP_PASS | login SMTP do provedor |
| EMAIL_FROM | `Radar de Licitações <radar@seudominio.com.br>` |
| LINK_ASSINATURA | link do checkout (Kiwify/Mercado Pago) |
| ASSINANTES_JSON | conteúdo do assinantes.json (fica fora do repositório por LGPD) |

## Próximas fases
1. Webhook do checkout → atualiza ASSINANTES_JSON automaticamente (hoje é manual).
2. Páginas públicas por nicho/cidade (SEO) em GitHub Pages.
3. Depois do 1º pagante: resumo e "vale disputar?" por LLM via chave de API, só para editais filtrados.
