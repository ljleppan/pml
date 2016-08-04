from sklearn.preprocessing import PolynomialFeatures
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import LassoCV, LinearRegression, RidgeCV
from sklearn.pipeline import Pipeline
from sklearn import cross_validation

import numpy as np

from cards.models import *

def learn():

    print("Doing thing!")

    try:
        data = np.load("heathstonedata.npy")
        print("Loaded from disk")
    except Exception:
        print("Fucked up, loading from DB")
        data =  _data_as_numpy_array()
        print("Saving to disk")
        np.save("heathstonedata.npy", data)
        print("Done!")

    cards = data[:, 0]

    y = np.ascontiguousarray(data[:, 1], dtype=np.int)
    X = np.ascontiguousarray(data[:, 2:], dtype=np.int)

    _learn_polynomial(cards, X, y)
    _learn_linear(X, y)

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

    best_model = None
    best_accuracy = float("-inf")
    for model in [LinearRegression(), LassoCV(cv=3), RidgeCV(cv=3)]:
        scores = cross_validation.cross_val_score(
            model,
            X,
            y,
            scoring="mean_squared_error",
            cv=4
        )
        print("Linear model accuracy for %s: %0.5f (+/- %0.5f)" % (model.__class__.__name__, scores.mean(), scores.std() * 2))
        if scores.mean() > best_accuracy:
            best_accuracy = scores.mean()
            best_model = model

    model = best_model
    model.fit(X, y)

    print("Using " + str(model))

    coeffs = model.coef_
    MetaData.objects.filter(name="health_coeff").update(value=coeffs[0])
    MetaData.objects.filter(name="attack_coeff").update(value=coeffs[1])
    coeffs = coeffs[2:]

    i = 0
    for ctype in CardType.objects.all().order_by('id'):
        ctype.value = coeffs[i]
        ctype.save()
        i+=1

    for mechanic in Mechanic.objects.all().order_by('id'):
        mechanic.value = coeffs[i]
        mechanic.save()
        i += 1

def _data_as_numpy_array():
    data = []
    for card in Card.objects.all():
        item = [
            card,
            card.mana,
            card.health,
            card.attack,
        ]
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
