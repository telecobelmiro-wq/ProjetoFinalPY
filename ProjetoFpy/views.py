from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from .models import Usuario, Aluguel, Espaco


HORARIOS = [
    '1:00', '2:00', '3:00', '4:00', '5:00', '6:00',
    '7:00', '8:00', '9:00', '10:00', '11:00', '12:00',
    '13:00', '14:00', '15:00', '16:00', '17:00', '18:00',
    '19:00', '20:00', '21:00', '22:00', '23:00', '00:00',
]


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


def get_usuario_logado(request):
    usuario_id = request.session.get('usuario_id')
    usuario = None

    if usuario_id:
        usuario = Usuario.objects.filter(id=usuario_id).first()

    if not usuario:
        usuario_nome = request.session.get('usuario_nome')
        if usuario_nome:
            usuario = Usuario.objects.filter(nome=usuario_nome).first()

    if usuario:
        request.session['usuario_id'] = usuario.id
        request.session['usuario_nome'] = usuario.nome
    else:
        request.session.pop('usuario_id', None)
        request.session.pop('usuario_nome', None)

    return usuario


def cpf_eh_valido(cpf):
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    primeiro_digito = (soma * 10 % 11) % 10
    if primeiro_digito != int(cpf[9]):
        return False

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    segundo_digito = (soma * 10 % 11) % 10
    return segundo_digito == int(cpf[10])


def tela_inicial(request):
    if request.session.get('admin_logado'):
        return redirect('painel_admin')

    cria_espaco()
    espacos = Espaco.objects.all()
    usuario = get_usuario_logado(request)
    nome = usuario.nome if usuario else None

    alugados = set()
    meus_alugueis = []
    if usuario:
        meus_alugueis = Aluguel.objects.filter(usuario=usuario).select_related('espaco').order_by('-criado_em')
        alugados = set(meus_alugueis.values_list('espaco_id', flat=True))

    return render(request, 'home.html', {
        'usuario_nome': nome,
        'espacos': espacos,
        'alugados': alugados,
        'meus_alugueis': meus_alugueis,
    })


def painel_admin(request):
    if not request.session.get('admin_logado'):
        return redirect('login')

    if request.method == 'POST':
        if request.POST.get('acao') == 'cancelar':
            Aluguel.objects.filter(id=request.POST.get('aluguel_id')).delete()
            messages.success(request, 'Reserva cancelada com sucesso.')
            return redirect('painel_admin')

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
        'alugueis': Aluguel.objects.select_related('usuario', 'espaco').all().order_by('-criado_em'),
        'espacos': Espaco.objects.all()
    })


def login_view(request):
    if request.session.get('admin_logado'):
        return redirect('painel_admin')

    if get_usuario_logado(request):
        return redirect('tela_inicial')

    nome = ''

    if request.method == 'POST':
        nome = request.POST.get('username', '').strip()
        senha = request.POST.get('password', '').strip()
        cpf_limpo = ''.join(filter(str.isdigit, nome))

        if not nome or not senha:
            messages.error(request, "Preencha nome/CPF e senha.")
        elif nome == 'admin' and senha == 'admin123':
            request.session.flush()
            request.session['admin_logado'] = True
            return redirect('painel_admin')
        else:
            filtro_usuario = Q(nome__iexact=nome)
            if cpf_limpo:
                filtro_usuario |= Q(cpf=cpf_limpo)

            u = Usuario.objects.filter(filtro_usuario).first()

            if u and check_password(senha, u.senha):
                request.session.flush()
                request.session['usuario_id'] = u.id
                request.session['usuario_nome'] = u.nome
                return redirect('tela_inicial')

            messages.error(request, "Nome/CPF ou senha invalidos.")

    return render(request, 'login.html', {'username': nome})


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


def pega_horarios_ocupados(espaco, dia):
    ocupados = []
    alugueis = Aluguel.objects.filter(espaco=espaco, dia=dia)

    for aluguel in alugueis:
        for hora in aluguel.horarios.split(','):
            hora = hora.strip()
            if hora and hora not in ocupados:
                ocupados.append(hora)

    return ocupados


