from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
import os, re

__ROOT__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test(request):
    return JsonResponse({"data": "test"})
