from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
@app.head("/health")
def health():
    return {"status": "ok"}
