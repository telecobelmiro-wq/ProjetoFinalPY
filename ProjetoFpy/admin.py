from django.contrib import admin
from .models import Aluguel, Espaco, Usuario


admin.site.register(Usuario)
admin.site.register(Aluguel)
admin.site.register(Espaco)
