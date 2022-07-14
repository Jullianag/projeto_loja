from django.shortcuts import render   # noqa
from django.views.generic.list import ListView
from django.views import View


class ListaProduto(ListView):
    pass


class DetalheProduto(View):
    pass


class AdicionarAoCarrinho(View):
    pass


class RemoverDoCarrinho(View):
    pass


class Carrinho(View):
    pass


class Finalizar(View):
    pass
