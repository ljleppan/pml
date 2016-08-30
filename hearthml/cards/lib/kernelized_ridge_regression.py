from sklearn.cross_validation import KFold
import json
import numpy as np

def kernelized_ridge_regression(X, y):

    print("AAAAA")

    cv = 5
    best_cost = float('inf')
    best_lamba = None
    best_p = None

    scores = {}

    for p in range(1, 10):
        scores[p] = {}
        lambas = [lamba for lamba in np.linspace(0, 10, num = 11) if lamba >= 0]
        print("Lamba in {}".format(lambas))
        for lamba in lambas:
            if lamba <= 0:
                lamba = 0.0000001
            cost = _score_cv(X, y, lamba, p)
            scores[p][lamba] = cost
            if cost < best_cost:
                best_cost = cost
                best_lamba = lamba
                best_p = p
        print("Best lamba: {}, p: {} (cost: {})".format(best_lamba, best_p, best_cost))

        delta = 2
        for i in range(10):
            if best_lamba - delta >= 0:
                lambas = [lamba for lamba in np.linspace(best_lamba - delta, best_lamba + delta, num = 11)]
                delta = delta / 2
            else:
                lambas = [lamba for lamba in np.linspace(0, 2*delta, num = 11)]
                delta = delta / 4


            print("Lamba in {}".format(lambas))
            for lamba in lambas:
                if lamba <= 0:
                    lamba = 0.0000001
                #print(lamba)
                try:
                    cost = _score_cv(X, y, lamba, p)
                    scores[p][lamba] = cost
                    if cost < best_cost:
                        best_cost = cost
                        best_lamba = lamba
                except Exception:
                    pass
            print("Best lamba: {}, p: {} (cost: {})".format(best_lamba, best_p, best_cost))

    print(json.dumps(scores, sort_keys=True))
    return (best_cost, _fit(X, y, best_lamba, best_p))

def _score_cv(X, y, lamba, p, cv=5):
    cost = 0
    for train, test in KFold(len(y), n_folds=cv):
        w = _fit(X[train], y[train], lamba, p)
        cost += _score(X[test], y[test], w, lamba)
    return cost / cv

def _fit(X, y, lamba, p):
    K = (1 + X.dot(X.T))**p
    #K = np.zeros((X.shape[0], X.shape[0]))
    #for i in range(X.shape[0]):
    #    for j in range(X.shape[0]):
    #        K[i, j] = (1 + X[i].T.dot(X[j]))**3

    alpha = K
    alpha += np.eye(K.shape[1]).dot(lamba)
    alpha = np.linalg.inv(alpha)
    alpha = alpha.dot(y)

    w = X.T.dot(alpha)
    return w

def _score(X, y, w, lamba):
    cost = y - predict(X, w)
    return cost.T.dot(cost) / y.shape[0]  + (lamba * (w.T.dot(w)))

def predict(X, w):
    return X.dot(w)
