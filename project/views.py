from django.template.response import TemplateResponse


def handler404(request):
    """
    400 error handler.

    Templates: :template:`400.html`
    Context: None
    """
    context = {'request': request}
    template_name = 'http_error/404.html'
    return TemplateResponse(request, template_name, context, status=404)


def handler500(request):
    """500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """

    context = {'request': request}
    # You need to create a 500.html template.
    template_name = 'http_error/500.html'
    return TemplateResponse(request, template_name, context, status=500)
