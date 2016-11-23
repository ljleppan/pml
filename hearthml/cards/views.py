from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models import ExpressionWrapper, F, FloatField
from django.http import HttpResponse, Http404
from django.shortcuts import render

from .models import *
from .lib import importer, learner, card_generator


@user_passes_test(lambda u: u.is_staff)
@transaction.atomic
def populate_db(request):
    importer.import_cards()
    return HttpResponse("Done!")

@user_passes_test(lambda u: u.is_staff)
@transaction.atomic
def learn(request):
    lin = learner.learn()
    return HttpResponse(str(lin))

def index(request):
    cards = Card.objects.all().order_by('?')[:4]
    cards = cards.annotate(complex_delta=ExpressionWrapper(F('complex_value') - F('mana'), output_field=FloatField()))
    cards = cards.annotate(simple_delta=ExpressionWrapper(F('simple_value') - F('mana'), output_field=FloatField()))

    health_coeff = MetaData.objects.get(name="health_coeff")
    attack_coeff = MetaData.objects.get(name="minion_attack_coeff")
    minion_coeff = CardType.objects.get(name="Minion")

    return render(request, 'index.html', {
        'cards': cards,
        'health_coeff': MetaData.objects.get(name="health_coeff").value,
        'minion_attack_coeff': MetaData.objects.get(name="minion_attack_coeff").value,
        'minion_coeff': CardType.objects.get(name="Minion").value,
        'durability_coeff': MetaData.objects.get(name="durability_coeff").value,
        'weapon_attack_coeff': MetaData.objects.get(name="weapon_attack_coeff").value,
        'weapon_coeff': CardType.objects.get(name="Weapon").value,
        'spell_coeff': CardType.objects.get(name="Spell").value,
    })

# CARDS
def cards_index(request, card_type=None):
    if card_type:
        if len(card_type) > 1:
            card_type = card_type[0].upper() + card_type[1:].lower()
        else: # len == 1 or len == 0
            card_type = card_type.upper()

    if not card_type:
        cards = Card.objects.all()
    elif CardType.objects.filter(name=card_type):
        cards = Card.objects.filter(cardType__name__exact=card_type)
    else:
        raise Http404("No such card type")

    cards = cards.annotate(complex_delta=ExpressionWrapper(F('complex_value') - F('mana'), output_field=FloatField()))
    cards = cards.annotate(simple_delta=ExpressionWrapper(F('simple_value') - F('mana'), output_field=FloatField()))

    return render(request, 'cards/index.html', {
        'cards': cards,
        'card_type': card_type
    })

def cards_show(request, id):
    card = Card.objects.filter(id=id)

    if not card:
        raise Http404("No such card")

    card = card.annotate(complex_delta=ExpressionWrapper(F('complex_value') - F('mana'), output_field=FloatField()))
    card = card.annotate(simple_delta=ExpressionWrapper(F('simple_value') - F('mana'), output_field=FloatField()))
    card = card[0]

    mechanics = CardMechanic.objects.filter(card = card)
    return render(request, 'cards/show.html', {
        'card': card,
        'mechanics':mechanics
    })

# MECHANICS
def mechanics_index(request):
    mechanics = Mechanic.objects.all()

    return render(request, 'mechanics/index.html', {
        'mechanics': mechanics
    })

def mechanics_show(request, id):
    mechanic = Mechanic.objects.get(id=id)

    if not mechanic:
        raise Http404("No such mechanic")

    cardmechanics = CardMechanic.objects.filter(mechanic=mechanic)
    is_numeric = "%d" in mechanic.name

    return render(request, 'mechanics/show.html', {
        'mechanic': mechanic,
        'cardmechanics': cardmechanics,
        'is_numeric': is_numeric
    })

def create_random_card(request):
    params = request.POST

    response = {
        'user_mana': params.get('mana', 5),
    }

    if 'mana' in params:
        mana = int(params.get('mana'))
        response['card'] = card_generator.generate_card(mana)

    return render(request, 'create/index.html', response)
