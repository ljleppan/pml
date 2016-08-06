def ridge_regression(X, y):
    cv = 5
    best_cost = float('inf')
    best_lamba = None

    lambas = [lamba for lamba in np.linspace(0, 10, num = 11) if lamba >= 0]
    print("Lamba in {}".format(lambas))
    for lamba in lambas:
        if lamba == 0:
            lamba = 0.00001
        cost = _score_cv(X, y, lamba)
        if cost < best_cost:
            best_cost = cost
            best_lamba = lamba
    print("Best lamba: {} (cost: {})".format(best_lamba, best_cost))

    delta = 2
    for i in range(10):
        lambas = [lamba for lamba in np.linspace(best_lamba - delta, best_lamba + delta, num = 11) if lamba > 0.0001]
        delta = delta / 2
        print("Lamba in {}".format(lambas))
        for lamba in lambas:
            print(lamba)
            cost = _score_cv(X, y, lamba)
            if cost < best_cost:
                best_cost = cost
                best_lamba = lamba
        print("Best lamba: {} (cost: {})".format(best_lamba, best_cost))

    return (best_cost, _fit_ridge(X, y, lamba))

def _score_cv(X, y, lamba, cv=5):
    cost = 0
    for train, test in KFold(len(y), n_folds=cv):
        w = _fit_ridge(X[train], y[train], lamba)
        cost += _score_ridge(X[test], y[test], w)
    return cost / cv

def _fit_ridge(X, y, lamba):
    w = X.T.dot(X)
    w += np.eye(X.shape[1]).dot(lamba)
    w = np.linalg.inv(w)
    w = w.dot(X.T.dot(y))
    return w

def _score_ridge(X, y, w):
    cost = y - X.dot(w)
    return cost.T.dot(cost) / y.shape[0]

def _predict_ridge(X, w):
    return X.dot(w)
