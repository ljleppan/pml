import numpy as np

from cards.models import *
from .ridge_regression import ridge_regression
from .kernelized_ridge_regression import kernelized_ridge_regression
from .kernelized_ridge_regression import predict as kernel_predict

def learn():

    print("Getting myself an eduation")

    try:
        data = np.load("heathstonedata.npy")
        print(".npy get!")
    except Exception:
        print("It's fucked, jim! Loading data from DB. This WILL take time")
        data =  _data_as_numpy_array()
        print("Saving to disk as .npy")
        np.save("heathstonedata.npy", data)
        print(".npy saved")

    cards = data[:, 0]

    y = np.ascontiguousarray(data[:, 1], dtype=np.float)
    X = np.ascontiguousarray(data[:, 2:], dtype=np.float)

    # print("Learning with kernels")
    # cost_polynomial = _learn_polynomial(cards, X, y)

    print("Learning the boring way")
    cost_linear =_learn_linear(X, y)

    print("All done")
    return cost_linear
    #return (cost_linear, cost_polynomial)

def _learn_polynomial(cards, X, y):
    cost, coeffs = kernelized_ridge_regression(X, y)

    predictions = kernel_predict(X, coeffs)

    for i in range(X.shape[0]):
        cards[i].complex_value = predictions[i]
        cards[i].save()

    return cost

def _learn_linear(X, y):
    cost, coeffs = ridge_regression(X, y)

    MetaData.objects.filter(name="health_coeff").update(value=coeffs[0])
    MetaData.objects.filter(name="minion_attack_coeff").update(value=coeffs[1])
    MetaData.objects.filter(name="durability_coeff").update(value=coeffs[2])
    MetaData.objects.filter(name="weapon_attack_coeff").update(value=coeffs[3])

    # Since we are only doing updates, the post_save hooks do not get
    # called. So we need to ensure that all cards get their simple_value
    # fields refreshed. We do this by simply calling save() on a random
    # metadata field, which causes a refresh for all cards.
    MetaData.objects.first().save()

    coeffs = coeffs[4:]

    i = 0
    for ctype in CardType.objects.all().order_by('id'):
        ctype.value = coeffs[i]
        ctype.save()
        i+=1

    for race in Race.objects.all().order_by('id'):
        race.value = coeffs[i]
        race.save()
        i+=1

    for mechanic in Mechanic.objects.all().order_by('id'):
        mechanic.value = coeffs[i]
        mechanic.save()
        i += 1

    return cost

def _data_as_numpy_array():
    data = []
    for card in Card.objects.all():
        item = [
            card,
            card.mana,
        ]

        if card.cardType.name == "Minion":
            item.extend([card.health, card.attack, 0, 0])
        elif card.cardType.name == "Weapon":
            item.extend([0, 0, card.health, card.attack])
        else:
            item.extend([0, 0, 0, 0])

        for ctype in CardType.objects.all().order_by('id'):
            if card.cardType.id == ctype.id:
                item.append(1)
            else:
                item.append(0)

        for race in Race.objects.all().order_by('id'):
            if card.race.id == race.id:
                item.append(1)
            else:
                item.append(0)
        data.append(item)

    for mechanic in Mechanic.objects.all().order_by('id'):
        for item in data:
            card_mechanics = CardMechanic.objects.filter(card_id=item[0].id, mechanic_id=mechanic.id)
            if card_mechanics:
                item.append(card_mechanics.first().effect_size)
            else:
                item.append(0)
    data = np.array(data)
    return data
