from django.shortcuts import render

# Create your views here.


def hotsite_base(request):
    return render(request, 'hotsite/base.html')


def hotsite_form(request):
    return render(request, 'hotsite/form.html')


