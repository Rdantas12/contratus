from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Cliente, Construtora, Equipe, Empreendimento, UnidadeEmpreendimento, Proposta, Contrato

# 🔹 Formulário de criação do usuário customizado
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'cpf', 'telefone', 'creci', 'nivel', 'equipe', 'foto')

# 🔹 Formulário de alteração do usuário customizado
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'cpf', 'telefone', 'creci', 'nivel', 'equipe', 'foto', 'is_active', 'is_staff', 'groups', 'user_permissions')

# 🔹 UserAdmin customizado
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = User

    list_display = ('username', 'email', 'first_name', 'last_name', 'nivel', 'equipe', 'is_staff', 'is_active')
    list_filter = ('nivel', 'is_staff', 'is_active', 'equipe')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'cpf')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email', 'cpf', 'telefone', 'creci', 'equipe', 'nivel', 'foto')}),
        ('Permissões', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'cpf', 'telefone', 'creci', 'nivel', 'equipe', 'foto', 'password1', 'password2', 'is_staff', 'is_active', 'groups')}
        ),
    )

# 🔹 Registrar o User customizado
admin.site.register(User, UserAdmin)

# 🔹 Registrar os outros modelos normalmente
admin.site.register(Cliente)
admin.site.register(Construtora)
admin.site.register(Equipe)
admin.site.register(Empreendimento)
admin.site.register(UnidadeEmpreendimento)
admin.site.register(Proposta)
admin.site.register(Contrato)
