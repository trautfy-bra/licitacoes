"""Coleta as contratações com proposta aberta e grava no SQLite.

Uso: python -m radar.coletar --ufs SP MG
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .nichos import NICHOS, classificar
from .pncp import MODALIDADES, buscar_abertos, normalizar, normalizar_busca, propostas_abertas

DB = Path(__file__).resolve().parent.parent / "data" / "editais.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS editais (
    id TEXT PRIMARY KEY,
    uf TEXT, municipio TEXT, ibge TEXT, orgao TEXT, esfera TEXT, modalidade TEXT,
    objeto TEXT, info TEXT, valor REAL,
    abertura TEXT, encerramento TEXT, publicacao TEXT,
    link_origem TEXT, link_pncp TEXT,
    nichos TEXT,
    visto_em TEXT,
    atualizado_em TEXT
);
CREATE INDEX IF NOT EXISTS ix_editais_enc ON editais(encerramento);
CREATE INDEX IF NOT EXISTS ix_editais_visto ON editais(visto_em);
CREATE TABLE IF NOT EXISTS envios (
    assinante TEXT, edital TEXT, enviado_em TEXT,
    PRIMARY KEY (assinante, edital)
);
"""


def conectar(path: Path = DB) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def gravar(con: sqlite3.Connection, e: dict, agora: str) -> bool:
    """Insere ou atualiza; retorna True se o edital é novo."""
    nichos = json.dumps(classificar(e["objeto"], e["info"]))
    existe = con.execute("SELECT 1 FROM editais WHERE id=?", (e["id"],)).fetchone()
    if existe:
        con.execute(
            "UPDATE editais SET encerramento=?, valor=?, nichos=?, atualizado_em=? WHERE id=?",
            (e["encerramento"], e["valor"], nichos, agora, e["id"]),
        )
        return False
    con.execute(
        """INSERT INTO editais (id, uf, municipio, ibge, orgao, esfera, modalidade, objeto, info, valor,
           abertura, encerramento, publicacao, link_origem, link_pncp, nichos, visto_em, atualizado_em)
           VALUES (:id, :uf, :municipio, :ibge, :orgao, :esfera, :modalidade, :objeto, :info, :valor,
           :abertura, :encerramento, :publicacao, :link_origem, :link_pncp, :nichos, :agora, :agora)""",
        {**e, "nichos": nichos, "agora": agora},
    )
    return True


def main(ufs: list[str], modo: str = "busca") -> dict:
    con = conectar()
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    novos = total = 0
    if modo == "busca":
        # Só os termos dos nichos ativos: poucas chamadas, sem varrer tudo.
        for chave, nicho in NICHOS.items():
            for termo in nicho.get("busca", []):
                for item in buscar_abertos(termo, ufs):
                    e = normalizar_busca(item)
                    if not classificar(e["objeto"]):
                        continue
                    total += 1
                    if gravar(con, e, agora):
                        novos += 1
                con.commit()
    else:
        for uf in ufs:
            for mod in MODALIDADES:
                for bruto in propostas_abertas(uf, mod):
                    total += 1
                    if gravar(con, normalizar(bruto), agora):
                        novos += 1
                con.commit()
    resumo = {"quando": agora, "modo": modo, "ufs": ufs, "lidos": total, "novos": novos}
    print(json.dumps(resumo, ensure_ascii=False))
    return resumo


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ufs", nargs="+", default=["SP", "MG"])
    ap.add_argument("--modo", choices=["busca", "varredura"], default="busca")
    a = ap.parse_args()
    main(a.ufs, a.modo)
