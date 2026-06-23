from django.db import models

class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11, unique=True)
    senha = models.CharField(max_length=128)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Espaco(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255)
    descricao = models.TextField()
    imagem1 = models.CharField(max_length=100)
    imagem2 = models.CharField(max_length=100)
    imagem3 = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Aluguel(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    espaco = models.ForeignKey('Espaco', on_delete=models.SET_NULL, null=True, blank=True)
    dia = models.CharField(max_length=20)
    duracao = models.CharField(max_length=20)
    horarios = models.CharField(max_length=200)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Aluguel em {self.dia}"