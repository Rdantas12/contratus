# models.py - VERSÃO ATUALIZADA
# ✅ Proposta com cálculo automático de parcelas baseado no valor que o cliente pode pagar
# ✅ Status da unidade muda para "reservada" quando proposta é criada
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from datetime import timedelta
from num2words import num2words

class User(AbstractUser):
    NIVEL_CHOICES = (
        ('administrador', 'Administrador'),
        ('gerente', 'Gerente'),
        ('corretor', 'Corretor'),
    )

    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        default='corretor',
        verbose_name='Nível de Acesso'
    )

    cpf = models.CharField(
        max_length=14,
        unique=True,
    )

    creci = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='CRECI'
    )

    telefone = models.CharField(
        max_length=20,
        verbose_name='Telefone'
    )

    equipe = models.ForeignKey(
        'Equipe',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='membros'
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='contratus_user_set',
        related_query_name='contratus_user',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='contratus_user_set',
        related_query_name='contratus_user',
    )

    foto = models.ImageField(
        upload_to='usuarios/',
        blank=True,
        null=True,
        verbose_name='Foto'
    )
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_nivel_display()})"


class Equipe(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    lider = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipes_lideradas'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Equipe'
        verbose_name_plural = 'Equipes'

    def __str__(self):
        return self.nome

class Construtora(models.Model):
    razao_social = models.CharField(max_length=200, verbose_name="Razão Social")
    nome_fantasia = models.CharField(max_length=200, verbose_name="Nome Fantasia")
    cnpj = models.CharField(max_length=18, unique=True)

    responsavel_legal = models.CharField(max_length=200)

    # Endereço
    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)

    # Contato
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    ativa = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Construtora"
        verbose_name_plural = "Construtoras"
        ordering = ["nome_fantasia"]

    def __str__(self):
        return self.nome_fantasia





class Empreendimento(models.Model):
    TIPO_IMOVEL_CHOICES = [
        ('apartamento', 'Apartamento'),
        ('casa', 'Casa'),
        ('terreno', 'Terreno'),
        ('comercial', 'Comercial'),
        ('rural', 'Rural'),
    ]

    STATUS_CHOICES = [
        ('planejamento', 'Em Planejamento'),
        ('lancamento', 'Lançamento'),
        ('obras', 'Em Obras'),
        ('pronto', 'Pronto'),
        ('entregue', 'Entregue'),
    ]

    construtora = models.ForeignKey(Construtora, on_delete=models.CASCADE, related_name='empreendimentos')

    # Dados básicos
    nome = models.CharField(max_length=200)
    tipo_imovel = models.CharField(max_length=20, choices=TIPO_IMOVEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planejamento')

    # Endereço
    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)

    # Descrição
    descricao_completa = models.TextField()

    # Unidades
    total_unidades = models.PositiveIntegerField()
    unidades_disponiveis = models.PositiveIntegerField()

    # Comissão
    taxa_corretagem_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("4.00")
    )

    # Datas
    data_lancamento = models.DateField()
    data_entrega_prevista = models.DateField()

    # Mídia
    imagem_principal = models.ImageField(upload_to="empreendimentos/", blank=True, null=True)

    # Controle
    ativo = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)

    cnpj = models.CharField(max_length=20, default='1')

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class TipoUnidade(models.Model):
    empreendimento = models.ForeignKey(
        Empreendimento,
        on_delete=models.CASCADE,
        related_name='tipos_unidade'
    )

    nome = models.CharField(max_length=100, verbose_name='Nome do Tipo')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')

    # Características
    quartos = models.PositiveIntegerField(default=0)
    banheiros = models.PositiveIntegerField(default=0)
    vagas_garagem = models.PositiveIntegerField(default=0)
    area_util = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Valores
    valor_imovel = models.DecimalField(max_digits=12, decimal_places=2)
    valor_engenharia_necessaria = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )

    # Imagem
    imagem = models.ImageField(upload_to='tipos_unidade/', blank=True, null=True)

    # Controle
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Tipo de Unidade'
        verbose_name_plural = 'Tipos de Unidade'
        ordering = ['nome']
        unique_together = ('empreendimento', 'nome')

    def __str__(self):
        return f"{self.empreendimento.nome} - {self.nome}"
