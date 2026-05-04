from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.schemas import TextInput, SignalOutput
from app.pipeline import process_text
from app.observability import setup_observability

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic can go here
    yield
    # Shutdown logic can go here

app = FastAPI(title="NLP Behavioral Engine", lifespan=lifespan)

# Initialize Observability
setup_observability(app, service_name="nlp_service")

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
