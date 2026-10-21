import os
import time
from dotenv import load_dotenv
from google import genai
from .schemas import Triagem

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODELO = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

SISTEMA = """Você faz a triagem de mensagens de pequenos empreendedores
que falam com o Estímulo (crédito, capacitação e tecnologia).

Categorias:
- credito: pedidos, dúvidas e andamento de crédito.
- suporte: problemas práticos de conta, pagamento, cadastro, documentos e erros do app/site, mesmo que o cliente esteja chateado, desde que o foco seja resolver um problema pontual.
- capacitacao: cursos, trilhas e conteúdos educativos.
- reclamacao: só quando o foco é insatisfação, cobrança indevida ou ameaça de tomar providências.
- outro: saudações, perguntas gerais e institucionais (horário, endereço).

Classifique a mensagem, avalie a urgência, resuma em 1 frase,
extraia os dados citados e sugira uma resposta curta, educada e clara.
Se não souber um dado, deixe nulo. Nunca invente valores.

Regras para a resposta sugerida:
- Não invente links, portais, telefones, prazos, taxas ou procedimentos.
- Não use marcadores como [link] ou [nome].
- Se faltar informação, peça os dados necessários (ex.: tipo de negócio, valor, CNPJ) ou diga que um atendente entrará em contato."""


def classificar(texto: str, tentativas: int = 4) -> Triagem:
    for i in range(tentativas):
        try:
            resp = client.models.generate_content(
                model=MODELO,
                contents=texto,
                config={
                    "system_instruction": SISTEMA,
                    "response_mime_type": "application/json",
                    "response_schema": Triagem,
                },
            )
            return resp.parsed
        except Exception:
            if i == tentativas - 1:
                raise
            time.sleep(5 * 2 ** i)  # espera 5s, 10s, 20s