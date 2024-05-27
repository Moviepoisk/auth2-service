from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from src.core.config.jaeger import jaeger_settings


def configure_tracer(service_name: str) -> None:
    trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: service_name})))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=jaeger_settings.agent_host_name,
                agent_port=jaeger_settings.agent_port,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    span_processor = BatchSpanProcessor(ConsoleSpanExporter())
    trace.get_tracer_provider().add_span_processor(span_processor)
