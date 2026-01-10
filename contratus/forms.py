# forms.py - VERSÃO ATUALIZADA
# ✅ Formulário com campos para cálculo automático de parcelas

from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    User, Equipe, Construtora, Empreendimento, UnidadeEmpreendimento,
    Cliente, Proposta, Contrato, TipoUnidade
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
        fields = ['username', 'first_name', 'last_name', 'email', 'cpf', 
                  'creci', 'telefone', 'nivel', 'equipe']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'creci': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
            'equipe': forms.Select(attrs={'class': 'form-select'}),
        }


class EquipeForm(forms.ModelForm):
    """Formulário de equipe"""
    class Meta:
        model = Equipe
        fields = ['nome', 'lider', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'lider': forms.Select(attrs={'class': 'form-select'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ConstrutoraForm(forms.ModelForm):
    """Formulário de construtora - VERSÃO CORRIGIDA"""
    class Meta:
        model = Construtora
        fields = [
            'razao_social', 'nome_fantasia', 'cnpj', 'responsavel_legal',
            'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep',
            'telefone', 'email', 'ativa', 'observacoes'
        ]
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razão Social Completa'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Fantasia'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'responsavel_legal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Responsável Legal'}),
            
            # Endereço
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Rua'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apto, Sala, etc.'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'estado': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Selecione o Estado'),
                ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
                ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
                ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
                ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
                ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
                ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
                ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
            ]),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            
            # Contato
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contato@construtora.com'}),
            
            # Outros
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Informações adicionais sobre a construtora...'}),
        }




# forms.py

class TipoUnidadeForm(forms.ModelForm):
    """Formulário de tipo de unidade"""

    class Meta:
        model = TipoUnidade
        fields = [
            'empreendimento',
            'nome', 'descricao',
            'quartos', 'banheiros', 'vagas_garagem', 'area_util',
            'valor_imovel', 'valor_engenharia_necessaria',
            'imagem',
            'ativo',
        ]
        widgets = {
            'empreendimento': forms.HiddenInput(),

            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

            'quartos': forms.NumberInput(attrs={'class': 'form-control'}),
            'banheiros': forms.NumberInput(attrs={'class': 'form-control'}),
            'vagas_garagem': forms.NumberInput(attrs={'class': 'form-control'}),
            'area_util': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),

            'valor_imovel': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_engenharia_necessaria': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),

            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        empreendimento_id = kwargs.pop('empreendimento_id', None)
        super().__init__(*args, **kwargs)

        if empreendimento_id:
            self.fields['empreendimento'].queryset = Empreendimento.objects.filter(pk=empreendimento_id)
            self.fields['empreendimento'].initial = empreendimento_id

class EmpreendimentoForm(forms.ModelForm):
    """Formulário de empreendimento - VERSÃO CORRIGIDA"""
    class Meta:
        model = Empreendimento
        fields = [
            'nome', 'tipo_imovel', 'construtora', 'status',
            'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep',
            'descricao_completa',
            'total_unidades', 'unidades_disponiveis', 'taxa_corretagem_percentual',
            'data_lancamento', 'data_entrega_prevista',
            'imagem_principal', 'ativo', 'observacoes','cnpj'
        ]
        widgets = {
            # Dados Básicos
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Empreendimento'}),
            'tipo_imovel': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Selecione'),
                ('apartamento', 'Apartamento'),
                ('casa', 'Casa'),
                ('terreno', 'Terreno'),
                ('comercial', 'Comercial'),
                ('rural', 'Rural')
            ]),
            'construtora': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Selecione'),
                ('planejamento', 'Em Planejamento'),
                ('lancamento', 'Lançamento'),
                ('obras', 'Em Obras'),
                ('pronto', 'Pronto'),
                ('entregue', 'Entregue')
            ]),
            
            # Localização
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Rua'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quadra, Lote, etc.'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'estado': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Selecione'),
                ('AC', 'AC'), ('AL', 'AL'), ('AP', 'AP'), ('AM', 'AM'),
                ('BA', 'BA'), ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'),
                ('GO', 'GO'), ('MA', 'MA'), ('MT', 'MT'), ('MS', 'MS'),
                ('MG', 'MG'), ('PA', 'PA'), ('PB', 'PB'), ('PR', 'PR'),
                ('PE', 'PE'), ('PI', 'PI'), ('RJ', 'RJ'), ('RN', 'RN'),
                ('RS', 'RS'), ('RO', 'RO'), ('RR', 'RR'), ('SC', 'SC'),
                ('SP', 'SP'), ('SE', 'SE'), ('TO', 'TO')
            ]),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            # Descrição
            'descricao_completa': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5,
                'placeholder': 'Descreva o empreendimento: diferenciais, infraestrutura, localização, etc.'
            }),
            
            # Unidades e Valores
            'total_unidades': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 100'}),
            'unidades_disponiveis': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 85'}),
            'taxa_corretagem_percentual': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': 'Ex: 4.00'
            }),
            
            # Datas
            'data_lancamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_entrega_prevista': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            
            # Imagem
            'imagem_principal': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            
            # Outros
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações internas...'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas construtoras ativas
        self.fields['construtora'].queryset = Construtora.objects.filter(ativa=True)


