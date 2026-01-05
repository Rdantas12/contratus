# models.py - VERSÃO ATUALIZADA
# ✅ ALTERAÇÃO 1: Removido valor_imovel e valor_engenharia do Empreendimento
# ✅ ALTERAÇÃO 2: Nova lógica de parcelamento na Proposta

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from decimal import Decimal


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
        related_name='membros',
        verbose_name='Equipe'
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )

    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Cadastro'
    )

    foto = models.ImageField(
        upload_to='usuarios/',
        blank=True,
        null=True,
        verbose_name='Foto'
    )

    groups = models.ManyToManyField(
        Group,
        related_name='contratus_users',
        blank=True
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='contratus_users_permissions',
        blank=True
    )

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name()} - {self.get_nivel_display()}"


class Equipe(models.Model):
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nome da Equipe'
    )
    
    gerente = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'nivel': 'gerente'},
        related_name='equipes_gerenciadas',
        verbose_name='Gerente'
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    
    ativa = models.BooleanField(
        default=True,
        verbose_name='Ativa'
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    class Meta:
        verbose_name = 'Equipe'
        verbose_name_plural = 'Equipes'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def total_corretores(self):
        return self.membros.filter(nivel='corretor', ativo=True).count()


class Construtora(models.Model):
    razao_social = models.CharField(
        max_length=200,
        verbose_name='Razão Social'
    )
    
    nome_fantasia = models.CharField(
        max_length=200,
        verbose_name='Nome Fantasia'
    )
    
    cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name='CNPJ'
    )
    
    # Endereço
    rua = models.CharField(max_length=200, verbose_name='Rua')
    numero = models.CharField(max_length=20, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=100, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=2, verbose_name='Estado (UF)')
    cep = models.CharField(max_length=10, verbose_name='CEP')
    
    # Contatos
    telefone = models.CharField(max_length=20, verbose_name='Telefone')
    email = models.EmailField(verbose_name='E-mail')
    responsavel_legal = models.CharField(max_length=200, verbose_name='Responsável Legal')
    
    # Controle
    ativa = models.BooleanField(default=True, verbose_name='Ativa')
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    cadastrado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, 
        related_name='construtoras_cadastradas', verbose_name='Cadastrado por'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    class Meta:
        verbose_name = 'Construtora'
        verbose_name_plural = 'Construtoras'
        ordering = ['nome_fantasia']
    
    def __str__(self):
        return self.nome_fantasia
    
    def get_endereco_completo(self):
        complemento = f" {self.complemento}" if self.complemento else ""
        return f"{self.rua}, n° {self.numero}{complemento}, {self.bairro} - {self.cidade}/{self.estado}"


