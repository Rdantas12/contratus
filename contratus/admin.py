
from django.contrib import admin
from .models import User, Cliente, Construtora, Equipe, Empreendimento, UnidadeEmpreendimento, Proposta, Contrato

# Registra os modelos
admin.site.register(User)
admin.site.register(Cliente)
admin.site.register(Construtora)
admin.site.register(Equipe)
admin.site.register(Empreendimento)
admin.site.register(UnidadeEmpreendimento)
admin.site.register(Proposta)
admin.site.register(Contrato)