class UnidadeForm(forms.ModelForm):
    """✅ CORRIGIDO: Formulário de unidade com campos corretos do modelo"""
    class Meta:
        model = UnidadeEmpreendimento
        fields = [
            'empreendimento',
            'tipo',
            'numero',
            'bloco',
            'andar',
            'area_privativa',
            'quartos',
            'suites',
            'banheiros',
            'vagas_garagem',
            'valor_imovel',
            'valor_engenharia',
            'status',
            'observacoes'
        ]
        widgets = {
            'empreendimento': forms.HiddenInput(),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 101'}),
            'bloco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Bloco A'}),
            'andar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1º andar'}),
            'area_privativa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quartos': forms.NumberInput(attrs={'class': 'form-control'}),
            'suites': forms.NumberInput(attrs={'class': 'form-control'}),
            'banheiros': forms.NumberInput(attrs={'class': 'form-control'}),
            'vagas_garagem': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_imovel': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_engenharia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        empreendimento_id = kwargs.pop('empreendimento_id', None)
        super().__init__(*args, **kwargs)

        if empreendimento_id:
            # Definir empreendimento
            self.fields['empreendimento'].initial = empreendimento_id
            self.fields['empreendimento'].queryset = Empreendimento.objects.filter(pk=empreendimento_id)
            
            # Filtrar tipos de unidade deste empreendimento
            self.fields['tipo'].queryset = TipoUnidade.objects.filter(
                empreendimento_id=empreendimento_id,
                ativo=True
            )

class UnidadesEmLoteForm(forms.Form):
    """Formulário para cadastro de unidades em lote"""
    empreendimento = forms.ModelChoiceField(
        queryset=Empreendimento.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Empreendimento'
    )
    tipo = forms.ModelChoiceField(
        queryset=TipoUnidade.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Unidade'
    )
    bloco = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Bloco/Torre'
    )
    prefixo = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: APT'}),
        label='Prefixo (opcional)'
    )
    numero_inicial = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Número Inicial'
    )
    numero_final = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Número Final'
    )
    area_privativa = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label='Área Privativa (m²)'
    )
    quartos = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Quartos'
    )
    suites = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Suítes'
    )
    banheiros = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Banheiros'
    )
    vagas_garagem = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Vagas de Garagem'
    )
    valor_imovel = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label='Valor do Imóvel'
    )
    valor_engenharia = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label='Valor de Engenharia'
    )

    
    andar = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Andar'
    )

    def __init__(self, *args, **kwargs):
        empreendimento_id = kwargs.pop('empreendimento_id', None)
        super().__init__(*args, **kwargs)

        if empreendimento_id:
            self.fields['empreendimento'].initial = empreendimento_id
            self.fields['tipo'].queryset = TipoUnidade.objects.filter(
                empreendimento_id=empreendimento_id,
                ativo=True
            )
