import re
from django.http.response import HttpResponse
from django.template.response import TemplateResponse

# Automatically add HTTP/2 Server Push to pages.
#
# Yes, we're parsing HTML as strings. It's awful. But! Because we control the
# template being rendered, we know exactly what to search for. It's a hack, but
# it's a reasonably safe one.

CSS_RE = re.compile(r'<link rel="stylesheet" href="([^"]+)"')
JS_RE = re.compile(r'<script type="text/javascript" src="([^"]+)"')
def post_render_callback(response):
    response["Link"] = ",".join([
        "<{}>;rel=preload;as={}".format(url, kind) for (url, kind) in \
            [(url, "stylesheet") for url in CSS_RE.findall(response.rendered_content)] + \
            [(url, "script") for url in JS_RE.findall(response.rendered_content)]
    ])
    return response

def ServerPushMiddleware(get_response):
    def middleware(request):
        response = get_response(request)
        if isinstance(response, TemplateResponse):
            response.add_post_render_callback(post_render_callback)
        return response
    return middleware
