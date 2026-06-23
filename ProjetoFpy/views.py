from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from .models import Usuario, Aluguel, Espaco


desc_dubai = (
    'Localizado em Santa Cruz do Sul, o Dubai Eventos oferece uma estrutura moderna e completa para receber eventos '
    'de diferentes formatos e tamanhos. O espaco combina elegancia, conforto e funcionalidade, proporcionando o '
    'ambiente perfeito para celebracoes inesqueciveis. Com atendimento personalizado e uma estrutura preparada para '
    'receber seus convidados, o Dubai Eventos e a escolha ideal para quem busca qualidade e excelencia em cada ocasiao.'
)


def cria_espaco():
    e, criado = Espaco.objects.get_or_create(
        nome='Dubai Eventos',
        defaults={
            'endereco': 'R. Barao do Arroio Grande, 599 - Lot. Vila Nova, Santa Cruz do Sul - RS, 96835-213',
            'descricao': desc_dubai,
            'imagem1': 'ProjetoFpy/img/dubaieventos.jpg',
            'imagem2': 'ProjetoFpy/img/dubaiinterno.jpg',
            'imagem3': 'ProjetoFpy/img/palcodubai.webp',
        }
    )
    if not criado and e.descricao != desc_dubai:
        e.descricao = desc_dubai
        e.save()


def tela_inicial(request):
    if request.session.get('admin_logado'):
        return redirect('painel_admin')

    cria_espaco()
    espacos = Espaco.objects.all()
    nome = request.session.get('usuario_nome')

    alugados = set()
    if nome:
        u = Usuario.objects.filter(nome=nome).first()
        if u:
            alugados = set(Aluguel.objects.filter(usuario=u).values_list('espaco_id', flat=True))

    return render(request, 'home.html', {
        'usuario_nome': nome,
        'espacos': espacos,
        'alugados': alugados,
    })


def painel_admin(request):
    if not request.session.get('admin_logado'):
        return redirect('login')

    if request.method == 'POST':
        Espaco.objects.create(
            nome=request.POST.get('nome'),
            endereco=request.POST.get('endereco'),
            descricao=request.POST.get('descricao'),
            imagem1='ProjetoFpy/img/dubaieventos.jpg',
            imagem2='ProjetoFpy/img/dubaiinterno.jpg',
            imagem3='ProjetoFpy/img/palcodubai.webp'
        )
        return redirect('painel_admin')

    cria_espaco()
    return render(request, 'admin.html', {
        'usuarios': Usuario.objects.all(),
        'alugueis': Aluguel.objects.all(),
        'espacos': Espaco.objects.all()
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

        u = Usuario.objects.filter(Q(nome__iexact=nome) | Q(cpf=cpf_limpo)).first()

        if u and check_password(senha, u.senha):
            request.session['usuario_nome'] = u.nome
            request.session.pop('admin_logado', None)
            return redirect('tela_inicial')

        messages.error(request, "Nome ou senha invalidos.")

    return render(request, 'login.html')


def sair_view(request):
    request.session.flush()
    return redirect('login')


def descricao_view(request):
    cria_espaco()
    espaco_id = request.GET.get('espaco')
    espaco = Espaco.objects.filter(id=espaco_id).first()
    if not espaco:
        espaco = Espaco.objects.first()
    return render(request, 'descricao.html', {'espaco': espaco})


def disponibilidade_view(request):
    if request.method == 'POST':
        u = Usuario.objects.filter(nome=request.session.get('usuario_nome')).first()
        espaco = Espaco.objects.filter(id=request.POST.get('espaco_id')).first()

        Aluguel.objects.create(
            dia=request.POST.get('dia'),
            duracao=request.POST.get('duracao'),
            horarios=request.POST.get('horarios'),
            usuario=u,
            espaco=espaco,
        )
        return redirect('tela_inicial')

    espaco_id = request.GET.get('espaco')
    espaco = Espaco.objects.filter(id=espaco_id).first()
    if not espaco:
        espaco = Espaco.objects.first()
    return render(request, 'disponibilidade.html', {'espaco': espaco})


def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        confirmar = request.POST.get('confirmar_senha')
        cpf_limpo = ''.join(filter(str.isdigit, cpf))

        if senha != confirmar:
            messages.error(request, "As senhas nao coincidem!")
        elif len(cpf_limpo) != 11:
            messages.error(request, "O CPF deve ter exatamente 11 numeros.")
        elif cpf_limpo == cpf_limpo[0] * 11:
            messages.error(request, "CPF invalido! Numeros repetidos nao permitidos.")
        elif Usuario.objects.filter(cpf=cpf_limpo).exists():
            messages.error(request, "CPF ja cadastrado.")
        else:
            Usuario.objects.create(nome=nome, cpf=cpf_limpo, senha=make_password(senha))
            return redirect('login')

    return render(request, 'cadastro.html')