from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.
def jump_index(request):
    return HttpResponse(render(
        request,
        'jump_index.html'
        ))