# ✅ ALTERAÇÃO 1: EMPREENDIMENTO SEM VALORES E SEM CARACTERÍSTICAS ESPECÍFICAS
class Empreendimento(models.Model):
    TIPO_IMOVEL_CHOICES = (
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('sobrado', 'Sobrado'),
        ('kitnet', 'Kitnet'),
    )
    
    STATUS_CHOICES = (
        ('lancamento', 'Lançamento'),
        ('em_obras', 'Em Obras'),
        ('pronto', 'Pronto para Entrega'),
        ('entregue', 'Entregue'),
        ('suspenso', 'Suspenso'),
    )
    
    # Dados Básicos
    nome = models.CharField(max_length=200, verbose_name='Nome do Empreendimento')
    construtora = models.ForeignKey(
        Construtora, on_delete=models.PROTECT, 
        related_name='empreendimentos', verbose_name='Construtora'
    )
    tipo_imovel = models.CharField(
        max_length=20, choices=TIPO_IMOVEL_CHOICES, verbose_name='Tipo de Imóvel'
    )
    
    # Endereço
    rua = models.CharField(max_length=200, verbose_name='Rua')
    numero = models.CharField(max_length=20, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=100, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=2, verbose_name='Estado (UF)')
    cep = models.CharField(max_length=10, verbose_name='CEP')
    
    # Descrição GERAL do empreendimento
    descricao_completa = models.TextField(
        verbose_name='Descrição Completa',
        help_text='Descrição geral do empreendimento e suas características comuns'
    )
    
    # ❌ REMOVIDO: quartos, banheiros, vagas_garagem, area_util
    # ✅ AGORA FICAM APENAS NO TipoUnidade
    
    # Unidades
    total_unidades = models.IntegerField(verbose_name='Total de Unidades')
    unidades_disponiveis = models.IntegerField(verbose_name='Unidades Disponíveis')
    
    taxa_corretagem_percentual = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.00, 
        verbose_name='Taxa de Corretagem (%)'
    )
    
    # Status e Datas
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, 
        default='lancamento', verbose_name='Status'
    )
    data_lancamento = models.DateField(blank=True, null=True, verbose_name='Data de Lançamento')
    data_entrega_prevista = models.DateField(blank=True, null=True, verbose_name='Data de Entrega Prevista')
    
    # Imagens
    imagem_principal = models.ImageField(
        upload_to='empreendimentos/', blank=True, null=True, 
        verbose_name='Imagem Principal'
    )
    
    # Controle
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    cadastrado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, 
        related_name='empreendimentos_cadastrados', verbose_name='Cadastrado por'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    class Meta:
        verbose_name = 'Empreendimento'
        verbose_name_plural = 'Empreendimentos'
        ordering = ['-data_cadastro']
    
    def __str__(self):
        return f"{self.nome} - {self.construtora.nome_fantasia}"
    
    def get_endereco_completo(self):
        complemento = f" {self.complemento}" if self.complemento else ""
        return f"{self.rua}, n° {self.numero}{complemento}, {self.bairro} - {self.cidade}/{self.estado}"
    
    def atualizar_unidades_disponiveis(self):
        vendidas = self.contratos.filter(status__in=['ativo', 'em_andamento']).count()
        self.unidades_disponiveis = self.total_unidades - vendidas
        self.save()


class TipoUnidade(models.Model):
    """
    Representa diferentes tipos de unidades dentro de um empreendimento
    Ex: "2 quartos - 60m²", "3 quartos + suíte - 80m²"
    
    ✅ AQUI FICAM OS VALORES (valor_imovel e valor_engenharia)
    """
    empreendimento = models.ForeignKey(
        Empreendimento, on_delete=models.CASCADE, 
        related_name='tipos_unidade', verbose_name='Empreendimento'
    )
    
    nome = models.CharField(
        max_length=200, verbose_name='Nome do Tipo',
        help_text='Ex: 2 Quartos, 3 Quartos + Suíte'
    )
    
    descricao = models.TextField(
        blank=True, verbose_name='Descrição',
        help_text='Descrição detalhada deste tipo de unidade'
    )
    
    # Características específicas
    quartos = models.IntegerField(default=0, verbose_name='Quartos')
    banheiros = models.IntegerField(default=0, verbose_name='Banheiros')
    vagas_garagem = models.IntegerField(default=0, verbose_name='Vagas de Garagem')
    area_util = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, 
        verbose_name='Área Útil (m²)'
    )
    
    # ✅ VALORES ESPECÍFICOS PARA ESTE TIPO
    valor_imovel = models.DecimalField(
        max_digits=12, decimal_places=2, 
        verbose_name='Valor do Imóvel'
    )
    
    valor_engenharia_necessaria = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True, 
        default=Decimal('0.00'),
        verbose_name='Valor da Engenharia Necessária',
        help_text='Deixe em branco se ainda não saiu a engenharia'
    )
    
    # Imagem (opcional)
    imagem = models.ImageField(
        upload_to='tipos_unidade/', blank=True, null=True, 
        verbose_name='Imagem/Planta'
    )
    
    # Controle
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    
    class Meta:
        verbose_name = 'Tipo de Unidade'
        verbose_name_plural = 'Tipos de Unidade'
        ordering = ['nome']
        unique_together = ['empreendimento', 'nome']
    
    def __str__(self):
        return f"{self.empreendimento.nome} - {self.nome}"
    
    def get_descricao_completa(self):
        """Retorna descrição formatada"""
        partes = []
        if self.quartos:
            partes.append(f"{self.quartos} quarto(s)")
        if self.banheiros:
            partes.append(f"{self.banheiros} banheiro(s)")
        if self.vagas_garagem:
            partes.append(f"{self.vagas_garagem} vaga(s)")
        if self.area_util:
            partes.append(f"{self.area_util}m²")
        
        return " | ".join(partes) if partes else "Sem características definidas"


