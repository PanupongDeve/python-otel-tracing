#!/usr/bin/env python3

from opentelemetry import context, trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

def configure_tracer():
    exporter = ConsoleSpanExporter()
    span_processor = SimpleSpanProcessor(exporter)
    provider = TracerProvider()
    provider.add_span_processor(span_processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer("shopper.py", "0.0.1")

tracer = configure_tracer()

@tracer.start_as_current_span("browse")
def browse():
    print("visiting the grocery store")
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
   