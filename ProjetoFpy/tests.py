from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Aluguel, Configuracao, Espaco, Usuario


class LoginTests(TestCase):
    def test_rota_inicial_abre_login(self):
        response = self.client.get(reverse('entrada'))

        self.assertRedirects(response, reverse('login'))

    def test_home_exige_login(self):
        response = self.client.get(reverse('tela_inicial'))

        self.assertRedirects(response, reverse('login'))

    def test_login_usuario_redireciona_para_home(self):
        Usuario.objects.create(
            nome='Maria',
            cpf='52998224725',
            senha=make_password('senha123'),
        )

        response = self.client.post(reverse('login'), {
            'username': 'Maria',
            'password': 'senha123',
        })

        self.assertRedirects(response, reverse('tela_inicial'))
        session = self.client.session
        self.assertEqual(session.get('usuario_nome'), 'Maria')
        self.assertIsNotNone(session.get('usuario_id'))

    def test_login_por_cpf_tambem_funciona(self):
        Usuario.objects.create(
            nome='Joao',
            cpf='52998224725',
            senha=make_password('senha123'),
        )

        response = self.client.post(reverse('login'), {
            'username': '529.982.247-25',
            'password': 'senha123',
        })

        self.assertRedirects(response, reverse('tela_inicial'))

    def test_login_admin_redireciona_para_painel(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'admin123',
        })

        self.assertRedirects(response, reverse('painel_admin'))
        self.assertTrue(self.client.session.get('admin_logado'))


class DisponibilidadeTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome='Maria',
            cpf='52998224725',
            senha=make_password('senha123'),
        )
        self.espaco = Espaco.objects.create(
            nome='Salao',
            endereco='Rua A',
            descricao='Espaco para eventos',
        )

        session = self.client.session
        session['usuario_id'] = self.usuario.id
        session['usuario_nome'] = self.usuario.nome
        session.save()

    def test_calendario_nao_permite_datas_passadas_na_tela(self):
        response = self.client.get(reverse('disponibilidade'), {'espaco': self.espaco.id})

        hoje = timezone.localdate().isoformat()
        self.assertContains(response, f'min="{hoje}"')

    def test_reserva_rejeita_dia_passado(self):
        ontem = (timezone.localdate() - timedelta(days=1)).isoformat()

        self.client.post(reverse('disponibilidade'), {
            'espaco_id': self.espaco.id,
            'dia': ontem,
            'duracao': '1',
            'horarios': '1:00',
        })

        self.assertEqual(Aluguel.objects.count(), 0)

    def test_reserva_exige_quantidade_de_horarios_da_duracao(self):
        amanha = (timezone.localdate() + timedelta(days=1)).isoformat()

        self.client.post(reverse('disponibilidade'), {
            'espaco_id': self.espaco.id,
            'dia': amanha,
            'duracao': '2 horas',
            'horarios': '1:00',
        })

        self.assertEqual(Aluguel.objects.count(), 0)

    def test_reserva_exige_horarios_seguidos(self):
        amanha = (timezone.localdate() + timedelta(days=1)).isoformat()

        self.client.post(reverse('disponibilidade'), {
            'espaco_id': self.espaco.id,
            'dia': amanha,
            'duracao': '2',
            'horarios': '1:00,3:00',
        })

        self.assertEqual(Aluguel.objects.count(), 0)

    def test_reserva_aceita_horarios_seguidos_e_organiza_ordem(self):
        amanha = (timezone.localdate() + timedelta(days=1)).isoformat()

        self.client.post(reverse('disponibilidade'), {
            'espaco_id': self.espaco.id,
            'dia': amanha,
            'duracao': '3 horas',
            'horarios': '3:00,1:00,2:00',
        })

        aluguel = Aluguel.objects.get()
        self.assertEqual(aluguel.duracao, '3 horas')
        self.assertEqual(aluguel.horarios, '1:00,2:00,3:00')


class PainelAdminTests(TestCase):
    def setUp(self):
        session = self.client.session
        session['admin_logado'] = True
        session.save()

    def test_admin_edita_espaco(self):
        espaco = Espaco.objects.create(
            nome='Antigo',
            endereco='Rua Antiga',
            descricao='Descricao antiga',
        )

        self.client.post(reverse('painel_admin'), {
            'acao': 'editar_espaco',
            'espaco_id': espaco.id,
            'nome': 'Novo',
            'endereco': 'Rua Nova',
            'descricao': 'Descricao nova',
        })

        espaco.refresh_from_db()
        self.assertEqual(espaco.nome, 'Novo')
        self.assertEqual(espaco.endereco, 'Rua Nova')
        self.assertEqual(espaco.descricao, 'Descricao nova')

    def test_admin_apaga_espaco_sem_recriar_padrao(self):
        espaco = Espaco.objects.create(
            nome='Dubai Eventos',
            endereco='Rua A',
            descricao='Descricao',
        )

        self.client.post(reverse('painel_admin'), {
            'acao': 'apagar_espaco',
            'espaco_id': espaco.id,
        })
        self.client.get(reverse('painel_admin'))

        self.assertEqual(Espaco.objects.count(), 0)
        self.assertTrue(Configuracao.objects.filter(chave='espaco_padrao_criado').exists())
