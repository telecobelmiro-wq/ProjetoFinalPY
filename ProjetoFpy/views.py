from datetime import date

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from .models import Usuario, Aluguel, Configuracao, Espaco, EspacoImagem


HORARIOS = [
    '1:00', '2:00', '3:00', '4:00', '5:00', '6:00',
    '7:00', '8:00', '9:00', '10:00', '11:00', '12:00',
    '13:00', '14:00', '15:00', '16:00', '17:00', '18:00',
    '19:00', '20:00', '21:00', '22:00', '23:00', '00:00',
]


ESPACO_PADRAO_CHAVE = 'espaco_padrao_criado'


desc_dubai = (
    'Localizado em Santa Cruz do Sul, o Dubai Eventos oferece uma estrutura moderna e completa para receber eventos '
    'de diferentes formatos e tamanhos. O espaco combina elegancia, conforto e funcionalidade, proporcionando o '
    'ambiente perfeito para celebracoes inesqueciveis. Com atendimento personalizado e uma estrutura preparada para '
    'receber seus convidados, o Dubai Eventos e a escolha ideal para quem busca qualidade e excelencia em cada ocasiao.'
)


def cria_espaco():
    _, criado = Configuracao.objects.get_or_create(chave=ESPACO_PADRAO_CHAVE)
    if not criado or Espaco.objects.exists():
        return

    Espaco.objects.create(
        nome='Dubai Eventos',
        endereco='R. Barao do Arroio Grande, 599 - Lot. Vila Nova, Santa Cruz do Sul - RS, 96835-213',
        descricao=desc_dubai,
        imagem1='ProjetoFpy/img/dubaieventos.jpg',
        imagem2='ProjetoFpy/img/dubaiinterno.jpg',
        imagem3='ProjetoFpy/img/palcodubai.webp',
    )


def entrada_view(request):
    request.session.flush()
    return redirect('login')


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


def email_eh_valido(email):
    try:
        validate_email(email)
    except ValidationError:
        return False
    return True


def imagens_invalidas(imagens):
    return [
        imagem.name for imagem in imagens
        if not imagem.content_type.startswith('image/')
    ]


