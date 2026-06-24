from django.contrib import admin
from .models import Aluguel, Espaco, EspacoImagem, Usuario


admin.site.register(Usuario)
admin.site.register(Aluguel)
admin.site.register(Espaco)
admin.site.register(EspacoImagem)
