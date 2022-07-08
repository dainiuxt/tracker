from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. Issue tracker is under heavy development. Check for the updates later.")
