from django.shortcuts import render, redirect
from django.contrib import messages


def tela_inicial(request):
    return render(request, 'home.html')


def login_view(request):
    return render(request, 'login.html')


def descricao_view(request):
    return render(request, 'descricao.html')


def disponibilidade_view(request):
    return render(request, 'disponibilidade.html')


def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf_input = request.POST.get('cpf')
        senha = request.POST.get('senha')
        conf_senha = request.POST.get('confirmar_senha')

        cpf_limpo = ''.join(filter(str.isdigit, cpf_input))

        erros = False
        if senha != conf_senha:
            messages.error(request, "As senhas nao coincidem!")
            erros = True

        elif len(cpf_limpo) != 11:
            messages.error(request, "O CPF deve ter exatamente 11 numeros.")
            erros = True

        elif cpf_limpo == cpf_limpo[0] * 11:
            messages.error(request, "CPF invalido! Numeros repetidos nao permitidos.")
            erros = True

        if not erros:
            return redirect('login')

    return render(request, 'cadastro.html')