class UnidadeEmpreendimento(models.Model):
    STATUS_CHOICES = (
        ('disponivel', 'Disponível'),
        ('reservada', 'Reservada'),
        ('vendida', 'Vendida'),
    )

    empreendimento = models.ForeignKey(
        Empreendimento,
        on_delete=models.CASCADE,
        related_name='unidades'
    )
    tipo = models.ForeignKey(
        TipoUnidade,
        on_delete=models.PROTECT,
        related_name='unidades',
        verbose_name='Tipo'
    )
    numero = models.CharField(max_length=20, verbose_name='Número/Identificação')
    bloco = models.CharField(max_length=50, blank=True, null=True, verbose_name='Bloco/Torre')
    andar = models.CharField(max_length=10, blank=True, null=True, verbose_name='Andar')
    area_privativa = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Área Privativa (m²)'
    )
    quartos = models.IntegerField(verbose_name='Quartos')
    suites = models.IntegerField(default=0, verbose_name='Suítes')
    banheiros = models.IntegerField(verbose_name='Banheiros')
    vagas_garagem = models.IntegerField(default=0, verbose_name='Vagas de Garagem')
    
    valor_imovel = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor do Imóvel'
    )
    
    valor_engenharia = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor de Engenharia'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='disponivel',
        verbose_name='Status'
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Unidade'
        verbose_name_plural = 'Unidades'
        unique_together = ['empreendimento', 'numero']
        ordering = ['empreendimento', 'numero']

    @property
    def identificacao(self):
        partes = []

        if self.bloco:
            partes.append(f"Bloco {self.bloco}")

        if self.andar:
            partes.append(f"Andar {self.andar}")

        if self.numero:
            partes.append(f"Unidade {self.numero}")

        return " - ".join(partes)
    
    
    def __str__(self):
        return f"{self.empreendimento.nome} - {self.identificacao}"

class Cliente(models.Model):
    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
        ('uniao_estavel', 'União Estável'),
    ]

    ORIGEM_CHOICES = [
        ('site', 'Site'),
        ('indicacao', 'Indicação'),
        ('midia_social', 'Mídia Social'),
        ('evento', 'Evento'),
        ('plantao', 'Plantão'),
        ('outro', 'Outro'),
    ]

    # Dados pessoais
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)
    rg = models.CharField(max_length=20)
    data_nascimento = models.DateField()
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES)
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES)

    # Contato
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    # Endereço
    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=9)

    observacoes = models.TextField(blank=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)
    corretor_cadastro = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="clientes_cadastrados"
    )

    class Meta:
        ordering = ['nome_completo']

    def __str__(self):
        return f"{self.nome_completo} - {self.cpf}"
    
    def get_endereco_completo(self):
        partes = [
            self.rua,
            self.numero,
            self.complemento,
            self.bairro,
            self.cidade,
            self.estado,
            self.cep,
        ]
        return ", ".join([p for p in partes if p])


class Proposta(models.Model):
    STATUS_CHOICES = (
        ('analise', 'Em Análise'),
        ('aprovada', 'Aprovada'),
        ('reprovada', 'Reprovada'),
        ('cancelada', 'Cancelada'),
    )

    numero_proposta = models.CharField(max_length=20, unique=True, verbose_name='Número da Proposta')
    empreendimento = models.ForeignKey(Empreendimento, on_delete=models.PROTECT)
    unidade = models.ForeignKey(UnidadeEmpreendimento, on_delete=models.PROTECT)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    corretor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='propostas'
    )
    
    # ✅ NOVOS CAMPOS - Valores base para cálculo
    valor_construtora = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor para Construtora (sem juros)',
        help_text='Valor que será pago à construtora'
    )
    
    valor_parcela_cliente = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor Mensal que Cliente Pode Pagar',
        help_text='Informe o valor mensal que o cliente consegue pagar'
    )
    
    # ✅ Campos calculados mas editáveis
    valor_com_juros = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor COM Juros (50%)',
        help_text='Automático: Valor sem juros × 1,5'
    )
    
    quantidade_parcelas = models.IntegerField(
        verbose_name='Número de Parcelas',
        help_text='Automático: Valor com juros ÷ Valor da parcela'
    )
    
    # Financiamento
    valor_financiamento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Financiamento'
    )
    valor_subsidio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subsídio'
    )
    valor_fgts = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='FGTS'
    )
    
    # Total calculado
    total_aprovacao = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Total da Aprovação',
        help_text='Financiamento + Subsídio + FGTS'
    )
    
    # Entrada
    valor_entrada = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valor de Entrada'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='analise',
        verbose_name='Status'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')

    class Meta:
        verbose_name = 'Proposta'
        verbose_name_plural = 'Propostas'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Proposta {self.numero_proposta} - {self.cliente.nome}"
    
    def save(self, *args, **kwargs):
        # ✅ Cálculo automático do valor com juros (50%)
        if self.valor_construtora:
            self.valor_com_juros = self.valor_construtora * Decimal('1.5')
        
        # ✅ Cálculo automático do número de parcelas
        if self.valor_com_juros and self.valor_parcela_cliente and self.valor_parcela_cliente > 0:
            self.quantidade_parcelas = int(self.valor_com_juros / self.valor_parcela_cliente)
        
        # ✅ Total da aprovação
        self.total_aprovacao = (
            self.valor_financiamento + 
            self.valor_subsidio + 
            self.valor_fgts
        )
        
        super().save(*args, **kwargs)


