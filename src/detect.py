import io
import pdfplumber

def detect_tipo_input(pdf_bytes: bytes) -> str:
    # pdf_text: tem texto nas primeiras 2 páginas
    # pdf_hibrido: mistura de páginas com/sem texto (nas primeiras 2)
    # imagem: sem texto nas primeiras 2
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        texts = []
        for p in pdf.pages[:2]:
            t = (p.extract_text() or "").strip()
            texts.append(bool(t))
    if any(texts) and all(texts):
        return "pdf_text"
    if any(texts) and not all(texts):
        return "pdf_hibrido"
    return "imagem"
