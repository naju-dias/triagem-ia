import logging
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import db
from .classifier import classificar
from .integrations import notify, sheets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("triagem")

LIMITE_CONFIANCA = 0.7


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.criar_tabela()
    yield


app = FastAPI(title="Triagem IA", lifespan=lifespan)


class MensagemIn(BaseModel):
    texto: str = Field(min_length=5, max_length=2000)


def enviar_integracoes(id_, texto, t, revisao):
    sheets.registrar(id_, texto, t, revisao)
    if t.urgencia == "alta":
        notify.alertar_urgente(id_, t)


@app.post("/mensagens")
def receber(msg: MensagemIn, background: BackgroundTasks):
    try:
        t = classificar(msg.texto)
    except Exception as e:
        logger.exception("Falha ao classificar")
        raise HTTPException(502, f"Falha ao classificar: {type(e).__name__}")

    revisao = t.confianca < LIMITE_CONFIANCA
    id_ = db.salvar(msg.texto, t, revisao)
    background.add_task(enviar_integracoes, id_, msg.texto, t, revisao)
    return {"id": id_, "revisao_humana": revisao, **t.model_dump()}


@app.get("/mensagens")
def listar():
    return db.listar()