def disponibilidade_view(request):
    usuario = get_usuario_logado(request)
    if not usuario:
        messages.error(request, 'Faca login para reservar um espaco.')
        return redirect('login')

    if request.method == 'POST':
        espaco = Espaco.objects.filter(id=request.POST.get('espaco_id')).first()
        dia = request.POST.get('dia', '').strip()
        duracao = request.POST.get('duracao', '').strip()
        horarios = request.POST.get('horarios', '').strip()
        horarios_lista = [h for h in horarios.split(',') if h]

        if not espaco:
            messages.error(request, 'Nao foi possivel encontrar o espaco.')
            return redirect('tela_inicial')

        if not dia or not duracao or not horarios_lista:
            messages.error(request, 'Preencha o dia, a duracao e escolha pelo menos um horario.')
            return redirect(f'/disponibilidade/?espaco={espaco.id}')

        ocupados = pega_horarios_ocupados(espaco, dia)
        conflito = [hora for hora in horarios_lista if hora in ocupados]

        if conflito:
            messages.error(request, 'Este horario ja esta reservado: ' + ', '.join(conflito))
            return redirect(f'/disponibilidade/?espaco={espaco.id}&dia={dia}')

        Aluguel.objects.create(
            dia=dia,
            duracao=duracao,
            horarios=horarios,
            usuario=usuario,
            espaco=espaco,
        )
        messages.success(request, 'Reserva criada com sucesso.')
        return redirect('tela_inicial')

    espaco_id = request.GET.get('espaco')
    dia = request.GET.get('dia', '')
    espaco = Espaco.objects.filter(id=espaco_id).first()
    if not espaco:
        espaco = Espaco.objects.first()
    ocupados = pega_horarios_ocupados(espaco, dia) if dia else []
    return render(request, 'disponibilidade.html', {
        'espaco': espaco,
        'horarios': HORARIOS,
        'ocupados': ocupados,
        'dia_selecionado': dia,
    })


def cancelar_aluguel_view(request, aluguel_id):
    aluguel = Aluguel.objects.filter(id=aluguel_id).select_related('usuario').first()

    if not aluguel:
        messages.error(request, 'Reserva nao encontrada.')
        return redirect('tela_inicial')

    usuario = get_usuario_logado(request)
    admin_logado = request.session.get('admin_logado')

    if admin_logado or (usuario and aluguel.usuario_id == usuario.id):
        aluguel.delete()
        messages.success(request, 'Reserva cancelada com sucesso.')
    else:
        messages.error(request, 'Voce nao tem permissao para cancelar esta reserva.')

    if admin_logado:
        return redirect('painel_admin')
    return redirect('tela_inicial')


def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        cpf = request.POST.get('cpf', '')
        senha = request.POST.get('senha', '').strip()
        confirmar = request.POST.get('confirmar_senha', '').strip()
        cpf_limpo = ''.join(filter(str.isdigit, cpf))

        if not nome or not cpf_limpo or not senha or not confirmar:
            messages.error(request, "Preencha todos os campos.")
        elif senha != confirmar:
            messages.error(request, "As senhas nao coincidem!")
        elif not cpf_eh_valido(cpf_limpo):
            messages.error(request, "CPF invalido.")
        elif Usuario.objects.filter(cpf=cpf_limpo).exists():
            messages.error(request, "CPF ja cadastrado.")
        elif Usuario.objects.filter(nome__iexact=nome).exists():
            messages.error(request, "Nome ja cadastrado. Use outro nome ou entre pelo CPF.")
        else:
            Usuario.objects.create(nome=nome, cpf=cpf_limpo, senha=make_password(senha))
            messages.success(request, "Cadastro realizado. Agora voce ja pode entrar.")
            return redirect('login')

    return render(request, 'cadastro.html')
