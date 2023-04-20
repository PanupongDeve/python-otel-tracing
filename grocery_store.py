import requests
from flask import Flask, request
from opentelemetry import trace
from opentelemetry.semconv.trace import HttpFlavorValues, SpanAttributes
from opentelemetry.trace import SpanKind
from common import configure_tracer
from opentelemetry import context
from opentelemetry.propagate import extract, inject, set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation import tracecontext
from common import set_span_attributes_from_flask



tracer = configure_tracer("0.1.2", "grocery-store")
app = Flask(__name__)

set_global_textmap(CompositePropagator([tracecontext.TraceContextTextMapPropagator(), B3MultiFormat()]))


@app.before_request
def before_request_func():
    print("before request doing...................")
    token = context.attach(extract(request.headers))
    request.environ["context_token"] = token

@app.teardown_request
def teardown_request_func(err):
    token = request.environ.get("context_token", None)
    print("teardown doing...................")
    if token:
        context.detach(token)

@app.route("/")
@tracer.start_as_current_span("welcome", kind=SpanKind.SERVER)
def welcome():
    print("main doing...................")
    # span = trace.get_current_span()
    # span.set_attributes(
    #     {
    #         SpanAttributes.HTTP_FLAVOR: request.environ.get("SERVER_PROTOCOL"),
    #         SpanAttributes.HTTP_METHOD: request.method,
    #         SpanAttributes.HTTP_USER_AGENT: str(request.user_agent),
    #         SpanAttributes.HTTP_HOST: request.host,
    #         SpanAttributes.HTTP_SCHEME: request.scheme,
    #         SpanAttributes.HTTP_TARGET: request.path,
    #         SpanAttributes.HTTP_CLIENT_IP: request.remote_addr,
    #     }
    # )
    set_span_attributes_from_flask()
    return "Welcom to the grocery store!"

@app.route("/products")
@tracer.start_as_current_span("/products", kind=SpanKind.SERVER)
def products():
    set_span_attributes_from_flask()
    with tracer.start_as_current_span("inventory request") as span:
        url = "http://localhost:5001/inventory"
        span.set_attributes(
            {
                SpanAttributes.HTTP_METHOD: "GET",
                SpanAttributes.HTTP_FLAVOR: str(HttpFlavorValues.HTTP_1_1),
                SpanAttributes.HTTP_URL: url,
                SpanAttributes.NET_PEER_IP: "127.0.0.1",
            }
        )

        headers = {}
        inject(headers)
        resp = requests.get(url, headers=headers)
        return resp.text

if __name__ == "__main__":
    app.run(host="0.0.0.0")