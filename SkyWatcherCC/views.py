from django.http import HttpResponse
from rest_framework.utils import json


class HttpSuccess(HttpResponse):
    def __init__(self, js=None, **kwargs):
        if js is None:
            js = {}
        js['success'] = True
        js = json.dumps(js)
        super().__init__(content=js, content_type='application/json', status=200, **kwargs)


class HttpFailed(HttpResponse):
    def __init__(self, js=None, **kwargs):
        if js is None:
            js = {}
        js['success'] = False
        js = json.dumps(js)
        super().__init__(content=js, content_type='application/json', status=400, **kwargs)

