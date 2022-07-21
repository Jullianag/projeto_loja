from django import forms
from . import models
from django.contrib.auth.models import User


class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil
        fields = '__all__'
        exclude = ('usuario',)


class UserForm(forms.ModelForm):

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Senha'
    )

    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Confirmação senha'
    )

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.usuario = usuario

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'password2', 'email')

    def clean(self, *args, **kwargs):
        data = self.data  # noqa
        cleaned = self.cleaned_data
        validation_error_msg = {}

        usuario_data = cleaned.get('username')
        password_data = cleaned.get('password')
        password2_data = cleaned.get('password2')
        email_data = cleaned.get('email')

        usuario_db = User.objects.filter(username=usuario_data).first()
        email_db = User.objects.filter(email=email_data).first()

        error_msg_user_exists = 'Usuáro já existe na base de dados!'
        error_msg_email_exists = 'E-mail já existe na base de dados!'
        error_msg_password_match = 'As duas senhas devem ser iguais!'
        error_msg_password_short = 'A senha precisa conter pelo menos 6 caracteres!'
        error_msg_required_field = 'Este campo é obrigatório!'  # noqa

        #  Usuário logado
        if self.usuario:

            if usuario_db:
                if usuario_data != usuario_db.username:
                    validation_error_msg['username'] = error_msg_user_exists

            if email_db:
                if email_data != email_db.email:
                    validation_error_msg['email'] = error_msg_email_exists

            if password_data:
                if password_data != password2_data:
                    validation_error_msg['password'] = error_msg_password_match
                    validation_error_msg['password2'] = error_msg_password_match

            if len(password_data) < 6:
                validation_error_msg['password'] = error_msg_password_short
        else:
            pass

        if validation_error_msg:
            raise(forms.ValidationError(validation_error_msg))
