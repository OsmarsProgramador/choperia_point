# usuario/views.py
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

# usuario: osmarnegao
# senha: 2324*-9+
"""
O uso do LoginRequiredMixin tem como objetivo garantir que apenas usuários autenticados possam acessar essa view.
Caso o usuário não esteja autenticado, o Django irá redirecionar o usuário para a página de login especificada.

Quando um usuário não está autenticada, a classe de redirecionamento, é aquela para 
o redirecionamento é configurado no arquivo settings.py, na variável LOGIN_URL. 
Essa variável define a URL para a qual o usuário será redirecionado quando uma view que 
requer autenticação for acessada por um usuário não autenticado.
configuração no settings.py: LOGIN_URL = 'usuario:login'

A classe de redirecionamento seria a UserLoginView

"""


class UserLoginView(View):  # Autentica e loga os usuários na aplicação
    def get(self, request):
        # Carregar todos os usuários, exceto o admin
        """Exibe a página de login carregando todos os usuários, exceto o usuário admin.
            A lista de usuários é passada para o template login.html, o que pode ser útil para 
            mostrar os usuários disponíveis para login ou outras finalidades administrativas."""
        usuarios = User.objects.exclude(username='admin')

        return render(request, 'usuario/login.html', {'usuarios': usuarios})

    def post(self, request):
        """
        Recebe os dados do formulário de login (username e password) enviados via POST.
        Autentica o usuário usando authenticate().
        Se a autenticação for bem-sucedida (user is not None), o usuário é logado com login() 
        e redirecionado para a página principal ('core:index').
        Se a autenticação falhar, retorna ao template login.html com uma mensagem de erro informando 
        que as credenciais são inválidas, além de recarregar a lista de usuários excluindo o admin."""
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('core:index')
        else:
            usuarios = User.objects.exclude(username='admin')
            return render(request, 'usuario/login.html', {'usuarios': usuarios, 'error': 'Credenciais inválidas'})

class UserLogoutView(View):  # logout do usuário atual usando a função logout(request), que encerra a sessão do usuário.
    def get(self, request):
        logout(request)
        return redirect('usuario:login')

class UserSignupView(View):  # Permite que novos usuários se registrem na aplicação. Realiza cadastro
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'usuario/cadastro.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save() # Salva o novo usuário diretamente no modelo User
            return redirect('usuario:login')
        return render(request, 'usuario/cadastro.html', {'form': form})

