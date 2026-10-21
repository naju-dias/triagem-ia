import logging
import os

import requests
from dotenv import load_dotenv

from ..schemas import Triagem

load_dotenv()
logger = logging.getLogger("triagem")
WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")


def alertar_urgente(id_: int, t: Triagem) -> None:
    if not WEBHOOK:
        return
    payload = {
        "embeds": [{
            "title": f"🚨 Triagem urgente #{id_}",
            "description": t.resumo,
            "color": 15158332,
            "fields": [
                {"name": "Categoria", "value": t.categoria, "inline": True},
                {"name": "Confiança", "value": f"{t.confianca:.0%}", "inline": True},
                {"name": "Resposta sugerida", "value": t.resposta_sugerida[:1000]},
            ],
        }]
    }
    try:
        requests.post(WEBHOOK, json=payload, timeout=10).raise_for_status()
    except requests.RequestException:
        logger.exception("Falha ao enviar alerta ao Discord")