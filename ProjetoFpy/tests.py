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
            email='maria@example.com',
            senha=make_password('senha123'),
        )

        response = self.client.post(reverse('login'), {
            'email': 'maria@example.com',
            'password': 'senha123',
        })

        self.assertRedirects(response, reverse('tela_inicial'))
        session = self.client.session
        self.assertEqual(session.get('usuario_nome'), 'Maria')
        self.assertIsNotNone(session.get('usuario_id'))

    def test_login_por_cpf_nao_funciona_mais(self):
        Usuario.objects.create(
            nome='Joao',
            email='joao@example.com',
            senha=make_password('senha123'),
        )

        response = self.client.post(reverse('login'), {
            'email': '529.982.247-25',
            'password': 'senha123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.client.session.get('usuario_id'))

    def test_login_admin_redireciona_para_painel(self):
        response = self.client.post(reverse('login'), {
            'email': 'admin',
            'password': 'admin123',
        })

        self.assertRedirects(response, reverse('painel_admin'))
        self.assertTrue(self.client.session.get('admin_logado'))


class DisponibilidadeTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome='Maria',
            email='maria@example.com',
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
            'horarios': '1:00',
        })

        self.assertEqual(Aluguel.objects.count(), 0)

    def test_reserva_exige_pelo_menos_um_horario(self):
        amanha = (timezone.localdate() + timedelta(days=1)).isoformat()

        self.client.post(reverse('disponibilidade'), {
            'espaco_id': self.espaco.id,
            'dia': amanha,
            'horarios': '',
        })

        self.assertEqual(Aluguel.objects.count(), 0)

    def test_reserva_aceita_horarios_nao_seguidos(self):
        amanha = (timezone.localdate() + timedelta(days=1)).isoformat()

        self.client.post(reverse('disponibilidade'), {
            'espaco_id': self.espaco.id,
            'dia': amanha,
            'horarios': '1:00,3:00',
        })

        aluguel = Aluguel.objects.get()
        self.assertEqual(aluguel.duracao, '2 horas')
        self.assertEqual(aluguel.horarios, '1:00,3:00')

    def test_reserva_calcula_duracao_e_organiza_ordem(self):
        amanha = (timezone.localdate() + timedelta(days=1)).isoformat()

        self.client.post(reverse('disponibilidade'), {
            'espaco_id': self.espaco.id,
            'dia': amanha,
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
