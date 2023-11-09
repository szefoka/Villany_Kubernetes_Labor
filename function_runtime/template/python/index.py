# Copyright (c) Alex Ellis 2017. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from flask import Flask, request
from function import handler
from waitress import serve
import os
import socket

import json
import base64

from jaeger_client import Config
from jaeger_client import Span
from jaeger_client import SpanContext
import logging

app = Flask(__name__)

def init_jaeger_tracer(function_name='your-app-name'):
    log_level = logging.DEBUG
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)
    hostname = socket.gethostname()
    config = Config(
        config={ # usually read from some yaml config
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': 'jaeger-udp.default.svc.cluster.local',
                'reporting_port': '6831',
            },
            'logging': True,
        },
        service_name="-".join(list(set(hostname.split("-")) - set(hostname.split("-")[-2:]))),
        validate=True,
    )
    # this call also sets opentracing.tracer
    tracer = config.initialize_tracer()
    return tracer


tracer = init_jaeger_tracer()


# distutils.util.strtobool() can throw an exception
def is_true(val):
    return len(val) > 0 and val.lower() == "true" or val == "1"

@app.before_request
def fix_transfer_encoding():
    """
    Sets the "wsgi.input_terminated" environment flag, thus enabling
    Werkzeug to pass chunked requests as streams.  The gunicorn server
    should set this, but it's not yet been implemented.
    """

    transfer_encoding = request.headers.get("Transfer-Encoding", None)
    if transfer_encoding == u"chunked":
        request.environ["wsgi.input_terminated"] = True

@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def main_route(path):
    global tracer

    raw_body = os.getenv("RAW_BODY", "false")

    as_text = True

    if is_true(raw_body):
        as_text = False
    req = request.get_data(as_text=as_text)
    param = None
    context = None

    print(req)

    try:
        data = json.loads(req)
        if isinstance(data, dict) and "jaeger_span" in data:
            param = data["data"]
            context = data["jaeger_span"]
        else:
            param = req
            context = None
    except:
        param = req
        context = None

    if context is None:
        with tracer.start_span('TestSpan') as span:
            span.log_kv({'event': 'test message', 'life': 42})
            ret = handler.handle(param, {"span_id": span.span_id, "trace_id": span.trace_id, "flags": span.flags})
    else:
        #parent_span_data = json.loads(str(base64.b64decode(context)))
        #parent_span_data = json.loads(context)
        parent_span_data = context
        parent_span_context = SpanContext(trace_id = parent_span_data["trace_id"], span_id = parent_span_data["span_id"], parent_id = None, flags = parent_span_data["flags"])
        #parent_span = Span(parent_span_context)
        #parent_span = base64.b64decode(context)
        with tracer.start_span('ChildSpan', child_of=parent_span_context) as child_span:
            child_span.log_kv({'event': 'down below'})
            ret = handler.handle(param, {"span_id": child_span.span_id, "trace_id": child_span.trace_id, "flags": child_span.flags})

    return ret

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
