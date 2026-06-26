from django.contrib import admin
from .models import Aluguel, Configuracao, Espaco, EspacoImagem, Usuario


admin.site.register(Usuario)
admin.site.register(Aluguel)
admin.site.register(Configuracao)
admin.site.register(Espaco)
admin.site.register(EspacoImagem)
