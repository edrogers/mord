import numpy as np
from scipy import stats, optimize, linalg
import mord
from nose.tools import assert_almost_equal, assert_less

np.random.seed(0)
from sklearn import datasets, metrics, svm, cross_validation, linear_model
n_class = 5
n_samples = 100
n_dim = 80

X, y = datasets.make_regression(n_samples=n_samples, n_features=n_dim,
    n_informative=n_dim // 10, noise=20.)
bins = stats.mstats.mquantiles(y, np.linspace(0, 1, n_class + 1))
y = np.digitize(y, bins[:-1])
y -= y.min()

def test_1():
    """
    Test two model in overfit mode
    """
    clf = mord.LogisticAT(alpha=0.)
    clf.fit(X, y)
    # the score is - absolute error, 0 is perfect
    assert_almost_equal(clf.score(X, y), 0., places=2)

    clf = mord.LogisticIT(alpha=0.)
    clf.fit(X, y)
    # the score is classification error, 1 is perfect
    assert_almost_equal(clf.score(X, y), 1., places=2)


def test_grad():
    x0 = np.random.randn(n_dim + n_class - 1)
    x0[n_dim+1:] = np.abs(x0[n_dim+1:])

    loss_fd = np.diag(np.ones(n_class - 1)) + \
        np.diag(np.ones(n_class - 2), k=-1)
    loss_fd = np.vstack((loss_fd, np.zeros(n_class -1)))
    loss_fd[-1, -1] = 1  # border case

    L = np.eye(n_class - 1) - np.diag(np.ones(n_class - 2), k=-1)


    fun = lambda x: mord.threshold_based.obj_margin(
        x, X, y, 100.0, n_class, loss_fd, L)
    grad = lambda x: mord.threshold_based.grad_margin(
        x, X, y, 100.0, n_class, loss_fd, L)
    assert_less(optimize.check_grad(fun, grad, x0),  0.1)


def test_binary_class():
    Xc, yc = datasets.make_classification(n_classes=2, n_samples=1000)
    clf = linear_model.LogisticRegression(C=1e6)
    clf.fit(Xc[:500], yc[:500])
    pred_lr = clf.predict(Xc[500:])

    clf = mord.LogisticAT(alpha=1e-6)
    clf.fit(Xc[:500], yc[:500])
    pred_at = clf.predict(Xc[500:])
    assert_almost_equal(np.abs(pred_lr - pred_at).mean(), 0.)

    clf2 = mord.LogisticSE(alpha=1e-6)
    clf2.fit(Xc[:500], yc[:500])
    pred_at = clf2.predict(Xc[500:])
    assert_almost_equal(np.abs(pred_lr - pred_at).mean(), 0.)
