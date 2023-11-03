import requests
import json
import base64

def invoke(funcname, param, context, asynch):
    #url = f"http://{funcname}.openfaas-fn.svc.cluster.local:8080/"
    if asynch:
        url = f"http://gateway.openfaas.svc.cluster.local:8080/async-function/{funcname}"
    else:
        url = f"http://gateway.openfaas.svc.cluster.local:8080/function/{funcname}"
    invoke_data = json.dumps({"data": param, "jaeger_span": context})
    x = requests.post(url, data=invoke_data)
    return x.text
