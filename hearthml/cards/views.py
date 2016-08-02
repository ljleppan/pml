from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render

from .models import *
from .lib import importer, learner

@user_passes_test(lambda u: u.is_staff)
@transaction.atomic
def populate_db(request):
    importer.import_cards()
    return HttpResponse("Done!")

@user_passes_test(lambda u: u.is_staff)
@transaction.atomic
def learn(request):
    score = learner.learn()
    return HttpResponse(score)

def index(request):
    return render(request, 'index.html', {})

# CARDS
def cards_index(request):
    return render(request, 'cards/index.html', {})

def cards_show(request, id):
    return render(request, 'cards/show.html', {'id':id})

# MECHANICS
def mechanics_index(request):
    return render(request, 'mechanics/index.html', {})

def mechanics_show(request, id):
    return render(request, 'mechanics/show.html', {'id':id})