class UnidadeEmpreendimento(models.Model):
    STATUS_CHOICES = (
        ('disponivel', 'Disponível'),
        ('reservada', 'Reservada'),
        ('vendida', 'Vendida'),
        ('bloqueada', 'Bloqueada'),
    )
    
    empreendimento = models.ForeignKey(
        Empreendimento, on_delete=models.CASCADE, 
        related_name='unidades', verbose_name='Empreendimento'
    )
    
    tipo_unidade = models.ForeignKey(
        TipoUnidade, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='unidades', verbose_name='Tipo de Unidade',
        help_text='Selecione o tipo se esta unidade tiver características específicas'
    )
    
    identificacao = models.CharField(
        max_length=50, verbose_name='Identificação',
        help_text='Ex: Casa 03, Apto 205, Bloco A - Apto 101'
    )
    
    andar = models.CharField(max_length=20, blank=True, verbose_name='Andar')
    bloco = models.CharField(max_length=20, blank=True, verbose_name='Bloco')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, 
        default='disponivel', verbose_name='Status'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    class Meta:
        verbose_name = 'Unidade'
        verbose_name_plural = 'Unidades'
        ordering = ['identificacao']
        unique_together = ['empreendimento', 'identificacao']
    
    def __str__(self):
        tipo_info = f" ({self.tipo_unidade.nome})" if self.tipo_unidade else ""
        return f"{self.empreendimento.nome} - {self.identificacao}{tipo_info}"
    
    # ✅ MÉTODOS PARA RETORNAR VALORES DO TIPO OU DO EMPREENDIMENTO
    def get_valor_imovel(self):
        """Retorna o valor do imóvel (do tipo de unidade)"""
        if self.tipo_unidade:
            return self.tipo_unidade.valor_imovel
        # Se não tiver tipo, não tem valor definido
        return Decimal('0.00')
    
    def get_valor_engenharia(self):
        """Retorna o valor da engenharia (do tipo de unidade)"""
        if self.tipo_unidade:
            return self.tipo_unidade.valor_engenharia_necessaria or Decimal('0.00')
        return Decimal('0.00')


class Cliente(models.Model):
    ORIGEM_CHOICES = (
        ('impulsionamento', 'Impulsionamento'),
        ('indicacao', 'Indicação'),
        ('walkin', 'Walk-in'),
        ('site', 'Site'),
        ('redes_sociais', 'Redes Sociais'),
        ('telefone', 'Telefone'),
        ('outros', 'Outros'),
    )
    
    # Dados Pessoais
    nome_completo = models.CharField(max_length=200, verbose_name='Nome Completo')
    cpf = models.CharField(max_length=14, unique=True, verbose_name='CPF')
    rg = models.CharField(max_length=20, blank=True, verbose_name='RG')
    data_nascimento = models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')
    estado_civil = models.CharField(max_length=50, blank=True, verbose_name='Estado Civil')
    
    # Contatos
    telefone = models.CharField(max_length=20, verbose_name='Telefone')
    email = models.EmailField(blank=True, verbose_name='E-mail')
    
    # Endereço
    rua = models.CharField(max_length=200, verbose_name='Rua')
    numero = models.CharField(max_length=20, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=100, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=2, verbose_name='Estado (UF)')
    cep = models.CharField(max_length=10, verbose_name='CEP')
    
    # Origem
    origem = models.CharField(
        max_length=20, choices=ORIGEM_CHOICES, 
        verbose_name='Origem do Cliente'
    )
    
    # Controle
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    cadastrado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, 
        related_name='clientes_cadastrados', verbose_name='Cadastrado por'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome_completo']
    
    def __str__(self):
        return f"{self.nome_completo} - {self.cpf}"
    
    def get_endereco_completo(self):
        complemento = f" {self.complemento}" if self.complemento else ""
        return f"{self.rua}, n° {self.numero}{complemento}. {self.bairro} - {self.cidade}/{self.estado}"


