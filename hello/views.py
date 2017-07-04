from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting
import requests
from pulp import *

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    prob = LpProblem("Travel Time",LpMinimize)
    r = requests.get('http://httpbin.org/status/418')
    print(r.text)
    return HttpResponse('<pre>' + r.text + '</pre>')

def db(request):
    #

