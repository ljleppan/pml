from django.conf import settings
from django.http import HttpResponse
from cards.models import *
import urllib
import json
import re
from sklearn.linear_model import LinearRegression
import numpy as np

def index(request):
    return HttpResponse("Hello, world. This is the CARDS index.")

def populate_db(request):
    request = "https://omgvamp-hearthstone-v1.p.mashape.com/cards/types/Minion?mashape-key=XXXXXXXXXX"
    response = urllib.request.urlopen(request)
    str_response = response.readall().decode('utf-8')
    obj = json.loads(str_response)

    _ensure_simple()
    _process_cards(obj)

    #_build_values()

    return HttpResponse("Done!")

def learn(request):
    data = _build_values()
    cards = data[:, 0]
    y = data[:, 1]
    X = data[:, 2:]

    model = LinearRegression()
    model.fit(X, y)
    predictions = model.predict(X)

    for i in range(X.shape[0]):
        cards[i].value = predictions[i]
        cards[i].save()

    return HttpResponse(model.score(X, y))

def _ensure_simple():
    simple_mechanics = [
        'Taunt',
        'Stealth',
        'Charge',
        'Divine Shield',
        'Windfury'
    ]

    for s in simple_mechanics:
        if Mechanic.objects.filter(name=s).count() == 0:
            mechanic = Mechanic(name=s, value=1)
            mechanic.save()

    if Faction.objects.filter(name='Neutral').count() == 0:
        faction = Faction(name='Neutral', value=1)
        faction.save()
    if Race.objects.filter(name='None').count() == 0:
        race = Race(name='None', value=1)
        race.save()
    if Rarity.objects.filter(name='Free').count() == 0:
        r = Rarity(name='Free', value=1)
        r.save()


def _process_cards(data):
    for card in data:
        _process_single(card)

def _process_single(card):

    if 'XXX_' in card['cardId']:
        return # skip as debug card

    db_card = None
    if Card.objects.filter(cardId=card['cardId']).count() == 0:
        db_card = Card(cardId=card['cardId'],name=card['name'])
    else:
        db_card = Card.objects.get(cardId=card['cardId'])

    if 'health' in card:
        db_card.health = card['health']
    else:
        db_card.health = 0

    if 'attack' in card:
        db_card.attack = card['attack']
    else:
        db_card.attack = 0

    if 'cost' in card:
        db_card.cost = card['cost']
    else:
        db_card.cost = 0

    db_card.value = 0

    if 'cardSet' in card:
        if CardSet.objects.filter(name=card['cardSet']).count() == 0:
            cardSet = CardSet(name=card['cardSet'], value=1)
            cardSet.save()
        db_card.cardSet = CardSet.objects.get(name=card['cardSet'])

    if 'type' in card:
        if CardType.objects.filter(name=card['type']).count() == 0:
            cardType = CardType(name=card['type'], value=1)
            cardType.save()
        db_card.cardType = CardType.objects.get(name=card['type'])

    if 'faction' in card:
        if Faction.objects.filter(name=card['faction']).count() == 0:
            faction = Faction(name=card['faction'], value=1)
            faction.save()
        db_card.faction = Faction.objects.get(name=card['faction'])
    else:
        db_card.faction = Faction.objects.get(name='Neutral')

    if 'rarity' in card:
        if Rarity.objects.filter(name=card['rarity']).count() == 0:
            rarity = Rarity(name=card['rarity'], value=1)
            rarity.save()
        db_card.rarity = Rarity.objects.get(name=card['rarity'])
    else:
        db_card.rarity = Rarity.objects.get(name="Free")

    if 'race' in card:
        if Race.objects.filter(name=card['race']).count() == 0:
            race = Race(name=card['race'], value=1)
            race.save()
        db_card.race = Race.objects.get(name=card['race'])
    else:
        db_card.race = Race.objects.get(name='None')

    if 'playerClass' in card:
        if CharacterClass.objects.filter(name=card['playerClass']).count() == 0:
            character_class = CharacterClass(name=card['playerClass'], value=1)
            character_class.save()
        db_card.playerClass = CharacterClass.objects.get(name=card['playerClass'])

    db_card.save()

    _update_mechanics(card, db_card)



def _update_mechanics(card, db_card):

    if not 'text' in card:
        return

    m = card['text']

    m = m.replace('[x]', '')
    m = m.replace('<b>', '')
    m = m.replace('</b>', '')
    m = m.replace('<i>', '')
    m = m.replace('</i>', '')

    # Such horrors

    simple_mechanics = [
        'Taunt',
        'Stealth',
        'Charge',
        'Divine Shield',
        'Windfury'
    ]

    any_match = True
    while any_match:
        any_match = False
        for s in simple_mechanics:
            if m.startswith(s):
                any_match = True

                db_card.mechanics.add(Mechanic.objects.get(name=s))

                m = m[len(s):]
                for i in range(2):
                    if len(m) == 0:
                        return
                    if m[0] == "." or m[0] == ",":
                        m = m[1:]
                    m = m.strip()

    if len(m) <= 1:
        return

    if m[0] == "." or m[0] == ",":
        m = m[1:]

    m = m.strip()

    if "".join(m.split()) == "":
        # Skip if whitespace only
        return

    if Mechanic.objects.filter(name=m).count() == 0:
        mechanic = Mechanic(name=m, value=1)
        mechanic.save()
    db_card.mechanics.add(Mechanic.objects.get(name=m))

    db_card.save()


def _build_values():
    return _data_as_numpy_array()


def _data_as_numpy_array():
    data = []
    for card in Card.objects.all():
        this = [
            card,
            card.cost,
            card.health,
            card.attack,
            #card.cardSet.id,
            card.cardType.id,
            card.faction.id,
            card.rarity.id,
            card.race.id,
            #card.character_class.id
        ]
        data.append(this)
    for mechanic in Mechanic.objects.all().order_by('id'):
        for item in data:
            if item[0].mechanics.filter(pk=mechanic.id):
                item.append(1)
            else:
                item.append(0)
    data = np.array(data)
    return data
