"""Relatório semanal de operação (sem LLM, sem dados pessoais).

Grava cerebro/memoria/semanal/AAAA-Wss.md com volume por nicho, coletas da semana e envios.
A rotina semanal do Claude lê este arquivo para preparar a revisão de sexta.

Uso: python -m radar.relatorio
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .coletar import EXECUCOES, conectar
from .nichos import NICHOS

RAIZ = Path(__file__).resolve().parent.parent
SEMANAL = RAIZ / "cerebro" / "memoria" / "semanal"


def main() -> Path:
    con = conectar()
    agora = datetime.now(timezone.utc)
    inicio = (agora - timedelta(days=7)).isoformat(timespec="seconds")
    hoje_brt = (agora - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")

    novos = Counter()
    abertos = Counter()
    for r in con.execute("SELECT nichos, uf, visto_em, encerramento FROM editais"):
        for n in json.loads(r["nichos"] or "[]"):
            if r["visto_em"] >= inicio:
                novos[(n, r["uf"])] += 1
            if (r["encerramento"] or "") > hoje_brt:
                abertos[n] += 1

    envios = con.execute(
        "SELECT COUNT(*) AS editais, COUNT(DISTINCT assinante) AS pessoas FROM envios WHERE enviado_em >= ?",
        (inicio,),
    ).fetchone()

    execs = []
    if EXECUCOES.exists():
        for linha in EXECUCOES.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(linha)
            except json.JSONDecodeError:
                continue
            if e.get("quando", "") >= inicio:
                execs.append(e)
    falhas = [e for e in execs if e.get("erro")]

    ano, semana, _ = agora.isocalendar()
    linhas = [
        f"# Semana {ano}-W{semana:02d} (gerado em {agora:%Y-%m-%d %H:%M} UTC)",
        "",
        "## Coletas",
        f"- Execuções: {len(execs)} · com erro: {len(falhas)}",
    ]
    for f in falhas[-5:]:
        linhas.append(f"  - {f['quando']}: {f['erro'][:200]}")
    linhas += ["", "## Editais por nicho", "", "| Nicho | Abertos agora | Novos SP (7d) | Novos MG (7d) |", "| --- | --- | --- | --- |"]
    for chave, n in NICHOS.items():
        linhas.append(f"| {n['nome']} | {abertos[chave]} | {novos[(chave, 'SP')]} | {novos[(chave, 'MG')]} |")
    linhas += [
        "",
        "## Envios (7d)",
        f"- Assinantes que receberam e-mail: {envios['pessoas']}",
        f"- Editais enviados: {envios['editais']}",
        "",
    ]
    SEMANAL.mkdir(parents=True, exist_ok=True)
    destino = SEMANAL / f"{ano}-W{semana:02d}.md"
    destino.write_text("\n".join(linhas), encoding="utf-8")
    print(destino)
    return destino


if __name__ == "__main__":
    main()
