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
tests/             teste ponta a ponta sem rede
```

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
