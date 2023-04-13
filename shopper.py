#!/usr/bin/env python3

from opentelemetry import context, trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor, BatchSpanProcessor

from local_machine_resource_detector import LocalMachineResourceDetector

def configure_tracer(name, version):
    exporter = ConsoleSpanExporter()
    span_processor = BatchSpanProcessor(exporter)
    local_resource = LocalMachineResourceDetector().detect()
    resource = local_resource.merge(
        Resource.create(
            {
                "service.name": name,
                "service.version": version
            }
        )
    )
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(span_processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(name, version)

tracer = configure_tracer("shopper", "0.1.2")

@tracer.start_as_current_span("browse")
def browse():
    print("visiting the grocery store")
    span = trace.get_current_span()
    span.set_attribute("http.method", "GET")
    span.set_attribute("http.flovor", "1.1")
    span.set_attribute("http.url", "http://localhost:5000")
    span.set_attribute("net.peer.ip", "127.0.0.1")
    add_item_to_cart("orange")

@tracer.start_as_current_span("add item to cart")
def add_item_to_cart(item):
    print("add {} to cart".format(item))

@tracer.start_as_current_span("visit store")
def visit_store():
    browse()


if __name__ == "__main__":
    visit_store()



    # span = tracer.start_span("visit store")
    
    # ctx = trace.set_span_in_context(span)
    # token = context.attach(ctx)
    # span2 = tracer.start_span("browse")
    # browse()
    # span2.end()
    # span.end()
    # context.detach(token)
   