import os
import requests

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
BUCKET = os.getenv("SUPABASE_BUCKET", "uploads")


def _headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


def db_select_template(instituicao_id: str, categoria: str, tipo_input: str):
    base = f"{SUPABASE_URL}/rest/v1/templates"
    params = {
        "select": "id,instituicao_id,categoria,tipo_input,familia,template_code,versao,ativo",
        "instituicao_id": f"eq.{instituicao_id}",
        "tipo_input": f"eq.{tipo_input}",
        "ativo": "eq.true",
        "order": "versao.desc",
        "limit": "1",
    }

    # 1) match categoria
    r = requests.get(base, headers=_headers(), params={**params, "categoria": f"eq.{categoria}"}, timeout=30)
    if r.ok and r.json():
        return r.json()[0]

    # 2) fallback categoria NULL
    r = requests.get(base, headers=_headers(), params={**params, "categoria": "is.null"}, timeout=30)
    if r.ok and r.json():
        return r.json()[0]

    return None


def db_insert_import(payload: dict):
    url = f"{SUPABASE_URL}/rest/v1/imports"
    h = _headers()
    h["Prefer"] = "return=representation"
    r = requests.post(url, headers=h, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()[0]


def db_update_import(import_id: str, patch: dict):
    url = f"{SUPABASE_URL}/rest/v1/imports"
    params = {"id": f"eq.{import_id}"}
    r = requests.patch(url, headers=_headers(), params=params, json=patch, timeout=30)
    r.raise_for_status()