def tela_inicial(request):
    if request.session.get('admin_logado'):
        return redirect('painel_admin')

    cria_espaco()
    usuario = get_usuario_logado(request)
    if not usuario:
        return redirect('login')

    espacos = Espaco.objects.prefetch_related('imagens').all()
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
        acao = request.POST.get('acao', 'cadastrar')

        if acao == 'cancelar':
            Aluguel.objects.filter(id=request.POST.get('aluguel_id')).delete()
            messages.success(request, 'Reserva cancelada com sucesso.')
            return redirect('painel_admin')

        if acao == 'apagar_espaco':
            Configuracao.objects.get_or_create(chave=ESPACO_PADRAO_CHAVE)
            espaco = Espaco.objects.filter(id=request.POST.get('espaco_id')).first()

            if not espaco:
                messages.error(request, 'Espaco nao encontrado.')
            else:
                espaco.delete()
                messages.success(request, 'Espaco apagado com sucesso.')

            return redirect('painel_admin')

        if acao == 'editar_espaco':
            espaco = Espaco.objects.filter(id=request.POST.get('espaco_id')).first()
            nome = request.POST.get('nome', '').strip()
            endereco = request.POST.get('endereco', '').strip()
            descricao = request.POST.get('descricao', '').strip()
            imagens = request.FILES.getlist('imagens')

            if not espaco:
                messages.error(request, 'Espaco nao encontrado.')
                return redirect('painel_admin')

            if not nome or not endereco or not descricao:
                messages.error(request, 'Preencha nome, endereco e descricao do espaco.')
                return redirect('painel_admin')

            nomes_invalidos = imagens_invalidas(imagens)
            if nomes_invalidos:
                messages.error(request, 'Envie apenas arquivos de imagem.')
                return redirect('painel_admin')

            espaco.nome = nome
            espaco.endereco = endereco
            espaco.descricao = descricao
            espaco.save()

            if imagens:
                espaco.imagens.all().delete()
                for imagem in imagens:
                    EspacoImagem.objects.create(espaco=espaco, imagem=imagem)

            messages.success(request, 'Espaco atualizado com sucesso.')
            return redirect('painel_admin')

        nome = request.POST.get('nome', '').strip()
        endereco = request.POST.get('endereco', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        imagens = request.FILES.getlist('imagens')

        if not nome or not endereco or not descricao:
            messages.error(request, 'Preencha nome, endereco e descricao do espaco.')
            return redirect('painel_admin')

        if not imagens:
            messages.error(request, 'Envie pelo menos uma imagem do espaco.')
            return redirect('painel_admin')

        nomes_invalidos = imagens_invalidas(imagens)
        if nomes_invalidos:
            messages.error(request, 'Envie apenas arquivos de imagem.')
            return redirect('painel_admin')

        espaco = Espaco.objects.create(
            nome=nome,
            endereco=endereco,
            descricao=descricao,
        )
        for imagem in imagens:
            EspacoImagem.objects.create(espaco=espaco, imagem=imagem)

        messages.success(request, 'Espaco cadastrado com sucesso.')
        return redirect('painel_admin')

    cria_espaco()
    return render(request, 'admin.html', {
        'usuarios': Usuario.objects.all(),
        'alugueis': Aluguel.objects.select_related('usuario', 'espaco').all().order_by('-criado_em'),
        'espacos': Espaco.objects.prefetch_related('imagens').all()
    })


def login_view(request):
    if request.session.get('admin_logado'):
        return redirect('painel_admin')

    if get_usuario_logado(request):
        return redirect('tela_inicial')

    email = ''

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('password', '').strip()

        if not email or not senha:
            messages.error(request, "Preencha email e senha.")
        elif email == 'admin' and senha == 'admin123':
            request.session.flush()
            request.session['admin_logado'] = True
            return redirect('painel_admin')
        else:
            u = Usuario.objects.filter(email__iexact=email).first()

            if u and check_password(senha, u.senha):
                request.session.flush()
                request.session['usuario_id'] = u.id
                request.session['usuario_nome'] = u.nome
                return redirect('tela_inicial')

            messages.error(request, "Email ou senha invalidos.")

    return render(request, 'login.html', {'email': email})


def sair_view(request):
    request.session.flush()
    return redirect('login')


def descricao_view(request):
    cria_espaco()
    espaco_id = request.GET.get('espaco')
    espaco = Espaco.objects.prefetch_related('imagens').filter(id=espaco_id).first()
    if not espaco:
        espaco = Espaco.objects.prefetch_related('imagens').first()
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


def data_reserva_valida(dia):
    try:
        return date.fromisoformat(dia)
    except (TypeError, ValueError):
        return None


def horarios_ordenados(horarios):
    horarios_limpos = [hora.strip() for hora in horarios if hora.strip()]
    if len(horarios_limpos) != len(set(horarios_limpos)):
        return None

    if any(hora not in HORARIOS for hora in horarios_limpos):
        return None

    return sorted(horarios_limpos, key=HORARIOS.index)


def texto_duracao(horas):
    return f'{horas} hora' if horas == 1 else f'{horas} horas'


def disponibilidade_view(request):
    usuario = get_usuario_logado(request)
    if not usuario:
        messages.error(request, 'Faca login para reservar um espaco.')
        return redirect('login')

    if request.method == 'POST':
        espaco = Espaco.objects.filter(id=request.POST.get('espaco_id')).first()
        dia = request.POST.get('dia', '').strip()
        horarios = request.POST.get('horarios', '').strip()
        horarios_lista = [h for h in horarios.split(',') if h]
        data_reserva = data_reserva_valida(dia)
        horarios_lista = horarios_ordenados(horarios_lista)

        if not espaco:
            messages.error(request, 'Nao foi possivel encontrar o espaco.')
            return redirect('tela_inicial')

        if not dia or not horarios_lista:
            messages.error(request, 'Escolha o dia e pelo menos um horario.')
            return redirect(f'/disponibilidade/?espaco={espaco.id}')

        if not data_reserva:
            messages.error(request, 'Escolha uma data valida.')
            return redirect(f'/disponibilidade/?espaco={espaco.id}')

        if data_reserva < timezone.localdate():
            messages.error(request, 'Nao e possivel reservar em dias que ja passaram.')
            return redirect(f'/disponibilidade/?espaco={espaco.id}')

        ocupados = pega_horarios_ocupados(espaco, dia)
        conflito = [hora for hora in horarios_lista if hora in ocupados]

        if conflito:
            messages.error(request, 'Este horario ja esta reservado: ' + ', '.join(conflito))
            return redirect(f'/disponibilidade/?espaco={espaco.id}&dia={dia}')

        Aluguel.objects.create(
            dia=dia,
            duracao=texto_duracao(len(horarios_lista)),
            horarios=','.join(horarios_lista),
            usuario=usuario,
            espaco=espaco,
        )
        messages.success(request, 'Reserva criada com sucesso.')
        return redirect('tela_inicial')

    espaco_id = request.GET.get('espaco')
    dia = request.GET.get('dia', '')
    espaco = Espaco.objects.prefetch_related('imagens').filter(id=espaco_id).first()
    if not espaco:
        espaco = Espaco.objects.prefetch_related('imagens').first()
    if dia:
        data_reserva = data_reserva_valida(dia)
        if not data_reserva or data_reserva < timezone.localdate():
            messages.error(request, 'Escolha uma data de hoje em diante.')
            dia = ''
    ocupados = pega_horarios_ocupados(espaco, dia) if dia else []
    return render(request, 'disponibilidade.html', {
        'espaco': espaco,
        'horarios': HORARIOS,
        'ocupados': ocupados,
        'dia_selecionado': dia,
        'hoje': timezone.localdate().isoformat(),
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
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha', '').strip()
        confirmar = request.POST.get('confirmar_senha', '').strip()

        if not nome or not email or not senha or not confirmar:
            messages.error(request, "Preencha todos os campos.")
        elif senha != confirmar:
            messages.error(request, "As senhas nao coincidem!")
        elif not email_eh_valido(email):
            messages.error(request, "Email invalido.")
        elif Usuario.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email ja cadastrado.")
        elif Usuario.objects.filter(nome__iexact=nome).exists():
            messages.error(request, "Nome ja cadastrado. Use outro nome ou entre pelo email.")
        else:
            Usuario.objects.create(nome=nome, email=email, senha=make_password(senha))
            messages.success(request, "Cadastro realizado. Agora voce ja pode entrar.")
            return redirect('login')

    return render(request, 'cadastro.html')
