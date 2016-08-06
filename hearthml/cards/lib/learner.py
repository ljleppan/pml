from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import RidgeCV
from sklearn.cross_validation import KFold

import numpy as np

from cards.models import *
from .ridge_regression import ridge_regression

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

    print("Learning with kernels")
     #_learn_polynomial(cards, X, y)

    print("Learning the boring way")
    cost_linear =_learn_linear(X, y)

    print("All done")
    return cost_linear

def _learn_polynomial(cards, X, y):
    model = KernelRidge()
    model.fit(X, y)
    predictions = model.predict(X)

    for i in range(X.shape[0]):
        cards[i].complex_value = predictions[i]
        cards[i].save()

    scores = cross_validation.cross_val_score(
        model,
        X,
        y,
        scoring="mean_squared_error",
        cv=4
    )

    print("Complex model accuracy: %0.5f (+/- %0.5f)" % (scores.mean(), scores.std() * 2))

def _learn_linear(X, y):
    cost, coeffs = ridge_regression(X, y)

    MetaData.objects.filter(name="health_coeff").update(value=coeffs[0])
    MetaData.objects.filter(name="minion_attack_coeff").update(value=coeffs[1])
    MetaData.objects.filter(name="durability_coeff").update(value=coeffs[2])
    MetaData.objects.filter(name="weapon_attack_coeff").update(value=coeffs[3])
    coeffs = coeffs[4:]

    i = 0
    for ctype in CardType.objects.all().order_by('id'):
        ctype.value = coeffs[i]
        ctype.save()
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
