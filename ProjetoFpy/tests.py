from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse

from .models import Usuario


class LoginTests(TestCase):
    def test_rota_inicial_abre_home(self):
        response = self.client.get(reverse('tela_inicial'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

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
