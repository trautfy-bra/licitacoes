"""Teste ponta a ponta sem rede: busca simulada -> SQLite -> e-mail em modo ensaio."""
import json
from pathlib import Path

import radar.coletar as coletar
import radar.enviar as enviar

FIX = json.loads((Path(__file__).parent / "amostra_busca.json").read_text(encoding="utf-8"))


def test_fluxo(tmp_path, monkeypatch):
    db = tmp_path / "e.db"
    monkeypatch.setattr(coletar, "DB", db)
    monkeypatch.setattr(coletar, "buscar_abertos", lambda termo, ufs: iter(FIX))
    orig = coletar.conectar
    monkeypatch.setattr(enviar, "conectar", lambda: orig(db))
    monkeypatch.setattr(coletar, "conectar", lambda: orig(db))
    r = coletar.main(["SP", "MG"], "busca")
    assert r["novos"] == 4  # os 4 itens batem em audiovisual-eventos e/ou comunicação

    assin = [{"email": "t@x.com", "plano": "pro", "ufs": ["SP", "MG"], "nichos": ["audiovisual-eventos"]}]
    (tmp_path / "a.json").write_text(json.dumps(assin))
    monkeypatch.setattr(enviar, "ASSINANTES", tmp_path / "a.json")
    monkeypatch.setattr(enviar, "SAIDA", tmp_path / "saida")
    enviar.main(ensaio=True)
    html = (tmp_path / "saida" / "t_at_x.com.html").read_text()
    assert "ITANHANDU" in html and "pncp.gov.br/app/editais/18186718000180/2026/58" in html
