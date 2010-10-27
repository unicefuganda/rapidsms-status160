from django.db import transaction
from django.views.decorators.http import require_GET, require_POST
from django.template import RequestContext
from django.shortcuts import redirect, get_object_or_404, render_to_response
from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Poll, Category, Rule, Response, ResponseCategory, STARTSWITH_PATTERN_TEMPLATE, CONTAINS_PATTERN_TEMPLATE
from rapidsms.models import Contact

def index(request):
    return HttpResponse(status=200)

def whitelist(request):
    return HttpResponse(status=200)

@require_POST
def new_event(request):
    return HttpResponse(status=200)

@require_POST
def send_masstext(request):
    return HttpResponse(status=200)

@require_POST
def send_alerts(request):
    return HttpResponse(status=200)




