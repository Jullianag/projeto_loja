from django.shortcuts import render, get_object_or_404, redirect   # noqa
from django.views.generic.list import ListView  # noqa
from django.views import View
from . import models
from django.contrib.auth.models import User
import copy
from django.contrib.auth import authenticate, login, logout
from . import forms
from django.contrib import messages


class BasePerfil(View):
    template_name = 'perfil/criar.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.carrinho = copy.deepcopy(self.request.session.get('carrinho', {}))   # noqa

        self.perfil = None  # noqa

        if self.request.user.is_authenticated:
            self.perfil = models.Perfil.objects.filter(   # noqa
                usuario=self.request.user
            ).first()

            self.contexto = {
                'userform': forms.UserForm(  # noqa
                    data=self.request.POST or None,
                    usuario=self.request.user,
                    instance=self.request.user,
                ),
                'perfilform': forms.PerfilForm(    # noqa
                    data=self.request.POST or None,
                    instance=self.perfil
                )
            }
        else:
            self.contexto = {    # noqa
                'userform': forms.UserForm(    # noqa
                    data=self.request.POST or None
                ),
                'perfilform': forms.PerfilForm(  # noqa
                    data=self.request.POST or None
                )
            }

        self.userform = self.contexto['userform']  # noqa
        self.perfilform = self.contexto['perfilform']  # noqa

        if self.request.user.is_authenticated:
            self.template_name = 'perfil/atualizar.html'  # noqa

        self.renderizar = render(    # noqa
            self.request, self.template_name, self.contexto)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.perfilform.is_valid():
            return self.renderizar

        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')

        # usuário logado
        if self.request.user.is_authenticated:
            usuario = get_object_or_404(
                User, username=self.request.user.username
            )
            usuario.username = username

            if password:
                usuario.set_password(password)

            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()

            if not self.perfil:
                self.perfilform.cleaned_data['usuario'] = usuario   # noqa
                perfil = models.Perfil(**self.perfilform.cleaned_data)
                perfil.save()

            else:
                perfil = self.perfilform.save(commit=False)   # noqa
                perfil.usuario = usuario  # noqa
                perfil.save()

            messages.error(
                self.request,
                'Existem erros no seu formulário de cadastro, verifique os campos!'
            )

        # usuario não logado
        else:
            usuario = self.userform.save(commit=False)   # noqa
            usuario.set_password(password)
            usuario.save()

            perfil = self.perfilform.save(commit=False)   # noqa
            perfil.usuario = usuario   # noqa
            perfil.save()

        if password:
            autentica = authenticate(self.request, username=usuario, password=password)

            if autentica:
                login(self.request, user=usuario)

        self.request.session['carrinho'] = self.carrinho    # noqa
        self.request.session.save()

        messages.success(
            self.request,
            'Seu cadastro foi criado ou atualizado com sucesso!'
        )
        messages.success(
            self.request,
            'Você fez login e pode concluir sua compra!'
        )

        return redirect('produto:carrinho')   # noqa


class Atualizar(View):
    pass


class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        if not username or not password:
            messages.error(
                self.request,
                'Usuário ou senha inválidos!'   # noqa
            )
            return redirect('prefil:criar')   # noqa

        usuario = authenticate(
            self.request, username=username, password=password
        )

        if not usuario:
            messages.error(
                self.request,
                'Usuário ou senha inválidos!'  # noqa
            )
            return redirect('perfil:criar')   # noqa

        login(self.request, user=usuario)

        messages.success(
            self.request,
            'Você fez login no sistema e pode concluir seu compra'
        )

        return redirect('produto:carrinho')  # noqa


class Logout(View):
    def get(self, *args, **kwargs):
        carrinho = copy.deepcopy(self.request.session.get('carrinho'))   # noqa

        logout(self.request)

        self.request.session['carrinho'] = carrinho
        self.request.session.save()
        return redirect('produto:lista')  # noqa
