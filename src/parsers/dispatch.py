def run_parser(template_code: str, pdf_bytes: bytes, mecanografico: str):
    # devolve lista de dicts: {data, hora_inicio, hora_fim, titulo, raw_code}
    if template_code == "SISQUAL_V1":
        from src.parsers.sisqual_v1 import parse_sisqual_v1
        return parse_sisqual_v1(pdf_bytes=pdf_bytes, mecanografico=mecanografico)
    return []
