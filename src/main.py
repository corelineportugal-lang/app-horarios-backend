from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
@app.head("/health")
def health():
    return {"status": "ok"}

