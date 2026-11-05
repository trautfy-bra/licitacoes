"""Monta e envia o e-mail diário de cada assinante.

Assinantes ficam em config/assinantes.json (formato em config/assinantes.exemplo.json).
SMTP vem de variáveis de ambiente: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM.
Sem SMTP configurado, grava os e-mails em data/saida/ (modo ensaio).

Uso: python -m radar.enviar [--ensaio]
"""
from __future__ import annotations

import argparse
import html
import json
import os
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

from .coletar import conectar
from .nichos import NICHOS, normalizar_texto

RAIZ = Path(__file__).resolve().parent.parent
ASSINANTES = RAIZ / "config" / "assinantes.json"
SAIDA = RAIZ / "data" / "saida"

BRT = timezone(timedelta(hours=-3))  # datas do PNCP vêm em horário de Brasília, sem fuso
LIMITE_GRATIS = 3  # editais por semana no plano grátis
DIA_GRATIS = 0  # segunda-feira


def carregar_assinantes() -> list[dict]:
    if not ASSINANTES.exists():
        return []
    return [a for a in json.loads(ASSINANTES.read_text(encoding="utf-8")) if a.get("ativo", True)]


def _dias_restantes(enc: str | None, agora: datetime) -> int | None:
    if not enc:
        return None
    try:
        dt = datetime.fromisoformat(enc).replace(tzinfo=BRT)
    except ValueError:
        return None
    return (dt - agora).days


def selecionar(con, a: dict, agora: datetime) -> list[dict]:
    """Editais em aberto que batem com o perfil do assinante e ainda não foram enviados a ele."""
    linhas = con.execute(
        """SELECT e.* FROM editais e
           WHERE e.encerramento > ?
             AND NOT EXISTS (SELECT 1 FROM envios v WHERE v.assinante=? AND v.edital=e.id)
           ORDER BY e.encerramento""",
        (agora.astimezone(BRT).strftime("%Y-%m-%dT%H:%M:%S"), a["email"]),
    ).fetchall()
    ufs = set(a.get("ufs") or [])
    municipios = {normalizar_texto(m) for m in a.get("municipios") or []}
    nichos = set(a.get("nichos") or [])
    termos = [normalizar_texto(t) for t in a.get("termos") or []]
    bloqueios = [normalizar_texto(t) for t in a.get("excluir_termos") or []]
    vmin = a.get("valor_min") or 0
    out = []
    for r in linhas:
        e = dict(r)
        obj = normalizar_texto(e["objeto"])
        if ufs and e["uf"] not in ufs:
            continue
        if municipios and normalizar_texto(e["municipio"] or "") not in municipios:
            continue
        bate_nicho = bool(nichos & set(json.loads(e["nichos"] or "[]")))
        bate_termo = any(t in obj for t in termos)
        if not (bate_nicho or bate_termo):
            continue
        if any(b in obj for b in bloqueios):
            continue
        if e["valor"] is not None and e["valor"] < vmin:
            continue
        out.append(e)
    return out


def _brl(v) -> str:
    if v is None:
        return "não informado"
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def montar_email(a: dict, editais: list[dict], agora: datetime) -> tuple[str, str]:
    n = len(editais)
    assunto = f"Radar: {n} edita{'l' if n == 1 else 'is'} aberto{'s' if n != 1 else ''} para você"
    itens = []
    for e in editais:
        dias = _dias_restantes(e["encerramento"], agora)
        prazo = f"{dias} dia{'s' if dias != 1 else ''}" if dias is not None else "?"
        link = e["link_pncp"] or e["link_origem"] or "#"
        nichos = ", ".join(NICHOS[k]["nome"] for k in json.loads(e["nichos"] or "[]") if k in NICHOS)
        itens.append(
            f"""<tr><td style="padding:14px 0;border-bottom:1px solid #e5e5e5">
<div style="font-size:15px;font-weight:600;margin-bottom:4px">{html.escape(e['objeto'][:300])}</div>
<div style="font-size:13px;color:#555">{html.escape(e['orgao'] or '')} · {html.escape(e['municipio'] or '')}/{e['uf']}</div>
<div style="font-size:13px;margin-top:6px">💰 {_brl(e['valor'])} &nbsp;·&nbsp; ⏳ encerra em {prazo}
 ({(e['encerramento'] or '')[:10]}) &nbsp;·&nbsp; {html.escape(e['modalidade'] or '')}</div>
<div style="font-size:12px;color:#777;margin-top:4px">{html.escape(nichos)}</div>
<div style="margin-top:6px"><a href="{html.escape(link)}">Ver edital no PNCP →</a></div>
</td></tr>"""
        )
    corpo = f"""<html><body style="font-family:Arial,sans-serif;max-width:640px;margin:auto;color:#222">
<h2 style="margin-bottom:4px">Editais abertos no seu radar</h2>
<p style="color:#555;margin-top:0">{agora.astimezone(BRT):%d/%m/%Y} · fonte: Portal Nacional de Contratações Públicas (PNCP)</p>
<table width="100%" cellspacing="0">{''.join(itens)}</table>
{'<p style="background:#fff7e0;padding:12px">Plano grátis: você recebe até 3 editais por semana. <a href="' + os.environ.get('LINK_ASSINATURA', '#') + '">Assine o Pro</a> para receber todos, todo dia.</p>' if a.get('plano') == 'gratis' else ''}
<p style="font-size:12px;color:#888">Confira sempre o edital original antes de decidir participar.
Para ajustar seus filtros ou cancelar, responda este e-mail.</p>
</body></html>"""
    return assunto, corpo


def enviar(dest: str, assunto: str, corpo: str, ensaio: bool) -> None:
    host = os.environ.get("SMTP_HOST")
    if ensaio or not host:
        SAIDA.mkdir(parents=True, exist_ok=True)
        (SAIDA / f"{dest.replace('@', '_at_')}.html").write_text(corpo, encoding="utf-8")
        print(f"[ensaio] {dest}: {assunto}")
        return
    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = os.environ.get("EMAIL_FROM", os.environ["SMTP_USER"])
    msg["To"] = dest
    msg.set_content("Seu cliente de e-mail não exibe HTML. Abra no navegador.")
    msg.add_alternative(corpo, subtype="html")
    with smtplib.SMTP(host, int(os.environ.get("SMTP_PORT", 587))) as s:
        s.starttls()
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        s.send_message(msg)
    print(f"[enviado] {dest}: {assunto}")


def main(ensaio: bool = False) -> None:
    con = conectar()
    agora = datetime.now(timezone.utc)
    for a in carregar_assinantes():
        gratis = a.get("plano") == "gratis"
        if gratis and agora.weekday() != DIA_GRATIS:
            continue
        editais = selecionar(con, a, agora)
        if gratis:
            editais = editais[:LIMITE_GRATIS]
        if not editais:
            continue
        assunto, corpo = montar_email(a, editais, agora)
        enviar(a["email"], assunto, corpo, ensaio)
        if not ensaio:
            con.executemany(
                "INSERT OR IGNORE INTO envios VALUES (?,?,?)",
                [(a["email"], e["id"], agora.isoformat(timespec="seconds")) for e in editais],
            )
            con.commit()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ensaio", action="store_true")
    main(ap.parse_args().ensaio)
