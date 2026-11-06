"""Cliente mínimo da API de consulta do PNCP (pública, sem autenticação).

Docs: https://pncp.gov.br/api/consulta/swagger-ui/index.html
"""
from __future__ import annotations

import time
from datetime import date, timedelta
from typing import Iterator

import requests

BASE = "https://pncp.gov.br/api/consulta/v1"

# Modalidades que recebem proposta (Lei 14.133)
MODALIDADES = {
    4: "Concorrência - Eletrônica",
    6: "Pregão - Eletrônico",
    7: "Pregão - Presencial",
    8: "Dispensa",
    12: "Credenciamento",
}

_session = requests.Session()
_session.headers["User-Agent"] = "radar-licitacoes/0.1"


def _get(path: str, params: dict, max_tries: int = 6) -> dict | None:
    """GET com backoff para 429/5xx. Retorna None quando a consulta não tem dados (204)."""
    wait = 2.0
    for attempt in range(max_tries):
        try:
            r = _session.get(f"{BASE}{path}", params=params, timeout=60)
        except requests.RequestException:
            time.sleep(wait)
            wait *= 2
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code == 204:
            return None
        if r.status_code == 429 or r.status_code >= 500:
            retry_after = r.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else wait)
            wait *= 2
            continue
        r.raise_for_status()
    raise RuntimeError(f"PNCP não respondeu após {max_tries} tentativas: {path} {params}")


def propostas_abertas(uf: str, modalidade: int, dias: int = 120, pausa: float = 0.8) -> Iterator[dict]:
    # A API responde 429 (página HTML "Limite de requisições excedido", sem Retry-After)
    # quando recebe chamadas em paralelo ou em rajada. Uma chamada por vez com ~0,8 s de
    # pausa passou nos testes de 05/11/2026.
    """Itera todas as contratações com recebimento de propostas em aberto."""
    data_final = (date.today() + timedelta(days=dias)).strftime("%Y%m%d")
    pagina = 1
    while True:
        j = _get(
            "/contratacoes/proposta",
            {
                "dataFinal": data_final,
                "codigoModalidadeContratacao": modalidade,
                "uf": uf,
                "pagina": pagina,
                "tamanhoPagina": 50,
            },
        )
        if not j or not j.get("data"):
            return
        yield from j["data"]
        if pagina >= j.get("totalPaginas", 1):
            return
        pagina += 1
        time.sleep(pausa)


def normalizar(d: dict) -> dict:
    """Reduz o registro do PNCP aos campos que o radar usa."""
    uo = d.get("unidadeOrgao") or {}
    oe = d.get("orgaoEntidade") or {}
    cnpj = oe.get("cnpj")
    ano = d.get("anoCompra")
    seq = d.get("sequencialCompra")
    return {
        "id": d["numeroControlePNCP"],
        "uf": uo.get("ufSigla"),
        "municipio": uo.get("municipioNome"),
        "ibge": uo.get("codigoIbge"),
        "orgao": oe.get("razaoSocial"),
        "esfera": oe.get("esferaId"),
        "modalidade": d.get("modalidadeNome"),
        "objeto": (d.get("objetoCompra") or "").strip(),
        "info": (d.get("informacaoComplementar") or "").strip(),
        "valor": d.get("valorTotalEstimado"),
        "abertura": d.get("dataAberturaProposta"),
        "encerramento": d.get("dataEncerramentoProposta"),
        "publicacao": d.get("dataPublicacaoPncp"),
        "link_origem": d.get("linkSistemaOrigem"),
        "link_pncp": f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}" if cnpj and ano and seq else None,
    }


# --- Modo busca -----------------------------------------------------------------
# Endpoint de busca do próprio portal (o mesmo que a página pncp.gov.br/app/editais usa).
# Não é documentado como API pública, mas permite filtrar por palavra-chave e por
# várias UFs em uma chamada só ("SP|MG"), com até 100 itens por página. Em 05/11/2026,
# 6 nichos x ~7 termos rodaram em ~30 s sem 429. Use como modo principal enquanto
# funcionar e mantenha /contratacoes/proposta como plano B.
BUSCA = "https://pncp.gov.br/api/search/"


def buscar_abertos(termo: str, ufs: list[str], max_paginas: int = 10, pausa: float = 0.5) -> Iterator[dict]:
    for pagina in range(1, max_paginas + 1):
        wait = 2.0
        r = None
        for _ in range(6):
            try:
                r = _session.get(
                BUSCA,
                params={
                    "tipos_documento": "edital",
                    "status": "recebendo_proposta",
                    "ordenacao": "-data",
                    "ufs": "|".join(ufs),
                    "q": termo,
                    "pagina": pagina,
                    "tam_pagina": 100,
                },
                timeout=60,
                )
            except requests.RequestException:
                r = None
                time.sleep(wait)
                wait *= 2
                continue
            if r.status_code != 429:
                break
            time.sleep(wait)
            wait *= 2
        if r is None:
            raise RuntimeError(f"PNCP (busca) sem resposta após 6 tentativas: termo={termo!r} pagina={pagina}")
        r.raise_for_status()
        itens = r.json().get("items") or []
        yield from itens
        if len(itens) < 100:
            return
        time.sleep(pausa)


def normalizar_busca(it: dict) -> dict:
    url = it.get("item_url") or ""  # /compras/{cnpj}/{ano}/{seq}
    partes = url.strip("/").split("/")
    link = f"https://pncp.gov.br/app/editais/{'/'.join(partes[1:])}" if len(partes) == 4 else None
    return {
        "id": it["numero_controle_pncp"],
        "uf": it.get("uf"),
        "municipio": it.get("municipio_nome"),
        "ibge": it.get("codigo_ibge"),
        "orgao": it.get("orgao_nome"),
        "esfera": it.get("esfera_id"),
        "modalidade": it.get("modalidade_licitacao_nome"),
        "objeto": (it.get("description") or "").strip(),
        "info": "",
        "valor": it.get("valor_global"),
        "abertura": it.get("data_inicio_vigencia"),
        "encerramento": it.get("data_fim_vigencia"),
        "publicacao": it.get("data_publicacao_pncp"),
        "link_origem": None,
        "link_pncp": link,
    }
