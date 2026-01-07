from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
@app.head("/health")
def health():
    return {"status": "ok"}


class ParseRequest(BaseModel):
    user_id: str
    instituicao_id: str
    categoria: str
    mecanografico: str
    file_url: str


@app.post("/parse")
def parse(req: ParseRequest):
    # placeholder: vamos ligar Supabase + parser no passo seguinte
    return {"status": "not_implemented_yet"}


@app.get("/ics")
def ics(import_id: str):
    # placeholder: vamos gerar ICS no passo seguinte
    return {"status": "not_implemented_yet", "import_id": import_id}
