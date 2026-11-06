"""Definição dos nichos do radar.

Cada nicho é um conjunto de expressões regulares aplicadas ao objeto da compra
(sem acento, minúsculo). `excluir` remove falsos positivos comuns.
"""
from __future__ import annotations

import re
import unicodedata


def normalizar_texto(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s.lower()).strip()
    # remove o prefixo do sistema de origem, ex.: "[portal de compras publicas] - "
    return re.sub(r"^\[[^\]]{1,60}\]\s*-?\s*", "", s)


NICHOS: dict[str, dict] = {
    "comunicacao-publicidade": {
        "busca": ["publicidade", "propaganda", "marketing", "divulgação", "assessoria de imprensa", "mídias sociais", "comunicação institucional"],
        "nome": "Comunicação, publicidade e mídia",
        "incluir": [
            r"\bpublicidade\b", r"\bpropaganda\b", r"agencia de (comunicacao|publicidade|propaganda)",
            r"\bmarketing\b", r"\bmidias? (sociais|digitais)\b", r"\bdivulgacao\b", r"\bassessoria de (imprensa|comunicacao)\b",
            r"\bveiculacao\b", r"\bradiodifus", r"\bcomunicacao (institucional|visual|social)\b",
        ],
        "excluir": [r"comunicacao de dados", r"radiocomunica", r"\btelefon"],
    },
    "audiovisual-eventos": {
        "busca": ["eventos", "sonorização", "palco", "audiovisual", "filmagem", "shows", "telão"],
        "nome": "Audiovisual, som e eventos",
        "incluir": [
            r"\baudiovisua", r"\bfilmage", r"\bproducao de (video|conteudo)", r"\bsonoriza", r"\biluminacao cenica",
            r"\bpalco", r"\bshows?\b", r"\beventos?\b", r"\btransmissao ao vivo", r"\bestrutura(s)? (para|de) eventos",
            r"\btelao\b", r"\bpaineis? de led\b",
        ],
        "excluir": [r"iluminacao publica", r"evento adverso", r"\b(obra|reforma|construcao|pavimentacao)\b",
                    r"materia(l|is) esportivo", r"seguranca (nao armada|patrimonial)"],
    },
    "software-ti": {
        "nome": "Software, sistemas e serviços de TI",
        "busca": ["software", "sistema de gestão", "licença de uso", "aplicativo", "nuvem", "suporte técnico", "portal"],
        "incluir": [
            r"\bsoftwares?\b", r"\bsistemas? (de gestao|integrado|informatizado|web|de informac|computacional)",
            r"\bsolucao (tecnologica|informatizada|de ti|em nuvem)", r"\blicenc(a|as|iamento) de (uso|software|direito de uso)",
            r"\bsaas\b", r"\bdesenvolvimento de (sistemas?|software|aplicativos?|portal|sites?)", r"\bportal (web|institucional|da transparencia)",
            r"\baplicativos?\b", r"\bcomputacao em nuvem\b", r"\bdata ?center", r"\bhospedagem de (sites?|sistemas?|dados)",
            r"\btecnologia da informacao\b", r"\bfabrica de software", r"\bsuporte tecnico (a|ao|aos|de|em) (sistemas?|software|ti|informatica)",
        ],
        "excluir": [r"sistema de (abastecimento|esgoto|drenagem|ar condicionado|climatiza|registro de precos|transferencia|som|iluminacao|seguranca eletronica)",
                    r"sistema viario"],
    },
    "dados-bi-ia": {
        "busca": ["business intelligence", "inteligência artificial", "análise de dados", "banco de dados", "geoprocessamento", "digitalização de documentos", "pesquisa de opinião"],
        "nome": "Dados, BI e inteligência artificial",
        "incluir": [
            r"\bbusiness intelligence\b", r"\b(bi)\b", r"\binteligencia artificial\b", r"\banalise de dados\b",
            r"\bciencia de dados\b", r"\bbanco de dados\b", r"\bpaine(l|is) (de|gerencia|de indicadores)", r"\bdashboards?\b",
            r"\bgeoprocessamento\b", r"\bdigitaliza(cao|r) de (documentos|acervo)", r"\bgestao (eletronica )?de documentos\b",
            r"\bchatbot", r"\bpesquisa de opiniao\b",
        ],
        "excluir": [],
    },
    "hardware-informatica": {
        "busca": ["computadores", "notebooks", "equipamentos de informática", "impressoras"],
        "nome": "Equipamentos de informática",
        "incluir": [r"\bcomputador", r"\bnotebook", r"\bmicrocomputador", r"\bimpressora", r"\bmonitor(es)?\b",
                    r"\bequipamentos? de informatica", r"\bservidor(es)? de rede", r"\btablets?\b", r"\bswitch"],
        "excluir": [r"monitor(ia|amento) de (pacientes|saude)"],
    },
    "treinamento-consultoria": {
        "busca": ["capacitação", "treinamento", "consultoria", "curso", "palestra"],
        "nome": "Treinamento, capacitação e consultoria",
        "incluir": [r"\bcapacitacao\b", r"\btreinamento", r"\bcursos?\b", r"\bconsultoria\b", r"\bassessoria tecnica\b",
                    r"\bpalestra"],
        "excluir": [r"consultoria (em )?engenharia", r"curso d.?agua"],
    },
    "grafica-impressao": {
        "busca": ["gráfica", "impressos", "banners", "material gráfico", "serviços de impressão"],
        "nome": "Gráfica e impressos",
        "incluir": [r"\bgrafic", r"\bimpressos?\b", r"\bservicos? de impressao", r"\bbanners?\b", r"\bplotage",
                    r"\bmaterial (grafico|de divulgacao)", r"\bconfeccao de (placas|faixas|adesivos)"],
        "excluir": [r"impressora"],
    },
}

_COMPILADO = {
    k: (
        [re.compile(p) for p in v["incluir"]],
        [re.compile(p) for p in v.get("excluir", [])],
    )
    for k, v in NICHOS.items()
}


def classificar(objeto: str, info: str = "") -> list[str]:
    """Retorna os nichos que batem com o objeto da compra."""
    texto = normalizar_texto(objeto)
    achados = []
    for chave, (inc, exc) in _COMPILADO.items():
        if any(p.search(texto) for p in inc) and not any(p.search(texto) for p in exc):
            achados.append(chave)
    return achados
