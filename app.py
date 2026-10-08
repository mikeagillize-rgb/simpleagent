
import os
import secrets
import logging

import uvicorn
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from agent import agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Assistente Rottas API")

API_KEY = os.getenv("API_KEY")


class PerguntaRequest(BaseModel):
    pergunta: str = Field(min_length=1, max_length=10000)


@app.get("/health")
def health():
    return {"status": "online"}


@app.post("/perguntar")
def perguntar(
    dados: PerguntaRequest,
    x_api_key: str | None = Header(default=None)
):
    if (
        not API_KEY
        or not x_api_key
        or not secrets.compare_digest(x_api_key, API_KEY)
    ):
        raise HTTPException(
            status_code=401,
            detail="Não autorizado"
        )

    try:
        result = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": dados.pergunta
                }
            ]
        })

        mensagem = result["messages"][-1]
        resposta = mensagem.content

        return {"resposta": resposta}

    except Exception:
        logger.exception("Erro ao executar agente")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao executar o agente"
        )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
