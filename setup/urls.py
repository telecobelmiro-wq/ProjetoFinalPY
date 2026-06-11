from django.contrib import admin
from django.urls import path
from ProjetoFpy import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rota da Página Inicial (Ex: http://127.0.0.1:8000/)
    path('', views.tela_inicial, name='tela_inicial'),
    
    # Rota da Página de Login (Ex: http://127.0.0.1:8000/login/)
    path('login/', views.login_view, name='login'),
    
    # Rota da Página de Cadastro (Ex: http://127.0.0.1:8000/cadastro/)
    path('cadastro/', views.cadastro_view, name='cadastro'),
]