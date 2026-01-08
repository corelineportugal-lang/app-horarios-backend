import io
import re
import datetime as dt
import pdfplumber


_MONTHS = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}

_RE_DATE = re.compile(r"(\d{1,2})\s+de\s+([A-Za-zçãõéêíóúô]+)\s+de\s+(\d{4})", re.I)
_RE_CODE_TIME = re.compile(r"([A-Z]{1,4}\d{0,3}[A-Za-z]{0,10})\([^)]*\)\s*(\d{2}:\d{2})-(\d{2}:\d{2})\*?")
_RE_TIMEISH = re.compile(r"^[-+]?\d{1,2}:\d{2}$|^\d+\.\d+$")


def _parse_pt_date(s: str):
    m = _RE_DATE.search(s)
    if not m:
        return None
    d = int(m.group(1))
    mon = _MONTHS.get(m.group(2).lower())
    y = int(m.group(3))
    if not mon:
        return None
    return dt.date(y, mon, d)


def _extract_range(text: str):
    dates = _RE_DATE.findall(text)
    if len(dates) < 2:
        return None, None
    d1 = _parse_pt_date(" ".join(dates[0]))
    d2 = _parse_pt_date(" ".join(dates[1]))
    return d1, d2


def _extract_code_map(text: str):
    m = {}
    for code, start, end in _RE_CODE_TIME.findall(text):
        m[code] = (start, end)
    return m


def _row_tokens_band(page, mecanografico: str):
    words = page.extract_words()
    mech = next((w for w in words if w["text"] == str(mecanografico)), None)
    if not mech:
        return None
    band = [w for w in words if (mech["top"] - 0.5) <= w["top"] <= (mech["top"] + 1.5)]
    band = sorted(band, key=lambda x: x["x0"])
    return [w["text"] for w in band]


def parse_sisqual_v1(pdf_bytes: bytes, mecanografico: str):
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        page = pdf.pages[0]
        text = page.extract_text() or ""

    start, end = _extract_range(text)
    code_map = _extract_code_map(text)

    tokens = _row_tokens_band(page, mecanografico)
    if not tokens or len(tokens) < 8:
        return []

    # separar "parte útil" da linha (tudo antes de totais/horas finais)
    cut = None
    for i, t in enumerate(tokens):
        if _RE_TIMEISH.match(t):
            cut = i
            break
    main = tokens[:cut] if cut else tokens

    # remover mecanográfico + nome (até começar códigos)
    # (códigos são curtos e em maiúsculas/números)
    idx = 1
    while idx < len(main):
        tok = main[idx]
        if tok in code_map or re.match(r"^[A-Z]{1,4}\d{0,3}$", tok):
            break
        idx += 1

    codes = main[idx:]

    # ajustar datas: se codes tiver mais 1 que o range, recua 1 dia
    if start and end:
        expected = (end - start).days + 1
        if len(codes) == expected + 1:
            start = start - dt.timedelta(days=1)

    if not start:
        return []

    events = []
    for j, code in enumerate(codes):
        day = start + dt.timedelta(days=j)

        if code not in code_map:
            continue

        h1, h2 = code_map[code]
        events.append({
            "data": day.isoformat(),
            "hora_inicio": h1,
            "hora_fim": h2,
            "raw_code": code,
            "titulo": code,
        })

    return events