# ✅ ALTERAÇÃO 2: NOVA LÓGICA DE PARCELAMENTO
class Proposta(models.Model):
    STATUS_CHOICES = (
        ('rascunho', 'Rascunho'),
        ('enviada', 'Enviada'),
        ('aprovada', 'Aprovada'),
        ('recusada', 'Recusada'),
        ('expirada', 'Expirada'),
    )
    
    # Relacionamentos
    empreendimento = models.ForeignKey(
        Empreendimento, on_delete=models.PROTECT, 
        related_name='propostas', verbose_name='Empreendimento'
    )
    unidade = models.ForeignKey(
        UnidadeEmpreendimento, on_delete=models.PROTECT, 
        related_name='propostas', verbose_name='Unidade Escolhida'
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, 
        related_name='propostas', verbose_name='Cliente'
    )
    corretor = models.ForeignKey(
        User, on_delete=models.PROTECT, 
        limit_choices_to={'nivel': 'corretor'},
        related_name='propostas_criadas', verbose_name='Corretor'
    )
    
    # Valores - Negociação
    valor_engenharia_necessaria = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True, 
        default=Decimal('0.00'),
        verbose_name='Engenharia Necessária',
        help_text='Deixe em branco se ainda não saiu a engenharia'
    )
    
    valor_imovel = models.DecimalField(
        max_digits=12, decimal_places=2, 
        verbose_name='Valor do Imóvel'
    )
    
    valor_financiamento = models.DecimalField(
        max_digits=12, decimal_places=2, 
        verbose_name='Valor do Financiamento'
    )
    
    valor_subsidio = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, 
        verbose_name='Valor do Subsídio'
    )
    
    valor_fgts = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, 
        verbose_name='Valor FGTS'
    )
    
    valor_sinal = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, 
        verbose_name='Valor do Sinal'
    )
    
    valor_entrada = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, 
        verbose_name='Valor da Entrada'
    )
    
    # ✅ NOVA LÓGICA DE PARCELAMENTO
    valor_parcelamento_construtora = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name='Parcelamento Construtora (SEM juros)',
        help_text='Valor que será pago à construtora (sem juros) - informado pelo corretor'
    )
    
    valor_parcela_cliente = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Valor da Parcela (que o cliente pode pagar)',
        help_text='Valor que o cliente consegue pagar mensalmente'
    )
    
    numero_parcelas = models.IntegerField(
        verbose_name='Número de Parcelas',
        help_text='Calculado automaticamente: parcelamento_construtora / valor_parcela'
    )
    
    # Valor COM 50% de juros (só para mostrar na proposta)
    valor_parcelamento_com_juros = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name='Parcelamento com Juros (50% - só para proposta)',
        help_text='Calculado automaticamente: valor_construtora * 1.5'
    )
    
    # Total
    total_aprovacao = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name='Total da Aprovação'
    )
    
    # Status e Controle
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, 
        default='rascunho', verbose_name='Status'
    )
    
    numero_proposta = models.CharField(
        max_length=50, unique=True, blank=True, 
        verbose_name='Número da Proposta'
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_envio = models.DateTimeField(blank=True, null=True, verbose_name='Data de Envio')
    data_resposta = models.DateTimeField(blank=True, null=True, verbose_name='Data de Resposta')
    validade_dias = models.IntegerField(default=30, verbose_name='Validade (dias)')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    arquivo_pdf = models.FileField(
        upload_to='propostas/', blank=True, null=True, 
        verbose_name='Arquivo PDF'
    )
    
    class Meta:
        verbose_name = 'Proposta'
        verbose_name_plural = 'Propostas'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Proposta {self.numero_proposta} - {self.cliente.nome_completo}"
    
    def save(self, *args, **kwargs):
        # Gerar número da proposta automaticamente
        if not self.numero_proposta:
            from datetime import datetime
            ano = datetime.now().year
            ultimo = Proposta.objects.filter(
                numero_proposta__startswith=f'PROP-{ano}'
            ).order_by('-numero_proposta').first()
            
            if ultimo:
                ultimo_numero = int(ultimo.numero_proposta.split('-')[-1])
                proximo_numero = ultimo_numero + 1
            else:
                proximo_numero = 1
            
            self.numero_proposta = f'PROP-{ano}-{proximo_numero:05d}'
        
        # ✅ CALCULAR AUTOMATICAMENTE O VALOR COM JUROS (50%)
        self.valor_parcelamento_com_juros = self.valor_parcelamento_construtora * Decimal('1.5')
        
        # ✅ CALCULAR TOTAL DE APROVAÇÃO
        self.total_aprovacao = (
            self.valor_financiamento + 
            self.valor_subsidio + 
            self.valor_fgts
        )
        
        super().save(*args, **kwargs)


class Contrato(models.Model):
    STATUS_CHOICES = (
        ('rascunho', 'Rascunho'),
        ('ativo', 'Ativo'),
        ('em_andamento', 'Em Andamento'),
        ('aguardando_assinatura', 'Aguardando Assinatura'),
        ('assinado', 'Assinado'),
        ('em_analise_banco', 'Em Análise no Banco'),
        ('aprovado_banco', 'Aprovado pelo Banco'),
        ('reprovado_banco', 'Reprovado pelo Banco'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
        ('distratado', 'Distratado'),
    )
    
    # Relacionamentos
    proposta = models.OneToOneField(
        Proposta, on_delete=models.PROTECT, 
        related_name='contrato', verbose_name='Proposta'
    )
    empreendimento = models.ForeignKey(
        Empreendimento, on_delete=models.PROTECT, 
        related_name='contratos', verbose_name='Empreendimento'
    )
    unidade = models.ForeignKey(
        UnidadeEmpreendimento, on_delete=models.PROTECT, 
        related_name='contratos', verbose_name='Unidade'
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, 
        related_name='contratos', verbose_name='Cliente/Comprador'
    )
    corretor = models.ForeignKey(
        User, on_delete=models.PROTECT, 
        limit_choices_to={'nivel': 'corretor'},
        related_name='contratos_criados', verbose_name='Corretor'
    )
    
    # Dados do Contrato (copiados da proposta)
    valor_imovel = models.DecimalField(
        max_digits=12, decimal_places=2, 
        verbose_name='Valor do Imóvel'
    )
    valor_financiamento = models.DecimalField(
        max_digits=12, decimal_places=2, 
        verbose_name='Valor do Financiamento'
    )
    valor_subsidio = models.DecimalField(
        max_digits=12, decimal_places=2, 
        verbose_name='Valor do Subsídio'
    )
    valor_fgts = models.DecimalField(
        max_digits=12, decimal_places=2, 
        verbose_name='Valor FGTS'
    )
    valor_entrada = models.DecimalField(
        max_digits=12, decimal_places=2, 
        verbose_name='Valor da Entrada'
    )
    
    # ✅ CONTRATO USA O VALOR SEM JUROS
    valor_parcelamento = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name='Valor Parcelamento (SEM juros - para construtora)'
    )
    
    numero_parcelas = models.IntegerField(
        verbose_name='Número de Parcelas'
    )
    
    valor_parcela = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Valor da Parcela'
    )
    
    # Controle de Contrato
    numero_contrato = models.CharField(
        max_length=50, unique=True, blank=True, 
        verbose_name='Número do Contrato'
    )
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, 
        default='rascunho', verbose_name='Status'
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    data_assinatura = models.DateField(blank=True, null=True, verbose_name='Data de Assinatura')
    validade_dias = models.IntegerField(default=180, verbose_name='Validade (dias)')
    data_vencimento = models.DateField(blank=True, null=True, verbose_name='Data de Vencimento')
    prorrogacao_dias = models.IntegerField(default=90, verbose_name='Prorrogação (dias)')
    
    # Testemunhas
    testemunha1_nome = models.CharField(max_length=200, blank=True, verbose_name='Nome da Testemunha 1')
    testemunha1_cpf = models.CharField(max_length=14, blank=True, verbose_name='CPF da Testemunha 1')
    testemunha2_nome = models.CharField(max_length=200, blank=True, verbose_name='Nome da Testemunha 2')
    testemunha2_cpf = models.CharField(max_length=14, blank=True, verbose_name='CPF da Testemunha 2')
    
    # Arquivos
    arquivo_contrato_pdf = models.FileField(
        upload_to='contratos/', blank=True, null=True, 
        verbose_name='Contrato PDF'
    )
    arquivo_auto_visita_pdf = models.FileField(
        upload_to='contratos/auto_visita/', blank=True, null=True, 
        verbose_name='Auto de Visita PDF'
    )
    arquivo_contrato_assinado = models.FileField(
        upload_to='contratos/assinados/', blank=True, null=True, 
        verbose_name='Contrato Assinado'
    )
    
    # Observações
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    motivo_cancelamento = models.TextField(blank=True, verbose_name='Motivo do Cancelamento')
    
    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Contrato {self.numero_contrato} - {self.cliente.nome_completo}"
    
    def save(self, *args, **kwargs):
        # Gerar número do contrato automaticamente
        if not self.numero_contrato:
            from datetime import datetime, timedelta
            ano = datetime.now().year
            ultimo = Contrato.objects.filter(
                numero_contrato__startswith=f'CONT-{ano}'
            ).order_by('-numero_contrato').first()
            
            if ultimo:
                ultimo_numero = int(ultimo.numero_contrato.split('-')[-1])
                proximo_numero = ultimo_numero + 1
            else:
                proximo_numero = 1
            
            self.numero_contrato = f'CONT-{ano}-{proximo_numero:05d}'
        
        # Calcular data de vencimento
        if self.data_assinatura and not self.data_vencimento:
            from datetime import timedelta
            self.data_vencimento = self.data_assinatura + timedelta(days=self.validade_dias)
        
        super().save(*args, **kwargs)
    
    def get_valor_total_extenso(self):
        from num2words import num2words
        valor_inteiro = int(self.valor_imovel)
        valor_centavos = int((self.valor_imovel - valor_inteiro) * 100)
        
        extenso = num2words(valor_inteiro, lang='pt_BR').upper()
        
        if valor_centavos > 0:
            return f"{extenso} REAIS E {num2words(valor_centavos, lang='pt_BR').upper()} CENTAVOS"
        return f"{extenso} REAIS"


