import pytest
import torch
from torch import nn

from laplace.jacobians import Jacobians
from tests.utils import Jacobians_naive


@pytest.fixture
def multioutput_model():
    model = torch.nn.Sequential(nn.Linear(3, 20), nn.Linear(20, 2))
    setattr(model, 'output_size', 2)
    return model


@pytest.fixture
def singleoutput_model():
    model = torch.nn.Sequential(nn.Linear(3, 20), nn.Linear(20, 1))
    setattr(model, 'output_size', 1)
    return model


@pytest.fixture
def linear_model():
    model = torch.nn.Sequential(nn.Linear(3, 1, bias=False))
    setattr(model, 'output_size', 1)
    return model


@pytest.fixture
def X():
    torch.manual_seed(15)
    return torch.randn(200, 3)


def test_linear_jacobians(linear_model, X):
    # jacobian of linear model is input X.
    Js, f = Jacobians(linear_model, X)
    # into Jacs shape (batch_size, output_size, params)
    true_Js = X.reshape(len(X), 1, -1)
    assert true_Js.shape == Js.shape
    assert torch.allclose(true_Js, Js, atol=1e-5)
    assert torch.allclose(f, linear_model(X), atol=1e-5)


def test_jacobians_singleoutput(singleoutput_model, X):
    model = singleoutput_model
    Js, f = Jacobians(model, X)
    Js_naive, f_naive = Jacobians_naive(model, X)
    assert Js.shape == Js_naive.shape
    assert torch.abs(Js-Js_naive).max() < 1e-6
    assert torch.allclose(model(X), f_naive)
    assert torch.allclose(f, f_naive)


def test_jacobians_multioutput(multioutput_model, X):
    model = multioutput_model
    Js, f = Jacobians(model, X)
    Js_naive, f_naive = Jacobians_naive(model, X)
    assert Js.shape == Js_naive.shape
    assert torch.abs(Js-Js_naive).max() < 1e-6
    assert torch.allclose(model(X), f_naive)
    assert torch.allclose(f, f_naive)