class ClienteForm(forms.ModelForm):
    """Formulário de cliente - VERSÃO CORRIGIDA"""
    class Meta:
        model = Cliente
        fields = [
            'nome_completo', 'cpf', 'rg', 'data_nascimento', 'estado_civil', 'origem',
            'telefone', 'email',
            'rua', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep',
            'observacoes'
        ]
        widgets = {
            # Dados Pessoais
            'nome_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo do cliente'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00', 'id': 'id_cpf'}),
            'rg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000-0'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Selecione'),
                ('solteiro', 'Solteiro(a)'),
                ('casado', 'Casado(a)'),
                ('divorciado', 'Divorciado(a)'),
                ('viuvo', 'Viúvo(a)'),
                ('uniao_estavel', 'União Estável')
            ]),
            'origem': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Selecione'),
                ('site', 'Site'),
                ('indicacao', 'Indicação'),
                ('midia_social', 'Mídia Social'),
                ('evento', 'Evento'),
                ('plantao', 'Plantão'),
                ('outro', 'Outro')
            ]),
            
            # Contatos
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000', 'id': 'id_telefone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            
            # Endereço
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Rua'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apto, Bloco, etc.'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'estado': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Selecione o Estado'),
                ('AC', 'AC'), ('AL', 'AL'), ('AP', 'AP'), ('AM', 'AM'),
                ('BA', 'BA'), ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'),
                ('GO', 'GO'), ('MA', 'MA'), ('MT', 'MT'), ('MS', 'MS'),
                ('MG', 'MG'), ('PA', 'PA'), ('PB', 'PB'), ('PR', 'PR'),
                ('PE', 'PE'), ('PI', 'PI'), ('RJ', 'RJ'), ('RN', 'RN'),
                ('RS', 'RS'), ('RO', 'RO'), ('RR', 'RR'), ('SC', 'SC'),
                ('SP', 'SP'), ('SE', 'SE'), ('TO', 'TO')
            ]),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000', 'id': 'id_cep'}),
            
            # Observações
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Observações sobre o cliente...'}),
        }


class PropostaForm(forms.ModelForm):
    """
    ✅ Formulário de Proposta com Cálculo Automático
    
    O corretor preenche:
    - valor_construtora (sem juros)
    - valor_parcela_cliente (quanto o cliente pode pagar por mês)
    
    Sistema calcula automaticamente:
    - valor_com_juros = valor_construtora × 1,5 (50% de juros)
    - quantidade_parcelas = valor_com_juros ÷ valor_parcela_cliente
    
    Todos os campos são editáveis para ajustes manuais
    """
    
    class Meta:
        model = Proposta
        fields = [
            'empreendimento',
            'unidade',
            'cliente',
            'valor_construtora',
            'valor_parcela_cliente',
            'valor_com_juros',
            'quantidade_parcelas',
            'valor_financiamento',
            'valor_subsidio',
            'valor_fgts',
            'valor_entrada',
            'observacoes'
        ]
        widgets = {
            'empreendimento': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_empreendimento'
            }),
            'unidade': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_unidade'
            }),
            'cliente': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_cliente'
            }),
            'valor_construtora': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'id': 'id_valor_construtora',
                'placeholder': 'Ex: 150000.00'
            }),
            'valor_parcela_cliente': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'id': 'id_valor_parcela_cliente',
                'placeholder': 'Ex: 1500.00'
            }),
            'valor_com_juros': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'id': 'id_valor_com_juros',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0;'
            }),
            'quantidade_parcelas': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_quantidade_parcelas',
                'readonly': 'readonly',
                'style': 'background-color: #f0f0f0;'
            }),
            'valor_financiamento': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'valor_subsidio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'valor_fgts': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'valor_entrada': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas unidades disponíveis
        self.fields['unidade'].queryset = UnidadeEmpreendimento.objects.filter(
            status='disponivel'
        )
        
        # Labels personalizados
        self.fields['valor_construtora'].label = 'Valor para Construtora (sem juros)'
        self.fields['valor_parcela_cliente'].label = 'Valor Mensal que Cliente Pode Pagar *'
        self.fields['valor_com_juros'].label = 'Valor COM Juros (50%) - Calculado'
        self.fields['quantidade_parcelas'].label = 'Número de Parcelas - Calculado'
        
        # Help texts
        self.fields['valor_construtora'].help_text = 'Valor base que será pago à construtora'
        self.fields['valor_parcela_cliente'].help_text = 'Quanto o cliente consegue pagar mensalmente?'
        self.fields['valor_com_juros'].help_text = 'Automático: Valor sem juros × 1,5'
        self.fields['quantidade_parcelas'].help_text = 'Automático: Valor com juros ÷ Valor da parcela'


class ContratoForm(forms.ModelForm):
    """
    ✅ Formulário de contrato SIMPLIFICADO
    Apenas dados complementares (dados da proposta já estão preenchidos)
    """
    class Meta:
        model = Contrato
        fields = [
            'registro_imovel',
            'matricula',
            'cartorio',
            'data_assinatura',
            'data_vencimento_primeira_parcela',
        ]
        widgets = {
            'registro_imovel': forms.TextInput(attrs={'class': 'form-control'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'cartorio': forms.TextInput(attrs={'class': 'form-control'}),
            'data_assinatura': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_vencimento_primeira_parcela': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
