from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

def setup_observability(app: FastAPI, service_name: str, otlp_endpoint: str = "http://jaeger:4317"):
    # 1. Tracing Setup
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # 2. Metrics Setup
    Instrumentator().instrument(app).expose(app)

    return app
