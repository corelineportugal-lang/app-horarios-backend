import traceback

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.supabase_http import db_insert_import, db_update_import, db_select_template, storage_delete_by_url


app = FastAPI(openapi_url="/openapi.json", docs_url="/docs")


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
    imp = db_insert_import({
        "user_id": req.user_id,
        "instituicao_id": req.instituicao_id,
        "categoria": req.categoria,
        "mecanografico": req.mecanografico,
        "file_url": req.file_url,
        "status": "processing",
    })

    try:
        tipo_input = "pdf_text"

        tpl = db_select_template(req.instituicao_id, req.categoria, tipo_input)
        if not tpl:
            db_update_import(imp["id"], {"status": "failed", "tipo_input": tipo_input, "error_code": "NO_TEMPLATE"})
            raise HTTPException(status_code=400, detail="NO_TEMPLATE")

        db_update_import(imp["id"], {"tipo_input": tipo_input, "template_id": tpl["id"]})

        db_update_import(imp["id"], {"status": "success"})
        storage_delete_by_url(req.file_url)
        return {"import_id": imp["id"], "template_id": tpl["id"], "events_count": 0}

    except HTTPException:
        raise
    
    except Exception as e:
        print("PARSE_ERROR:", repr(e))
        print(traceback.format_exc())
        db_update_import(imp["id"], {"status": "failed", "error_code": "SERVER_ERROR"})
        raise HTTPException(status_code=500, detail="SERVER_ERROR")


