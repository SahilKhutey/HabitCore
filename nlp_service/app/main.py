from fastapi import FastAPI
from app.schemas import TextInput, SignalOutput
from app.pipeline import process_text

app = FastAPI(title="NLP Behavioral Engine")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=SignalOutput)
def analyze(input: TextInput):
    result = process_text(input.user_id, input.text)
    return result


@app.post("/analyze/batch")
def analyze_batch(inputs: list[TextInput]):
    return [process_text(i.user_id, i.text) for i in inputs]
