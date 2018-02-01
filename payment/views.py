from django.http import HttpResponse
from django.views import generic


class PostBackView(generic.View):

    def post(self, *args, **kwargs):
        return HttpResponse('testing')
