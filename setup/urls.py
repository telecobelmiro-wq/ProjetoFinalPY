from django.contrib import admin
from django.urls import path
from ProjetoFpy import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.tela_inicial, name='tela_inicial'),
    path('painel-admin/', views.painel_admin, name='painel_admin'),
    path('login/', views.login_view, name='login'),
    path('sair/', views.sair_view, name='sair'),
    path('descricao/', views.descricao_view, name='descricao'),
    path('disponibilidade/', views.disponibilidade_view, name='disponibilidade'),
    path('cancelar/<int:aluguel_id>/', views.cancelar_aluguel_view, name='cancelar_aluguel'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
]
