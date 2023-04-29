#!/usr/bin/env python3
import requests
import time
from common import configure_tracer, configure_meter

from opentelemetry import context, trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor, BatchSpanProcessor
from opentelemetry.semconv.trace import HttpFlavorValues, SpanAttributes

from local_machine_resource_detector import LocalMachineResourceDetector
from opentelemetry.propagate import inject
from opentelemetry.trace import Status, StatusCode




# def configure_tracer(name, version):
#     exporter = ConsoleSpanExporter()
#     span_processor = BatchSpanProcessor(exporter)
#     local_resource = LocalMachineResourceDetector().detect()
#     resource = local_resource.merge(
#         Resource.create(
#             {
#                 "service.name": name,
#                 "service.version": version
#             }
#         )
#     )
#     provider = TracerProvider(resource=resource)
#     provider.add_span_processor(span_processor)
#     trace.set_tracer_provider(provider)
#     return trace.get_tracer(name, version)

tracer = configure_tracer("shopper", "0.1.2")
meter = configure_meter("shopper", "0.1.2")

total_duration_histo = meter.create_histogram(
    name="duration",
    description="request duration",
    unit="ms",
)

upstream_duration_histo = meter.create_histogram(
    name="upstream_request_duration",
    description="duration of upstream requests",
    unit="ms",
)

@tracer.start_as_current_span("browse")
def browse():
    print("visiting the grocery store")
    with tracer.start_as_current_span(
        "web request", kind=trace.SpanKind.CLIENT
    ) as span:
        headers = {}
        inject(headers)
        try:
            url = "http://localhost:5000/products"
            span.set_attributes(
                {
                    SpanAttributes.HTTP_METHOD: "GET",
                    SpanAttributes.HTTP_FLAVOR: str(HttpFlavorValues.HTTP_1_1),
                    SpanAttributes.HTTP_URL: url,
                    SpanAttributes.NET_PEER_IP: "127.0.0.1",
                }
            )
            span.add_event("about to send a request")
            start = time.time_ns()
            resp = requests.get(url, headers=headers)
            duration = (time.time_ns() - start)/1e6
            upstream_duration_histo.record(duration)

            span.add_event("request sent", attributes={"url": url})
            span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, resp.status_code)
            span.set_status(Status(StatusCode.OK))
        except Exception as err:
            attributes = {
                SpanAttributes.EXCEPTION_MESSAGE: str(err),
            }
            span.add_event("exception", attributes=attributes)
            span.set_status(Status(StatusCode.ERROR, "status code: {}", str(err)))

@tracer.start_as_current_span("add item to cart")
def add_item_to_cart(item, quantity):
    span = trace.get_current_span()
    span.set_attributes({
        "item": item,
        "quantity": quantity
    })
    print("add {} to cart".format(item))

@tracer.start_as_current_span("visit store")
def visit_store():
    start = time.time_ns()
    browse()
    duration = (time.time_ns() - start)/1e6
    total_duration_histo.record(duration)


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
   