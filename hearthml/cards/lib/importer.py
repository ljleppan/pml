import urllib
import json
import re
from cards.models import *

MASHAPE_KEY = "ADD_KEY_HERE"

def import_cards():
        types = ['Minion', 'Spell', 'Weapon']
        for card_type in types:
            request =  "https://omgvamp-hearthstone-v1.p.mashape.com/cards/types/%s?collectible=1&mashape-key=%s" % (card_type, MASHAPE_KEY)
            response = urllib.request.urlopen(request)
            str_response = response.read().decode('utf-8')
            _process_cards(json.loads(str_response))


def _process_cards(data):

    MetaData.objects.update_or_create(
        name="health_coeff",
        defaults = {
            'value': 0
        }
    )
    MetaData.objects.update_or_create(
        name="minion_attack_coeff",
        defaults = {
            'value': 0
        }
    )
    MetaData.objects.update_or_create(
        name="durability_coeff",
        defaults = {
            'value': 0
        }
    )
    MetaData.objects.update_or_create(
        name="weapon_attack_coeff",
        defaults = {
            'value': 0
        }
    )

    for card in data:
        _process_single(card)

def _process_single(card):

    if 'XXX_' in card['cardId']:
        return # skip as debug card

    db_card = Card.objects.update_or_create(
        cardId = card.get('cardId'),
        defaults = {
            'name': card.get('name'),
            'health': card.get('health', card.get('durability', 0)),
            'attack': card.get('attack', 0),
            'mana': card.get('cost', 0),
            'text': card.get('text', ""),
            'image': card.get('img', ''),
            'complex_value': 0,
            'simple_value': 0,
            'cardSet': CardSet.objects.get_or_create(
                name=card.get("cardSet", "Default"),
                defaults = {
                    'value': 0
                }
            )[0],
            'cardType': CardType.objects.get_or_create(
                name=card.get("type", "Default"),
                defaults = {
                    'value': 0
                }
            )[0],
            'faction': Faction.objects.get_or_create(
                name=card.get("faction", "Neutral"),
                defaults = {
                    'value': 0
                }
            )[0],
            'rarity': Rarity.objects.get_or_create(
                name=card.get("rarity", "Free"),
                defaults = {
                    'value': 0
                }
            )[0],
            'race': Race.objects.get_or_create(
                name=card.get("race", "None"),
                defaults = {
                    'value': 0
                }
            )[0],
            'character_class': CharacterClass.objects.get_or_create(
                name=card.get("playerClass", "All"),
                defaults = {
                    'value': 0
                }
            )[0]
        }
    )[0]

    _update_mechanics(card, db_card)


def _update_mechanics(card, db_card):

    if not 'text' in card:
        return

    text = card['text']

    text = text.replace('[x]', '')
    text = text.replace('<b>', '')
    text = text.replace('</b>', '')
    text = text.replace('<i>', '')
    text = text.replace('</i>', '')
    text = text.replace('$', '')
    text = text.replace('#', '')
    text = text.replace('\n', ' ')

    # Jousting as a single mechanic
    text = text.replace('Reveal a minion in each deck.', 'Reveal a minion in each deck:')

    # Fix Brawl, BoK etc.
    text = text.replace('. (', ' (')

    # Fix Elemental Destruction
    text = text.replace('Overload: (5),', 'Overload: (5)')

    # Fix Dunemaul Shaman
    text = text.replace('Overload: (1) 50%', 'Overload: (1). 50%')

    # Do simple mechanics separately since Blizz can't decide on a standard way
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
        if len(text) < 3:
            continue
        for simple in simple_mechanics:
            if text.startswith(simple):
                any_match = True

                CardMechanic.objects.update_or_create(
                    card = db_card,
                    mechanic = Mechanic.objects.get_or_create(
                        name = simple,
                        defaults = {
                            'value': 0
                        }
                    )[0],
                    defaults = {
                        'effect_size': 1
                    }
                )

                text = text[len(simple):]
                while text != "" and (text[0] == "." or text[0] == ","):
                    text = text[1:].strip()

    # Not a simple thing
    single_number_regex = re.compile("^\D*(\d+)\D*$")
    range_regex = re.compile("^\D*(\d+)-(\d+)\D*$")

    any_match = True
    while any_match:
        any_match = False

        text = text.strip()
        if len(text) < 3:
            return
        if "." in text:
            first_dot = text.find(".")
            mechanic = text[:first_dot].strip()
            text = text[first_dot+1:]
        else:
            mechanic = text
            text = ""

        match = range_regex.match(mechanic.lower())
        if match:
            any_match = True
            avg = (float(match.group(1)) + float(match.group(2)))/2
            mechanic = mechanic.replace(match.group(1), "%d")
            mechanic = mechanic.replace(match.group(2), "%d")
            mechanic = "%s (± %0.1f)" % (mechanic, float(avg - float(match.group(1))))
            CardMechanic.objects.update_or_create(
                card = db_card,
                mechanic = Mechanic.objects.get_or_create(
                    name = mechanic,
                    defaults = {
                        'value': 0
                    }
                )[0],
                defaults = {
                    'effect_size': (float(match.group(1)) + float(match.group(2)))/2
                }
            )
            continue

        match = single_number_regex.match(mechanic.lower())
        if match:
            any_match = True
            mechanic = mechanic.replace(match.group(1), "%d")
            CardMechanic.objects.update_or_create(
                card = db_card,
                mechanic = Mechanic.objects.get_or_create(
                    name = mechanic,
                    defaults = {
                        'value': 0
                    }
                )[0],
                defaults = {
                    'effect_size': match.group(1)
                }
            )
            continue

        # Didn't match any, saving as is
        any_match = True
        CardMechanic.objects.update_or_create(
            card = db_card,
            mechanic = Mechanic.objects.get_or_create(
                name = mechanic,
                defaults = {
                    'value': 0
                }
            )[0],
            defaults = {
                'effect_size': 1
            }
        )
