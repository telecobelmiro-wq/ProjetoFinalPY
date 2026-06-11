from django.shortcuts import render, redirect
from django.contrib import messages

def tela_inicial(request):
    return render(request, 'home.html')

def login_view(request):
    return render(request, 'login.html') 

def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf_input = request.POST.get('cpf')
        senha = request.POST.get('senha')
        conf_senha = request.POST.get('confirmar_senha')

        # 1. Limpa o CPF (deixa só números)
        cpf_limpo = ''.join(filter(str.isdigit, cpf_input))

        erros = False

        # Validação das senhas
        if senha != conf_senha:
            messages.error(request, "As senhas não coincidem!")
            erros = True
        
        # Validação do tamanho do CPF
        elif len(cpf_limpo) != 11:
            messages.error(request, "O CPF deve ter exatamente 11 números.")
            erros = True
        
        # Validação de números repetidos (Ex: 11111111111)
        elif cpf_limpo == cpf_limpo[0] * 11:
            messages.error(request, "CPF inválido! Números repetidos não permitidos.")
            erros = True

        # Se passou em tudo sem erros, redireciona para a tela de login
        if not erros:
            return redirect('login')

    return render(request, 'cadastro.html')