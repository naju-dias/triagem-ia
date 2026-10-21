from typing import Literal, Optional
from pydantic import BaseModel

class Triagem(BaseModel):
    categoria: Literal["credito", "suporte", "capacitacao", "reclamacao", "outro"]
    urgencia: Literal["baixa", "media", "alta"]
    confianca: float            # 0 a 1
    resumo: str
    nome: Optional[str] = None
    valor_solicitado: Optional[float] = None
    tipo_negocio: Optional[str] = None
    resposta_sugerida: str