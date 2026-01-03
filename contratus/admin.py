from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Cliente, Construtora, Equipe, Empreendimento, UnidadeEmpreendimento, Proposta, Contrato

# Formulário de criação do usuário
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'nivel')

# Formulário de alteração do usuário
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'nivel')

# UserAdmin customizado
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'nivel', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('nivel',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('nivel',)}),
    )

# Registra o User customizado com o admin correto
admin.site.register(User, UserAdmin)

# Registra os outros modelos normalmente
admin.site.register(Cliente)
admin.site.register(Construtora)
admin.site.register(Equipe)
admin.site.register(Empreendimento)
admin.site.register(UnidadeEmpreendimento)
admin.site.register(Proposta)
admin.site.register(Contrato)