# ✅ Signal para mudar status da unidade para "reservada" quando proposta é criada
@receiver(post_save, sender=Proposta)
def reservar_unidade_proposta(sender, instance, created, **kwargs):
    """Quando uma proposta é criada, a unidade vai para status 'reservada'"""
    if created:
        unidade = instance.unidade
        if unidade.status == 'disponivel':
            unidade.status = 'reservada'
            unidade.save()



class Contrato(models.Model):
    STATUS_CHOICES = (
        ('ativo', 'Ativo'),
        ('assinado', 'Assinado'),
        ('em_andamento', 'Em Andamento'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
        ('distratado', 'Distratado'),
    )

    numero_contrato = models.CharField(max_length=20, unique=True, verbose_name='Número do Contrato')
    
    proposta = models.OneToOneField(
        Proposta,
        on_delete=models.PROTECT,
        related_name='contrato'
    )

    # RELACIONAMENTOS AUTOMÁTICOS
    empreendimento = models.ForeignKey(
        Empreendimento,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    unidade = models.ForeignKey(
        UnidadeEmpreendimento,  # CORRIGIDO
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    corretor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    # DADOS COMPLEMENTARES DO CONTRATO
    registro_imovel = models.CharField(max_length=100, verbose_name='Registro do Imóvel', blank=True, null=True)
    matricula = models.CharField(max_length=50, verbose_name='Matrícula', blank=True, null=True)
    cartorio = models.CharField(max_length=200, verbose_name='Cartório', blank=True, null=True)

    # DATAS
    data_assinatura = models.DateField(verbose_name='Data de Assinatura', null=True, blank=True)
    data_vencimento_primeira_parcela = models.DateField(verbose_name='Vencimento 1ª Parcela', null=True, blank=True)

    # VALORES FINANCEIROS
    valor_imovel = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    valor_financiamento = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    valor_subsidio = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    valor_fgts = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    valor_entrada = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    valor_parcelamento = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    numero_parcelas = models.PositiveIntegerField(default=0)
    valor_parcela = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)

    # CONFIGURAÇÃO DE CONTRATO
    validade_dias = models.PositiveIntegerField(default=30)
    prorrogacao_dias = models.PositiveIntegerField(default=0)

    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contratos_criados')

    # STATUS
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo', verbose_name='Status')

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Contrato {self.numero_contrato}"

    def calcular_vencimento_primeira_parcela(self):
        """Calcula a data de vencimento da primeira parcela com base na data de assinatura e validade do contrato"""
        if self.data_assinatura and self.validade_dias:
            self.data_vencimento_primeira_parcela = self.data_assinatura + timedelta(days=self.validade_dias)
            return self.data_vencimento_primeira_parcela
        return None
    def get_valor_total(self):
        """
        Retorna o valor total do contrato somando entrada + financiamento + subsídio + FGTS
        """
        return self.valor_entrada + self.valor_financiamento + self.valor_subsidio + self.valor_fgts

    def get_valor_total_extenso(self):
        """
        Retorna o valor total do contrato por extenso, em português.
        Exemplo: "Um milhão e duzentos mil reais"
        """
        total = self.get_valor_total()
        return num2words(total, lang='pt_BR').capitalize() + " reais"
    
class HistoricoContrato(models.Model):
    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE,
        related_name='historico'
    )
    data = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    descricao = models.TextField()

    class Meta:
        verbose_name = 'Histórico de Contrato'
        verbose_name_plural = 'Históricos de Contratos'
        ordering = ['-data']


class Comissao(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('paga', 'Paga'),
        ('cancelada', 'Cancelada'),
    )

    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=20)  # 'corretor' ou 'gerente'
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    percentual = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    data_pagamento = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Comissão'
        verbose_name_plural = 'Comissões'


class Configuracao(models.Model):
    chave = models.CharField(max_length=50, unique=True)
    valor = models.TextField()
    descricao = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'

    def __str__(self):
        return f"{self.chave}: {self.valor}"

class ConfiguracaoSistema(models.Model):
    nome_empresa = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18)
    logo = models.ImageField(upload_to='config/', null=True, blank=True)

    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=20)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)

    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configuração do Sistema"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj