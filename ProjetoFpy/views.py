from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from .models import Usuario, Aluguel

def tela_inicial(request):
    if request.session.get('admin_logado'):
        return redirect('painel_admin')

    return render(request, 'home.html', {
        'usuario_nome': request.session.get('usuario_nome')
    })


def painel_admin(request):
    if not request.session.get('admin_logado'):
        return redirect('login')

    usuarios = Usuario.objects.all()
    alugueis = Aluguel.objects.all()

    return render(request, 'admin.html', {
        'usuarios': usuarios,
        'alugueis': alugueis
    })

def login_view(request):
    if request.method == 'POST':
        nome = request.POST.get('username').strip()
        senha = request.POST.get('password').strip()
        cpf_limpo = ''.join(filter(str.isdigit, nome))

        if nome == 'admin' and senha == 'admin123':
            request.session['admin_logado'] = True
            request.session.pop('usuario_nome', None)
            return redirect('painel_admin')

        usuario = Usuario.objects.filter(
            Q(nome__iexact=nome) | Q(cpf=cpf_limpo)
        ).first()

        if usuario:
            if check_password(senha, usuario.senha):
                request.session['usuario_nome'] = usuario.nome
                request.session.pop('admin_logado', None)
                return redirect('tela_inicial')

        messages.error(request, "Nome ou senha invalidos.")

    return render(request, 'login.html')


def sair_view(request):
    request.session.flush()
    return redirect('login')


def descricao_view(request):
    return render(request, 'descricao.html')


def disponibilidade_view(request):
    if request.method == 'POST':
        dia = request.POST.get('dia')
        duracao = request.POST.get('duracao')
        horarios = request.POST.get('horarios')

        Aluguel.objects.create(
            dia=dia,
            duracao=duracao,
            horarios=horarios
        )

        return redirect('tela_inicial')

    return render(request, 'disponibilidade.html')


def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        confirmar = request.POST.get('confirmar_senha')

        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        erro = False

        if senha != confirmar:
            messages.error(request, "As senhas nao coincidem!")
            erro = True

        elif len(cpf_limpo) != 11:
            messages.error(request, "O CPF deve ter exatamente 11 numeros.")
            erro = True

        elif cpf_limpo == cpf_limpo[0] * 11:
            messages.error(request, "CPF invalido! Numeros repetidos nao permitidos.")
            erro = True

        elif Usuario.objects.filter(cpf=cpf_limpo).exists():
            messages.error(request, "CPF ja cadastrado.")
            erro = True

        if erro == False:
            Usuario.objects.create(
                nome=nome,
                cpf=cpf_limpo,
                senha=make_password(senha)
            )

            return redirect('login')
    return render(request, 'cadastro.html')
