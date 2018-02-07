from django.shortcuts import render_to_response
from django.template import RequestContext


def handler404(request):
    response = render_to_response(
        template_name='404.html',
        context=RequestContext(request)
    )
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', RequestContext(request))
    response.status_code = 500
    return response
