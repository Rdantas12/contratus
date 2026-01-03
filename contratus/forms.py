# forms.py - VERSÃO ATUALIZADA
# ✅ FORMULÁRIO DE CONTRATO SIMPLIFICADO - APENAS DADOS COMPLEMENTARES

from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    User, Equipe, Construtora, Empreendimento, UnidadeEmpreendimento,
    Cliente, Proposta, Contrato
)


class LoginForm(forms.Form):
    """Formulário de login"""
    username = forms.CharField(
        label='Usuário',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu usuário'
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })
    )


class UserForm(UserCreationForm):
    """Formulário de usuário"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'cpf', 'creci', 
                  'telefone', 'nivel', 'equipe', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'creci': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'nivel': forms.Select(attrs={'class': 'form-control'}),
            'equipe': forms.Select(attrs={'class': 'form-control'}),
        }


class EquipeForm(forms.ModelForm):
    """Formulário de equipe"""
    class Meta:
        model = Equipe
        fields = ['nome', 'gerente', 'descricao', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'gerente': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ConstrutoraForm(forms.ModelForm):
    """Formulário de construtora"""
    class Meta:
        model = Construtora
        fields = [
            'razao_social', 'nome_fantasia', 'cnpj',
            'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep',
            'telefone', 'email', 'responsavel_legal', 'ativa', 'observacoes'
        ]
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2', 'placeholder': 'RJ'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'responsavel_legal': forms.TextInput(attrs={'class': 'form-control'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class EmpreendimentoForm(forms.ModelForm):
    """Formulário de empreendimento"""
    class Meta:
        model = Empreendimento
        fields = [
            'nome', 'construtora', 'tipo_imovel',
            'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep',
            'descricao_completa', 'quartos', 'banheiros', 'vagas_garagem', 'area_util',
            'total_unidades', 'unidades_disponiveis',
            'valor_imovel', 'valor_engenharia_necessaria', 'taxa_corretagem_percentual',
            'status', 'data_lancamento', 'data_entrega_prevista',
            'imagem_principal', 'ativo', 'observacoes'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'construtora': forms.Select(attrs={'class': 'form-control'}),
            'tipo_imovel': forms.Select(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao_completa': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quartos': forms.NumberInput(attrs={'class': 'form-control'}),
            'banheiros': forms.NumberInput(attrs={'class': 'form-control'}),
            'vagas_garagem': forms.NumberInput(attrs={'class': 'form-control'}),
            'area_util': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_unidades': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidades_disponiveis': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_imovel': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_engenharia_necessaria': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'taxa_corretagem_percentual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'data_lancamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_entrega_prevista': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'imagem_principal': forms.FileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UnidadeForm(forms.ModelForm):
    """Formulário de unidade"""
    class Meta:
        model = UnidadeEmpreendimento
        fields = ['empreendimento', 'identificacao', 'andar', 'bloco', 'status', 'observacoes']
        widgets = {
            'empreendimento': forms.Select(attrs={'class': 'form-control'}),
            'identificacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Casa 03, Apto 205'}),
            'andar': forms.TextInput(attrs={'class': 'form-control'}),
            'bloco': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ClienteForm(forms.ModelForm):
    """Formulário de cliente"""
    class Meta:
        model = Cliente
        fields = [
            'nome_completo', 'cpf', 'rg', 'data_nascimento', 'estado_civil',
            'telefone', 'email',
            'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep',
            'origem', 'observacoes'
        ]
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'origem': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PropostaForm(forms.ModelForm):
    """Formulário de proposta"""
    
    # Campo auxiliar: Valor da Parcela (usuário informa)
    valor_parcela_input = forms.DecimalField(
        label='Valor da Parcela (R$)',
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'id': 'id_valor_parcela_input',
            'placeholder': 'Ex: 1500.00'
        }),
        help_text='Informe o valor de cada parcela'
    )
    
    class Meta:
        model = Proposta
        fields = [
            'empreendimento', 'unidade', 'cliente',
            'valor_engenharia_necessaria', 'valor_imovel', 'valor_financiamento',
            'valor_subsidio', 'valor_fgts', 'valor_sinal', 'valor_entrada',
            'valor_parcelamento_sem_juros',
            'observacoes'
        ]
        widgets = {
            'empreendimento': forms.Select(attrs={'class': 'form-control', 'id': 'id_empreendimento'}),
            'unidade': forms.Select(attrs={'class': 'form-control', 'id': 'id_unidade'}),
            'cliente': forms.Select(attrs={'class': 'form-control', 'id': 'id_cliente'}),
            'valor_engenharia_necessaria': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Deixe em branco se não saiu a engenharia'
            }),
            'valor_imovel': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_financiamento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_subsidio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_fgts': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_sinal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_entrada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_parcelamento_sem_juros': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'id': 'id_valor_parcelamento',
                'readonly': 'readonly'
            }),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar clientes baseado no usuário
        if user:
            if user.nivel == 'corretor':
                self.fields['cliente'].queryset = Cliente.objects.filter(cadastrado_por=user)
            elif user.nivel == 'gerente' and user.equipe:
                corretores_equipe = user.equipe.membros.filter(nivel='corretor')
                self.fields['cliente'].queryset = Cliente.objects.filter(cadastrado_por__in=corretores_equipe)
        
        # Tornar valor_engenharia_necessaria opcional
        self.fields['valor_engenharia_necessaria'].required = False
        
        # Se está editando, preencher o campo valor_parcela_input
        if self.instance and self.instance.pk:
            self.fields['valor_parcela_input'].initial = self.instance.valor_parcela
    
    def clean(self):
        cleaned_data = super().clean()
        valor_parcelamento = cleaned_data.get('valor_parcelamento_sem_juros')
        valor_parcela_input = cleaned_data.get('valor_parcela_input')
        
        if valor_parcelamento and valor_parcela_input:
            if valor_parcela_input > valor_parcelamento:
                raise forms.ValidationError(
                    'O valor da parcela não pode ser maior que o valor total do parcelamento.'
                )
            
            # Calcular número de parcelas
            numero_parcelas = int(valor_parcelamento / valor_parcela_input)
            
            if numero_parcelas < 1:
                raise forms.ValidationError('O número de parcelas deve ser no mínimo 1.')
            
            # Armazenar nos dados limpos
            cleaned_data['numero_parcelas'] = numero_parcelas
            cleaned_data['valor_parcela'] = valor_parcela_input
        
        # Se valor_engenharia_necessaria estiver vazio, definir como 0
        if not cleaned_data.get('valor_engenharia_necessaria'):
            cleaned_data['valor_engenharia_necessaria'] = Decimal('0.00')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Atribuir valores calculados
        instance.numero_parcelas = self.cleaned_data['numero_parcelas']
        instance.valor_parcela = self.cleaned_data['valor_parcela']
        
        if commit:
            instance.save()
        return instance


# ✅ NOVO FORMULÁRIO DE CONTRATO SIMPLIFICADO
class ContratoForm(forms.ModelForm):
    """Formulário de contrato - APENAS DADOS COMPLEMENTARES
    
    Os dados principais (cliente, valores, etc.) são copiados automaticamente da proposta.
    O corretor preenche apenas:
    - Data de assinatura
    - Testemunhas (opcional)
    - Observações (opcional)
    """
    
    class Meta:
        model = Contrato
        fields = [
            'data_assinatura',
            'testemunha1_nome',
            'testemunha1_cpf',
            'testemunha2_nome',
            'testemunha2_cpf',
            'observacoes'
        ]
        widgets = {
            'data_assinatura': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'testemunha1_nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo da primeira testemunha (opcional)'
            }),
            'testemunha1_cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'testemunha2_nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo da segunda testemunha (opcional)'
            }),
            'testemunha2_cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais sobre o contrato (opcional)'
            }),
        }
        labels = {
            'data_assinatura': 'Data de Assinatura do Contrato *',
            'testemunha1_nome': 'Nome da Testemunha 1',
            'testemunha1_cpf': 'CPF da Testemunha 1',
            'testemunha2_nome': 'Nome da Testemunha 2',
            'testemunha2_cpf': 'CPF da Testemunha 2',
            'observacoes': 'Observações',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Data de assinatura é obrigatória
        self.fields['data_assinatura'].required = True
        
        # Testemunhas são opcionais
        self.fields['testemunha1_nome'].required = False
        self.fields['testemunha1_cpf'].required = False
        self.fields['testemunha2_nome'].required = False
        self.fields['testemunha2_cpf'].required = False
        self.fields['observacoes'].required = False
