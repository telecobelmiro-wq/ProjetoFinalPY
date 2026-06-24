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
    imagem1 = models.CharField(max_length=100, blank=True, default='')
    imagem2 = models.CharField(max_length=100, blank=True, default='')
    imagem3 = models.CharField(max_length=100, blank=True, default='')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    @property
    def imagens_padrao(self):
        return [imagem for imagem in [self.imagem1, self.imagem2, self.imagem3] if imagem]

    @property
    def imagem_capa_padrao(self):
        imagens = self.imagens_padrao
        return imagens[0] if imagens else ''


class EspacoImagem(models.Model):
    espaco = models.ForeignKey(Espaco, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.FileField(upload_to='espacos/')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em', 'id']

    def __str__(self):
        return f'Imagem de {self.espaco.nome}'

class Aluguel(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    espaco = models.ForeignKey('Espaco', on_delete=models.SET_NULL, null=True, blank=True)
    dia = models.CharField(max_length=20)
    duracao = models.CharField(max_length=20)
    horarios = models.CharField(max_length=200)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Aluguel em {self.dia}"
