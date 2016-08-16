from sklearn.cross_validation import KFold
import numpy as np

def kernelized_ridge_regression(X, y):
    cv = 5
    best_cost = float('inf')
    best_lamba = None
    best_p = None

    for p in range(1, 15):
        lambas = [lamba for lamba in np.linspace(0, 10, num = 11) if lamba >= 0]
        print("Lamba in {}".format(lambas))
        for lamba in lambas:
            if lamba == 0:
                lamba = 0.00001
            cost = _score_cv(X, y, lamba, p)
            if cost < best_cost:
                best_cost = cost
                best_lamba = lamba
                best_p = p
        print("Best lamba: {}, p: {} (cost: {})".format(best_lamba, best_p, best_cost))

        delta = 2
        for i in range(10):
            lambas = [lamba for lamba in np.linspace(best_lamba - delta, best_lamba + delta, num = 11) if lamba > 0.0001]
            delta = delta / 2
            print("Lamba in {}".format(lambas))
            for lamba in lambas:
                #print(lamba)
                cost = _score_cv(X, y, lamba, p)
                if cost < best_cost:
                    best_cost = cost
                    best_lamba = lamba
            print("Best lamba: {}, p: {} (cost: {})".format(best_lamba, best_p, best_cost))

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
