import logging
import os
from datetime import datetime

import gspread
from dotenv import load_dotenv

from ..schemas import Triagem

load_dotenv()
logger = logging.getLogger("triagem")

_ws = None


def _aba():
    global _ws
    if _ws is None:
        gc = gspread.service_account(
            filename=os.getenv("GOOGLE_CREDENTIALS", "credentials.json")
        )
        _ws = gc.open_by_key(os.environ["GOOGLE_SHEET_ID"]).sheet1
    return _ws


def registrar(id_: int, mensagem: str, t: Triagem, revisao: bool) -> None:
    if not os.getenv("GOOGLE_SHEET_ID"):
        return
    try:
        _aba().append_row(
            [
                id_,
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                mensagem,
                t.categoria,
                t.urgencia,
                t.confianca,
                t.resumo,
                t.nome or "",
                t.valor_solicitado or "",
                t.tipo_negocio or "",
                t.resposta_sugerida,
                "SIM" if revisao else "não",
            ],
            value_input_option="USER_ENTERED",
        )
    except Exception:
        logger.exception("Falha ao registrar na planilha")