"""Envio das vagas para o Telegram via Bot API (requests)."""
import html
import logging

import requests

from config import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN, TIMEOUT
from scraper import Vaga

log = logging.getLogger(__name__)
POR_MENSAGEM = 8  # mantém cada mensagem abaixo do limite de 4096 caracteres


def formatar(vagas: list[Vaga]) -> str:
    blocos = []
    for v in vagas:
        selo = " 🏠 remoto" if v.remoto else ""
        blocos.append(
            f"<b>{html.escape(v.titulo)}</b>\n"
            f"{html.escape(v.empresa)} · {html.escape(v.local)}{selo}\n"
            f"<a href=\"{html.escape(v.url)}\">Ver vaga</a> ({v.fonte})"
        )
    return "\n\n".join(blocos)


def telegram_configurado() -> bool:
    return bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID)


def enviar_telegram(vagas: list[Vaga]) -> bool:
    """Retorna True se todas as mensagens foram entregues."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for i in range(0, len(vagas), POR_MENSAGEM):
        texto = f"🔎 <b>Novas vagas front-end</b>\n\n{formatar(vagas[i:i + POR_MENSAGEM])}"
        try:
            resp = requests.post(
                url,
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": texto,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            log.error("Falha ao enviar para o Telegram: %s", exc)
            return False
    return True