class HistoricoContrato(models.Model):
    contrato = models.ForeignKey(
        Contrato, on_delete=models.CASCADE, 
        related_name='historico', verbose_name='Contrato'
    )
    usuario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, 
        verbose_name='Usuário'
    )
    status_anterior = models.CharField(max_length=30, verbose_name='Status Anterior')
    status_novo = models.CharField(max_length=30, verbose_name='Status Novo')
    data_alteracao = models.DateTimeField(auto_now_add=True, verbose_name='Data da Alteração')
    observacao = models.TextField(blank=True, verbose_name='Observação')
    
    class Meta:
        verbose_name = 'Histórico do Contrato'
        verbose_name_plural = 'Históricos dos Contratos'
        ordering = ['-data_alteracao']
    
    def __str__(self):
        return f"{self.contrato.numero_contrato} - {self.status_anterior} → {self.status_novo}"


class Comissao(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('paga', 'Paga'),
        ('cancelada', 'Cancelada'),
    )
    
    contrato = models.OneToOneField(
        Contrato, on_delete=models.CASCADE, 
        related_name='comissao', verbose_name='Contrato'
    )
    corretor = models.ForeignKey(
        User, on_delete=models.PROTECT, 
        related_name='comissoes', verbose_name='Corretor'
    )
    
    valor_base = models.DecimalField(
        max_digits=12, decimal_places=2, 
        verbose_name='Valor Base (Imóvel)'
    )
    percentual = models.DecimalField(
        max_digits=5, decimal_places=2, 
        verbose_name='Percentual (%)'
    )
    valor_comissao = models.DecimalField(
        max_digits=12, decimal_places=2, 
        verbose_name='Valor da Comissão'
    )
    valor_descontos = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, 
        verbose_name='Descontos'
    )
    valor_liquido = models.DecimalField(
        max_digits=12, decimal_places=2, 
        verbose_name='Valor Líquido'
    )
    
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, 
        default='pendente', verbose_name='Status'
    )
    
    data_previsao_pagamento = models.DateField(
        blank=True, null=True, 
        verbose_name='Previsão de Pagamento'
    )
    data_pagamento = models.DateField(
        blank=True, null=True, 
        verbose_name='Data de Pagamento'
    )
    forma_pagamento = models.CharField(
        max_length=50, blank=True, 
        verbose_name='Forma de Pagamento'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    class Meta:
        verbose_name = 'Comissão'
        verbose_name_plural = 'Comissões'
        ordering = ['-data_previsao_pagamento']
    
    def __str__(self):
        return f"Comissão {self.corretor.get_full_name()} - {self.contrato.numero_contrato}"
    
    def save(self, *args, **kwargs):
        # Calcular valor da comissão
        self.valor_comissao = (self.valor_base * self.percentual) / 100
        self.valor_liquido = self.valor_comissao - self.valor_descontos
        super().save(*args, **kwargs)


class Configuracao(models.Model):
    # Dados da Imobiliária
    nome_imobiliaria = models.CharField(
        max_length=200, default='CLICK GR2 IMOBILIÁRIA LTDA', 
        verbose_name='Nome da Imobiliária'
    )
    cnpj_imobiliaria = models.CharField(
        max_length=18, default='26.903.395/0001-26', 
        verbose_name='CNPJ'
    )
    endereco_imobiliaria = models.CharField(
        max_length=300, 
        default='Rua Gervásio Neri, n° 48 - Vila Iara - São Gonçalo/RJ',
        verbose_name='Endereço'
    )
    cep_imobiliaria = models.CharField(
        max_length=10, default='24465-016', 
        verbose_name='CEP'
    )
    telefone_imobiliaria = models.CharField(
        max_length=20, default='(21) 96594-4343', 
        verbose_name='Telefone'
    )
    email_imobiliaria = models.EmailField(blank=True, verbose_name='E-mail')
    site_imobiliaria = models.URLField(
        default='www.clickimoveisrj.com', 
        verbose_name='Site'
    )
    instagram_imobiliaria = models.CharField(
        max_length=50, default='@imoveis.click', 
        verbose_name='Instagram'
    )
    logo = models.ImageField(
        upload_to='configuracao/', blank=True, null=True, 
        verbose_name='Logo'
    )
    
    # Configurações de Contrato
    validade_proposta_padrao = models.IntegerField(
        default=30, 
        verbose_name='Validade Padrão Proposta (dias)'
    )
    validade_contrato_padrao = models.IntegerField(
        default=180, 
        verbose_name='Validade Padrão Contrato (dias)'
    )
    prorrogacao_contrato_padrao = models.IntegerField(
        default=90, 
        verbose_name='Prorrogação Padrão Contrato (dias)'
    )
    taxa_corretagem_padrao = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.00, 
        verbose_name='Taxa Corretagem Padrão (%)'
    )
    
    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'
    
    def __str__(self):
        return 'Configurações do Sistema'
    
    def save(self, *args, **kwargs):
        # Garantir que só existe uma instância
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
