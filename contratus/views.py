from django.db.models.functions import TruncMonth, TruncWeek
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Sum, Avg, Max, Min
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import io

from num2words import num2words

from .models import (
    User, Equipe, Construtora, Empreendimento, UnidadeEmpreendimento,
    Cliente, Proposta, Contrato, HistoricoContrato, Comissao, Configuracao, TipoUnidade, ConfiguracaoSistema
)
from .forms import (
    LoginForm, ConstrutoraForm, EmpreendimentoForm, UnidadeForm,
    ClienteForm, PropostaForm, ContratoForm, UserForm, EquipeForm, TipoUnidadeForm, UnidadesEmLoteForm
)


# =====================================================
# AUTENTICAÇÃO
# =====================================================


def login_view(request):
    """Login do sistema"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Usuário inativo. Contate o administrador.')
                else:
                    login(request, user)
                    messages.success(
                        request,
                        f'Bem-vindo, {user.get_full_name() or user.username}!'
                    )
                    return redirect('dashboard')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = LoginForm()
    
    return render(request, 'contratus/login.html', {'form': form})

@login_required
def logout_view(request):
    """Logout do sistema"""
    logout(request)
    messages.success(request, 'Você saiu do sistema.')
    return redirect('login')

# =====================================================
# DASHBOARD
# =====================================================
@login_required
def dashboard(request):
    """Dashboard completo com controle de acesso por nível"""
    user = request.user
    hoje = timezone.now().date()
    
    # ============================================
    # FILTROS DINÂMICOS
    # ============================================
    periodo = request.GET.get('periodo', '30')  # Últimos 30 dias por padrão
    status_filtro = request.GET.get('status', 'todos')
    equipe_filtro = request.GET.get('equipe', 'todas')
    corretor_filtro = request.GET.get('corretor', 'todos')
    empreendimento_filtro = request.GET.get('empreendimento', 'todos')
    
    # Calcular data inicial baseado no período
    if periodo == '7':
        data_inicio = hoje - timedelta(days=7)
        periodo_label = 'Últimos 7 dias'
    elif periodo == '30':
        data_inicio = hoje - timedelta(days=30)
        periodo_label = 'Últimos 30 dias'
    elif periodo == '90':
        data_inicio = hoje - timedelta(days=90)
        periodo_label = 'Últimos 90 dias'
    elif periodo == 'ano':
        data_inicio = hoje.replace(month=1, day=1)
        periodo_label = 'Este ano'
    elif periodo == 'todos':
        data_inicio = None
        periodo_label = 'Todos os períodos'
    else:
        data_inicio = hoje - timedelta(days=30)
        periodo_label = 'Últimos 30 dias'
    
    # ============================================
    # CONTROLE DE ACESSO - QUERIES BASE
    # ============================================
    
    if user.nivel == 'administrador':
        # ADMIN vê tudo
        contratos_query = Contrato.objects.select_related('proposta', 'criado_por')
        propostas_query = Proposta.objects.select_related('cliente', 'empreendimento', 'unidade', 'corretor')
        usuarios_query = User.objects.filter(is_active=True)
        equipes_disponiveis = Equipe.objects.filter(ativa=True)
        pode_ver_todas_equipes = True
        
    elif user.nivel == 'gerente':
        # GERENTE vê apenas sua equipe
        if user.equipe:
            corretores_equipe = user.equipe.membros.filter(nivel='corretor', is_active=True)
            contratos_query = Contrato.objects.filter(
                criado_por__in=corretores_equipe
            ).select_related('proposta', 'criado_por')
            propostas_query = Proposta.objects.filter(
                corretor__in=corretores_equipe
            ).select_related('cliente', 'empreendimento', 'unidade', 'corretor')
            usuarios_query = corretores_equipe
            equipes_disponiveis = Equipe.objects.filter(id=user.equipe.id)
            pode_ver_todas_equipes = False
        else:
            contratos_query = Contrato.objects.none()
            propostas_query = Proposta.objects.none()
            usuarios_query = User.objects.none()
            equipes_disponiveis = Equipe.objects.none()
            pode_ver_todas_equipes = False
            
    else:  # CORRETOR
        # CORRETOR vê apenas os próprios
        contratos_query = Contrato.objects.filter(
            criado_por=user
        ).select_related('proposta', 'criado_por')
        propostas_query = Proposta.objects.filter(
            corretor=user
        ).select_related('cliente', 'empreendimento', 'unidade', 'corretor')
        usuarios_query = User.objects.filter(id=user.id)
        equipes_disponiveis = Equipe.objects.none()
        pode_ver_todas_equipes = False
    
    # ============================================
    # APLICAR FILTROS
    # ============================================
    
    # Filtro de período
    if data_inicio:
        contratos_query = contratos_query.filter(data_criacao__date__gte=data_inicio)
        propostas_query = propostas_query.filter(data_criacao__date__gte=data_inicio)
    
    # Filtro de status
    if status_filtro != 'todos':
        contratos_query = contratos_query.filter(status=status_filtro)
    
    # Filtro de equipe (apenas admin)
    if equipe_filtro != 'todas' and user.nivel == 'administrador':
        try:
            equipe_obj = Equipe.objects.get(id=int(equipe_filtro))
            corretores_equipe = equipe_obj.membros.filter(nivel='corretor')
            contratos_query = contratos_query.filter(criado_por__in=corretores_equipe)
            propostas_query = propostas_query.filter(corretor__in=corretores_equipe)
        except (ValueError, Equipe.DoesNotExist):
            pass
    
    # Filtro de corretor (admin e gerente)
    if corretor_filtro != 'todos' and user.nivel in ['administrador', 'gerente']:
        try:
            contratos_query = contratos_query.filter(criado_por_id=int(corretor_filtro))
            propostas_query = propostas_query.filter(corretor_id=int(corretor_filtro))
        except ValueError:
            pass
    
    # Filtro de empreendimento
    if empreendimento_filtro != 'todos':
        try:
            contratos_query = contratos_query.filter(proposta__empreendimento_id=int(empreendimento_filtro))
            propostas_query = propostas_query.filter(empreendimento_id=int(empreendimento_filtro))
        except ValueError:
            pass
    
    # ============================================
    # ESTATÍSTICAS GERAIS (CARDS)
    # ============================================
    
    total_contratos = contratos_query.count()
    total_propostas = propostas_query.count()
    
    # ✅ CORRIGIDO: Status agora existe no modelo
    contratos_ativos = contratos_query.filter(status__in=['ativo', 'em_andamento', 'assinado']).count()
    contratos_finalizados = contratos_query.filter(status='finalizado').count()
    contratos_cancelados = contratos_query.filter(status__in=['cancelado', 'distratado']).count()
    
    # Status das propostas
    propostas_pendentes = propostas_query.filter(status='analise').count()
    propostas_aprovadas = propostas_query.filter(status='aprovada').count()
    propostas_recusadas = propostas_query.filter(status__in=['reprovada', 'cancelada']).count()
    
    # ============================================
    # VALORES FINANCEIROS
    # ============================================
    
    # ✅ CORRIGIDO: Usar valores da proposta através do relacionamento
    valor_total_contratos = contratos_query.aggregate(
        total=Sum('proposta__valor_com_juros')
    )['total'] or Decimal('0')
    
    valor_total_comissoes = contratos_query.filter(
        status__in=['ativo', 'assinado', 'em_andamento', 'finalizado']
    ).aggregate(
        total=Sum('proposta__valor_com_juros')
    )['total'] or Decimal('0')
    
    # Calcular comissão estimada
    # Assumindo 3% de comissão total (ajuste conforme sua regra de negócio)
    comissao_estimada = valor_total_comissoes * Decimal('0.03')
    
    # Taxa de conversão
    if total_propostas > 0:
        taxa_conversao = (propostas_aprovadas / total_propostas) * 100
    else:
        taxa_conversao = 0
    
    # ============================================
    # GRÁFICOS - EVOLUÇÃO MENSAL
    # ============================================
    
    # Contratos por mês (últimos 6 meses)
    seis_meses_atras = hoje - timedelta(days=180)
    
    contratos_por_mes = contratos_query.filter(
        data_criacao__date__gte=seis_meses_atras
    ).annotate(
        mes=TruncMonth('data_criacao')
    ).values('mes').annotate(
        total=Count('id'),
        valor=Sum('proposta__valor_com_juros')
    ).order_by('mes')
    
    # Preparar dados para o gráfico
    meses_labels = []
    meses_contratos = []
    meses_valores = []
    
    for item in contratos_por_mes:
        mes_nome = item['mes'].strftime('%b/%Y')
        meses_labels.append(mes_nome)
        meses_contratos.append(item['total'])
        meses_valores.append(float(item['valor'] or 0))
    
    # ============================================
    # GRÁFICO - STATUS DOS CONTRATOS
    # ============================================
    
    status_contratos = contratos_query.values('status').annotate(
        total=Count('id')
    ).order_by('-total')
    
    status_labels = []
    status_valores = []
    
    for item in status_contratos:
        status_dict = dict(Contrato.STATUS_CHOICES)
        status_labels.append(status_dict.get(item['status'], item['status']))
        status_valores.append(item['total'])
    
    # ============================================
    # GRÁFICO - STATUS DAS PROPOSTAS
    # ============================================
    
    status_propostas = propostas_query.values('status').annotate(
        total=Count('id')
    ).order_by('-total')
    
    propostas_status_labels = []
    propostas_status_valores = []
    
    for item in status_propostas:
        status_dict = dict(Proposta.STATUS_CHOICES)
        propostas_status_labels.append(status_dict.get(item['status'], item['status']))
        propostas_status_valores.append(item['total'])
    
    # ============================================
    # RANKING DE CORRETORES
    # ============================================
    
    if user.nivel in ['administrador', 'gerente']:
        # ✅ CORRIGIDO: Usar related_name correto
        ranking_corretores = usuarios_query.annotate(
            total_contratos=Count(
                'contratos_criados',
                filter=Q(contratos_criados__id__in=contratos_query.values_list('id', flat=True))
            ),
            total_propostas=Count(
                'propostas',
                filter=Q(propostas__id__in=propostas_query.values_list('id', flat=True))
            ),
            valor_total=Sum(
                'contratos_criados__proposta__valor_com_juros',
                filter=Q(contratos_criados__id__in=contratos_query.values_list('id', flat=True))
            )
        ).filter(
            Q(total_contratos__gt=0) | Q(total_propostas__gt=0)
        ).order_by('-total_contratos')[:10]
    else:
        ranking_corretores = None
    
    # ============================================
    # EMPREENDIMENTOS MAIS VENDIDOS
    # ============================================
    
    # ✅ CORRIGIDO: Acessar empreendimento através da proposta
    empreendimentos_top = contratos_query.values(
        'proposta__empreendimento__nome'
    ).annotate(
        total=Count('id'),
        valor_total=Sum('proposta__valor_com_juros')
    ).order_by('-total')[:5]
    
    # ============================================
    # CONTRATOS RECENTES
    # ============================================
    
    contratos_recentes = contratos_query.select_related(
        'proposta__cliente',
        'proposta__corretor',
        'proposta__empreendimento',
        'proposta__unidade',
        'criado_por'
    ).order_by('-data_criacao')[:10]
    
    # ============================================
    # PROPOSTAS RECENTES
    # ============================================
    
    propostas_recentes = propostas_query.select_related(
        'cliente', 'corretor', 'empreendimento', 'unidade'
    ).order_by('-data_criacao')[:10]
    
    # ============================================
    # COMPARATIVO COM PERÍODO ANTERIOR
    # ============================================
    
    if data_inicio:
        # Calcular período anterior
        dias_periodo = (hoje - data_inicio).days
        data_inicio_anterior = data_inicio - timedelta(days=dias_periodo)
        data_fim_anterior = data_inicio - timedelta(days=1)
        
        # Estatísticas do período anterior
        if user.nivel == 'administrador':
            contratos_anterior = Contrato.objects.filter(
                data_criacao__date__range=[data_inicio_anterior, data_fim_anterior]
            ).count()
        elif user.nivel == 'gerente' and user.equipe:
            corretores_equipe = user.equipe.membros.filter(nivel='corretor')
            contratos_anterior = Contrato.objects.filter(
                criado_por__in=corretores_equipe,
                data_criacao__date__range=[data_inicio_anterior, data_fim_anterior]
            ).count()
        else:
            contratos_anterior = Contrato.objects.filter(
                criado_por=user,
                data_criacao__date__range=[data_inicio_anterior, data_fim_anterior]
            ).count()
        
        # Calcular variação percentual
        if contratos_anterior > 0:
            variacao_contratos = ((total_contratos - contratos_anterior) / contratos_anterior) * 100
        else:
            variacao_contratos = 100 if total_contratos > 0 else 0
    else:
        variacao_contratos = 0
    
    # ============================================
    # CONTEXT - ENVIAR PARA TEMPLATE
    # ============================================
    
    context = {
        # Usuário e permissões
        'user': user,
        'pode_ver_todas_equipes': pode_ver_todas_equipes,
        
        # Filtros
        'periodo': periodo,
        'periodo_label': periodo_label,
        'status_filtro': status_filtro,
        'equipe_filtro': equipe_filtro,
        'corretor_filtro': corretor_filtro,
        'empreendimento_filtro': empreendimento_filtro,
        
        # Opções para filtros
        'equipes_disponiveis': equipes_disponiveis,
        'corretores_disponiveis': usuarios_query,
        'empreendimentos_disponiveis': Empreendimento.objects.all(),
        'status_choices': Contrato.STATUS_CHOICES,
        
        # Estatísticas gerais
        'total_contratos': total_contratos,
        'total_propostas': total_propostas,
        'contratos_ativos': contratos_ativos,
        'contratos_finalizados': contratos_finalizados,
        'contratos_cancelados': contratos_cancelados,
        'propostas_pendentes': propostas_pendentes,
        'propostas_aprovadas': propostas_aprovadas,
        'propostas_recusadas': propostas_recusadas,
        
        # Valores financeiros
        'valor_total_contratos': valor_total_contratos,
        'comissao_estimada': comissao_estimada,
        'taxa_conversao': round(taxa_conversao, 1),
        'variacao_contratos': round(variacao_contratos, 1),
        
        # Gráficos - JSON para JavaScript
        'grafico_meses_labels': meses_labels,
        'grafico_meses_contratos': meses_contratos,
        'grafico_meses_valores': meses_valores,
        'grafico_status_labels': status_labels,
        'grafico_status_valores': status_valores,
        'grafico_propostas_labels': propostas_status_labels,
        'grafico_propostas_valores': propostas_status_valores,
        
        # Rankings e tops
        'ranking_corretores': ranking_corretores,
        'empreendimentos_top': empreendimentos_top,
        
        # Listas recentes
        'contratos_recentes': contratos_recentes,
        'propostas_recentes': propostas_recentes,
    }
    
    return render(request, 'contratus/dashboard.html', context)



# =====================================================
# CONSTRUTORAS (apenas administrador)
# =====================================================

@login_required
def construtora_list(request):
    """Lista de construtoras - todos podem ver, apenas admin edita"""
    construtoras = Construtora.objects.all()
    
    # Verificar permissão de edição
    pode_editar = request.user.nivel == 'administrador'
    
    return render(request, 'contratus/construtoras/list.html', {
        'construtoras': construtoras,
        'pode_editar': pode_editar
    })


@login_required
def construtora_create(request):
    """Criar construtora - apenas administrador"""
    if request.user.nivel != 'administrador':
        messages.error(request, 'Acesso negado. Apenas administradores podem criar construtoras.')
        return redirect('construtora_list')
    
    if request.method == 'POST':
        form = ConstrutoraForm(request.POST)
        if form.is_valid():
            construtora = form.save(commit=False)
            construtora.cadastrado_por = request.user
            construtora.save()
            messages.success(request, 'Construtora cadastrada com sucesso!')
            return redirect('construtora_list')
    else:
        form = ConstrutoraForm()
    
    return render(request, 'contratus/construtoras/form.html', {'form': form, 'title': 'Nova Construtora'})

@login_required
def construtora_edit(request, pk):
    """Editar construtora - apenas administrador"""
    if request.user.nivel != 'administrador':
        messages.error(request, 'Acesso negado. Apenas administradores podem editar construtoras.')
        return redirect('construtora_list')
    
    construtora = get_object_or_404(Construtora, pk=pk)
    
    if request.method == 'POST':
        form = ConstrutoraForm(request.POST, instance=construtora)
        if form.is_valid():
            form.save()
            messages.success(request, 'Construtora atualizada com sucesso!')
            return redirect('construtora_list')
    else:
        form = ConstrutoraForm(instance=construtora)
    
    return render(request, 'contratus/construtoras/form.html', {'form': form, 'title': 'Editar Construtora'})


# =====================================================
# EMPREENDIMENTOS (apenas administrador)
# =====================================================
@login_required
def empreendimento_list(request):
    """Lista de empreendimentos - todos podem ver, apenas admin edita"""
    empreendimentos = Empreendimento.objects.all()
    
    # Verificar permissão de edição
    pode_editar = request.user.nivel == 'administrador'
    
    return render(request, 'contratus/empreendimentos/list.html', {
        'empreendimentos': empreendimentos,
        'pode_editar': pode_editar
    })


@login_required
def empreendimento_create(request):
    """Criar empreendimento - apenas administrador"""
    if request.user.nivel != 'administrador':
        messages.error(request, 'Acesso negado. Apenas administradores podem criar empreendimentos.')
        return redirect('empreendimento_list')
    
    if request.method == 'POST':
        form = EmpreendimentoForm(request.POST, request.FILES)
        if form.is_valid():
            empreendimento = form.save(commit=False)
            empreendimento.cadastrado_por = request.user
            empreendimento.save()
            messages.success(request, 'Empreendimento cadastrado com sucesso!')
            return redirect('empreendimento_list')
    else:
        form = EmpreendimentoForm()
    
    return render(request, 'contratus/empreendimentos/form.html', {'form': form, 'title': 'Novo Empreendimento'})


@login_required
def empreendimento_edit(request, pk):
    """Editar empreendimento - apenas administrador"""
    if request.user.nivel != 'administrador':
        messages.error(request, 'Acesso negado. Apenas administradores podem editar empreendimentos.')
        return redirect('empreendimento_list')
    
    empreendimento = get_object_or_404(Empreendimento, pk=pk)
    
    if request.method == 'POST':
        form = EmpreendimentoForm(request.POST, request.FILES, instance=empreendimento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empreendimento atualizado com sucesso!')
            return redirect('empreendimento_list')
    else:
        form = EmpreendimentoForm(instance=empreendimento)
    
    return render(request, 'contratus/empreendimentos/form.html', {'form': form, 'title': 'Editar Empreendimento'})


@login_required
def empreendimento_detail(request, pk):
    """Detalhes do empreendimento com unidades - todos podem ver"""
    empreendimento = get_object_or_404(Empreendimento, pk=pk)
    
    # ✅ CORREÇÃO: Buscar as unidades do empreendimento
    unidades = empreendimento.unidades.select_related('tipo').all()
    
    # Verificar permissão de edição
    pode_editar = request.user.nivel == 'administrador'
    
    return render(request, 'contratus/empreendimentos/empreendimento_detail.html', {
        'empreendimento': empreendimento,
        'unidades': unidades,  # ✅ ADICIONADO
        'pode_editar': pode_editar
    })


# =====================================================
# CLIENTES
# =====================================================

@login_required
def cliente_list(request):
    """Lista de clientes"""
    user = request.user
    
    if user.nivel == 'administrador':
        clientes = Cliente.objects.all()
    elif user.nivel == 'gerente':
        if user.equipe:
            corretores_equipe = user.equipe.membros.filter(nivel='corretor')
            clientes = Cliente.objects.filter(cadastrado_por__in=corretores_equipe)
        else:
            clientes = Cliente.objects.none()
    else:
        clientes = Cliente.objects.filter(corretor_cadastro=user)
    
    return render(request, 'contratus/clientes/list.html', {'clientes': clientes})


@login_required
def cliente_create(request):
    """Criar cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.cadastrado_por = request.user
            cliente.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('cliente_list')
    else:
        form = ClienteForm()
    
    return render(request, 'contratus/clientes/form.html', {'form': form, 'title': 'Novo Cliente'})


@login_required
def cliente_edit(request, pk):
    """Editar cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    # Verificar permissão
    if request.user.nivel == 'corretor' and cliente.cadastrado_por != request.user:
        messages.error(request, 'Você não tem permissão para editar este cliente.')
        return redirect('cliente_list')
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('cliente_list')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'contratus/clientes/form.html', {'form': form, 'title': 'Editar Cliente'})


# =====================================================
# PROPOSTAS
# =====================================================

@login_required
def proposta_list(request):
    user = request.user

    if user.nivel == 'administrador':
        propostas = Proposta.objects.all()
    elif user.nivel == 'gerente':
        if user.equipe:
            corretores_equipe = user.equipe.membros.filter(nivel='corretor')
            propostas = Proposta.objects.filter(corretor__in=corretores_equipe)
        else:
            propostas = Proposta.objects.none()
    else:
        propostas = Proposta.objects.filter(corretor=user)
    
    # Adiciona um atributo temporário para indicar se já tem contrato
    for proposta in propostas:
        proposta.tem_contrato = hasattr(proposta, 'contrato')

    return render(request, 'contratus/propostas/list.html', {'propostas': propostas})


@login_required
def proposta_create(request):
    """
    ✅ Cria nova proposta com cálculo automático de parcelas
    
    Lógica:
    1. Corretor preenche: valor_construtora e valor_parcela_cliente
    2. Sistema calcula: valor_com_juros (×1.5) e quantidade_parcelas
    3. Unidade automaticamente vai para status "reservada"
    4. Gera número da proposta automaticamente
    """
    
    if request.method == 'POST':
        form = PropostaForm(request.POST)
        
        if form.is_valid():
            proposta = form.save(commit=False)
            
            # ✅ Atribuir corretor logado
            proposta.corretor = request.user
            
            # ✅ Gerar número da proposta automaticamente
            ano_atual = timezone.now().year
            
            # Buscar última proposta do ano
            ultima_proposta = Proposta.objects.filter(
                numero_proposta__startswith=f'PROP-{ano_atual}'
            ).aggregate(Max('numero_proposta'))
            
            if ultima_proposta['numero_proposta__max']:
                # Extrair número sequencial
                ultimo_numero = int(ultima_proposta['numero_proposta__max'].split('-')[-1])
                novo_numero = ultimo_numero + 1
            else:
                novo_numero = 1
            
            proposta.numero_proposta = f'PROP-{ano_atual}-{novo_numero:04d}'
            
            # ✅ Salvar (o signal vai mudar status da unidade para "reservada")
            proposta.save()
            
            messages.success(
                request,
                f'Proposta {proposta.numero_proposta} criada com sucesso! '
                f'A unidade {proposta.unidade.numero} foi reservada.'
            )
            return redirect('proposta_detail', pk=proposta.pk)
        else:
            messages.error(request, 'Erro ao criar proposta. Verifique os campos.')
    else:
        form = PropostaForm()
    
    context = {
        'form': form,
        'title': 'Nova Proposta'
    }
    return render(request, 'contratus/propostas/form.html', context)


# ========================================
# ✅ PROPOSTA - EDIT
# ========================================
@login_required
def proposta_edit(request, pk):
    """Edita proposta existente"""
    proposta = get_object_or_404(Proposta, pk=pk)
    
    # ✅ Verificar permissão
    if request.user.nivel == 'corretor' and proposta.corretor != request.user:
        messages.error(request, 'Você não tem permissão para editar esta proposta.')
        return redirect('proposta_list')
    
    # ✅ Não permite editar proposta aprovada
    if proposta.status == 'aprovada' and proposta.contrato:
        messages.error(request, 'Proposta já possui contrato gerado. Não é possível editar.')
        return redirect('proposta_detail', pk=pk)
    
    if request.method == 'POST':
        form = PropostaForm(request.POST, instance=proposta)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Proposta atualizada com sucesso!')
            return redirect('proposta_detail', pk=proposta.pk)
        else:
            messages.error(request, 'Erro ao atualizar proposta.')
    else:
        form = PropostaForm(instance=proposta)
    
    context = {
        'form': form,
        'title': f'Editar Proposta {proposta.numero_proposta}',
        'proposta': proposta
    }
    return render(request, 'contratus/propostas/form.html', context)


# ========================================
# ✅ PROPOSTA - DETAIL
# ========================================
@login_required
def proposta_detail(request, pk):
    """Exibe detalhes da proposta"""
    proposta = get_object_or_404(Proposta, pk=pk)
    
    # ✅ Verificar permissão de acesso
    if request.user.nivel == 'corretor' and proposta.corretor != request.user:
        messages.error(request, 'Você não tem permissão para ver esta proposta.')
        return redirect('proposta_list')
    
    # ✅ Calcular informações adicionais
    valor_total = proposta.valor_com_juros
    valor_financiado = proposta.total_aprovacao
    saldo_parcelar = valor_total - valor_financiado - proposta.valor_entrada
    
    context = {
        'proposta': proposta,
        'valor_total': valor_total,
        'valor_financiado': valor_financiado,
        'saldo_parcelar': saldo_parcelar,
    }
    return render(request, 'contratus/propostas/detail.html', context)


# ========================================
# ✅ PROPOSTA - LIST
# ========================================
@login_required
def proposta_list(request):
    """Lista propostas com filtros"""
    propostas = Proposta.objects.select_related(
        'cliente', 'empreendimento', 'unidade', 'corretor'
    ).all()
    
    # ✅ Filtro por corretor (se for corretor, vê apenas suas propostas)
    if request.user.nivel == 'corretor':
        propostas = propostas.filter(corretor=request.user)
    
    # ✅ Filtros
    status = request.GET.get('status')
    empreendimento = request.GET.get('empreendimento')
    corretor = request.GET.get('corretor')
    busca = request.GET.get('busca')
    
    if status:
        propostas = propostas.filter(status=status)
    
    if empreendimento:
        propostas = propostas.filter(empreendimento_id=empreendimento)
    
    if corretor:
        propostas = propostas.filter(corretor_id=corretor)
    
    if busca:
        propostas = propostas.filter(
            Q(numero_proposta__icontains=busca) |
            Q(cliente__nome__icontains=busca) |
            Q(cliente__cpf__icontains=busca)
        )
    
    propostas = propostas.order_by('-data_criacao')
    
    context = {
        'propostas': propostas,
        'empreendimentos': Empreendimento.objects.all(),
        'corretores': User.objects.filter(nivel='corretor'),
    }
    return render(request, 'contratus/propostas/list.html', context)


# ========================================
# ✅ PROPOSTA - APROVAR
# ========================================
@login_required
def proposta_aprovar(request, pk):
    """Aprova proposta (apenas gerente e admin)"""
    if request.user.nivel not in ['gerente', 'administrador']:
        messages.error(request, 'Você não tem permissão para aprovar propostas.')
        return redirect('proposta_list')
    
    proposta = get_object_or_404(Proposta, pk=pk)
    
    if proposta.status != 'analise':
        messages.warning(request, 'Esta proposta não está em análise.')
        return redirect('proposta_detail', pk=pk)
    
    proposta.status = 'aprovada'
    proposta.save()
    
    messages.success(
        request,
        f'Proposta {proposta.numero_proposta} aprovada com sucesso! '
        'Agora você pode gerar o contrato.'
    )
    return redirect('proposta_detail', pk=pk)


# ========================================
# ✅ PROPOSTA - REPROVAR
# ========================================
@login_required
def proposta_reprovar(request, pk):
    """Reprova proposta (apenas gerente e admin)"""
    if request.user.nivel not in ['gerente', 'administrador']:
        messages.error(request, 'Você não tem permissão para reprovar propostas.')
        return redirect('proposta_list')
    
    proposta = get_object_or_404(Proposta, pk=pk)
    
    if proposta.status != 'analise':
        messages.warning(request, 'Esta proposta não está em análise.')
        return redirect('proposta_detail', pk=pk)
    
    proposta.status = 'reprovada'
    proposta.save()
    
    # ✅ Liberar unidade novamente
    unidade = proposta.unidade
    unidade.status = 'disponivel'
    unidade.save()
    
    messages.success(
        request,
        f'Proposta {proposta.numero_proposta} reprovada. '
        f'A unidade {unidade.numero} voltou para status disponível.'
    )
    return redirect('proposta_detail', pk=pk)


# ========================================
# ✅ PROPOSTA - DELETE
# ========================================
@login_required
def proposta_delete(request, pk):
    """Cancela/deleta proposta"""
    proposta = get_object_or_404(Proposta, pk=pk)
    
    # ✅ Verificar permissão
    if request.user.nivel == 'corretor' and proposta.corretor != request.user:
        messages.error(request, 'Você não tem permissão para cancelar esta proposta.')
        return redirect('proposta_list')
    
    # ✅ Não permite deletar se já tem contrato
    if hasattr(proposta, 'contrato'):
        messages.error(request, 'Não é possível cancelar proposta com contrato gerado.')
        return redirect('proposta_detail', pk=pk)
    
    if request.method == 'POST':
        # ✅ Liberar unidade
        unidade = proposta.unidade
        unidade.status = 'disponivel'
        unidade.save()
        
        numero = proposta.numero_proposta
        proposta.delete()
        
        messages.success(
            request,
            f'Proposta {numero} cancelada com sucesso. '
            f'A unidade {unidade.numero} voltou para status disponível.'
        )
        return redirect('proposta_list')
    
    context = {'proposta': proposta}
    return render(request, 'contratus/propostas/delete.html', context)

@login_required
def proposta_gerar_pdf(request, pk):
    from weasyprint import HTML, CSS
    """Gerar PDF da proposta - 100% fiel ao modelo fornecido"""
    proposta = get_object_or_404(Proposta, pk=pk)
    
    # Verificar permissão
    user = request.user
    if user.nivel == 'corretor' and proposta.corretor != user:
        messages.error(request, 'Você não tem permissão.')
        return redirect('proposta_list')
    
    config = ConfiguracaoSistema.load()

    if not config:
        raise Exception("Nenhuma configuração cadastrada. Cadastre em /admin.")
    
    context = {
        'proposta': proposta,
        'config': config,
        'data_hoje': timezone.now().strftime('%d/%m/%Y')
    }
    
    # Renderizar template HTML
    html_string = render_to_string('contratus/propostas/proposta_pdf.html', context)
    
    # Gerar PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    # Retornar como response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Proposta_{proposta.numero_proposta}.pdf"'
    
    return response





# =====================================================
# CONTRATOS
# =====================================================
@login_required
def contrato_list(request):
    """Lista de contratos com controle de acesso"""
    user = request.user

    if user.nivel == 'administrador':
        contratos = Contrato.objects.all()

    elif user.nivel == 'gerente':
        if user.equipe:
            corretores_equipe = user.equipe.membros.filter(nivel='corretor')
            contratos = Contrato.objects.filter(proposta__corretor__in=corretores_equipe)
        else:
            contratos = Contrato.objects.none()

    else:  # corretor
        contratos = Contrato.objects.filter(proposta__corretor=user)

    return render(request, 'contratus/contratos/list.html', {
        'contratos': contratos
    })


@login_required
def contrato_create_from_proposta(request, proposta_pk):
    """
    Cria um contrato a partir de uma proposta existente.
    Preenche automaticamente todos os campos financeiros e relacionamentos.
    """
    # Busca a proposta
    proposta = get_object_or_404(Proposta, pk=proposta_pk)

    # Se já existe contrato para essa proposta, apenas redireciona
    if hasattr(proposta, 'contrato'):
        contrato = proposta.contrato
        return redirect('contrato_detail', pk=contrato.id)

    # Criação do contrato
    contrato = Contrato(
        proposta=proposta,
        empreendimento=proposta.empreendimento,
        unidade=proposta.unidade,
        cliente=proposta.cliente,
        corretor=proposta.corretor,
        numero_contrato=f"CT-{proposta.numero_proposta}",
        criado_por=request.user,
        valor_imovel=proposta.valor_com_juros,
        valor_parcelamento=proposta.valor_com_juros,
        numero_parcelas=proposta.quantidade_parcelas,
        valor_parcela=proposta.valor_parcela_cliente,
        valor_financiamento=proposta.valor_financiamento,
        valor_subsidio=proposta.valor_subsidio,
        valor_fgts=proposta.valor_fgts,
        valor_entrada=proposta.valor_entrada,
    )

    # Define data de vencimento da primeira parcela como hoje + validade do contrato, se houver
    if not contrato.data_assinatura:
        contrato.data_assinatura = date.today()
    contrato.calcular_vencimento_primeira_parcela()

    # Salva o contrato
    contrato.save()

    # Redireciona para a página de detalhe do contrato
    return redirect('contrato_detail', pk=contrato.id)


@login_required
def contrato_detail(request, pk):
    """Detalhes do contrato"""
    contrato = get_object_or_404(Contrato, pk=pk)
    
    # Verificar permissão
    user = request.user
    if user.nivel == 'corretor' and contrato.corretor != user:
        messages.error(request, 'Você não tem permissão para visualizar este contrato.')
        return redirect('contrato_list')
    elif user.nivel == 'gerente':
        if not user.equipe or contrato.corretor not in user.equipe.membros.all():
            messages.error(request, 'Você não tem permissão para visualizar este contrato.')
            return redirect('contrato_list')
    
    historico = contrato.historico.all()[:10]
    
    return render(request, 'contratus/contratos/detail.html', {
        'contrato': contrato,
        'historico': historico
    })


@login_required
def contrato_gerar_pdf(request, pk):
    from weasyprint import HTML, CSS
    """Gerar PDF do contrato - 100% fiel ao modelo fornecido"""
    contrato = get_object_or_404(Contrato, pk=pk)
    
    # Verificar permissão
    user = request.user
    if user.nivel == 'corretor' and contrato.corretor != user:
        messages.error(request, 'Você não tem permissão.')
        return redirect('contrato_list')
    
    config = ConfiguracaoSistema.load()
    
    # Converter valor para extenso
    valor_extenso = contrato.get_valor_total_extenso()
    
    context = {
        'contrato': contrato,
        'config': config,
        'valor_extenso': valor_extenso,
        'data_hoje': timezone.now().strftime('%d de %B de %Y').upper()
    }
    
    # Renderizar template HTML
    html_string = render_to_string('contratus/contratos/contrato_pdf.html', context)
    
    # Gerar PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    # Retornar como response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Contrato_{contrato.numero_contrato}.pdf"'
    
    return response


@login_required
def contrato_alterar_status(request, pk):
    """Alterar status do contrato"""
    contrato = get_object_or_404(Contrato, pk=pk)
    
    # Verificar permissão
    if request.user.nivel == 'corretor' and contrato.corretor != request.user:
        messages.error(request, 'Você não tem permissão.')
        return redirect('contrato_list')
    
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        observacao = request.POST.get('observacao', '')
        
        if novo_status in dict(Contrato.STATUS_CHOICES):
            status_anterior = contrato.status
            contrato.status = novo_status
            contrato.save()
            
            # Registrar no histórico
            HistoricoContrato.objects.create(
                contrato=contrato,
                usuario=request.user,
                status_anterior=status_anterior,
                status_novo=novo_status,
                observacao=observacao
            )
            
            messages.success(request, f'Status alterado para: {contrato.get_status_display()}')
        else:
            messages.error(request, 'Status inválido.')
    
    return redirect('contrato_detail', pk=pk)


# =====================================================
# API - AJAX
# =====================================================

@login_required
def api_empreendimento_info(request, pk):
    """API para retornar informações do empreendimento"""

    empreendimento = get_object_or_404(Empreendimento, pk=pk)

    data = {
        'id': empreendimento.id,
        'nome': empreendimento.nome,
        'endereco': empreendimento.get_endereco_completo(),
        'descricao': empreendimento.descricao_completa,

        'construtora': {
            'razao_social': empreendimento.construtora.razao_social,
            'cnpj': empreendimento.construtora.cnpj,
            'endereco': empreendimento.construtora.get_endereco_completo(),
        },

        # Tipos de unidade (modelo correto para valor base)
        'tipos_unidade': [
            {
                'id': tipo.id,
                'nome': tipo.nome,
                'valor_imovel': str(tipo.valor_imovel),
                'valor_engenharia_necessaria': str(tipo.valor_engenharia_necessaria or 0),
            }
            for tipo in empreendimento.tipos_unidade.filter(ativo=True)
        ],

        # Unidades disponíveis
        'unidades': [
            {
                'id': unidade.id,
                'identificacao': unidade.identificacao,
                'status': unidade.status,
                'status_display': unidade.get_status_display(),
                'tipo_unidade_id': unidade.tipo_unidade.id if unidade.tipo_unidade else None,
                'tipo_unidade_nome': unidade.tipo_unidade.nome if unidade.tipo_unidade else None,
                'valor_imovel': str(unidade.get_valor_imovel()),
            }
            for unidade in empreendimento.unidades.filter(status='disponivel')
        ]
    }

    return JsonResponse(data)

@login_required
def api_tipos_unidade(request, empreendimento_pk):
    """
    ✅ CORRIGIDO: API para retornar tipos de unidade
    """
    empreendimento = get_object_or_404(Empreendimento, pk=empreendimento_pk)
    
    tipos = empreendimento.tipos_unidade.filter(ativo=True).order_by('nome')
    
    data = []
    for tipo in tipos:
        # ✅ CONSTRUIR DESCRIÇÃO MANUALMENTE
        desc_parts = []
        if tipo.quartos:
            desc_parts.append(f"{tipo.quartos} quarto(s)")
        if tipo.banheiros:
            desc_parts.append(f"{tipo.banheiros} banheiro(s)")
        if tipo.vagas_garagem:
            desc_parts.append(f"{tipo.vagas_garagem} vaga(s)")
        if tipo.area_util:
            desc_parts.append(f"{tipo.area_util}m²")
        
        descricao = " | ".join(desc_parts) if desc_parts else "Sem detalhes"
        
        data.append({
            'id': tipo.id,
            'nome': tipo.nome,
            'descricao': descricao,  # ✅ CORRIGIDO
            'quartos': tipo.quartos,
            'banheiros': tipo.banheiros,
            'vagas_garagem': tipo.vagas_garagem,
            'area_util': float(tipo.area_util),
            'valor_imovel': float(tipo.valor_imovel),
            'valor_engenharia': float(tipo.valor_engenharia_necessaria or 0),
        })
    
    return JsonResponse(data, safe=False)


@login_required
def api_cliente_info(request, pk):
    """API para retornar informações do cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    data = {
        'nome_completo': cliente.nome_completo,
        'cpf': cliente.cpf,
        'endereco': cliente.get_endereco_completo(),
        'telefone': cliente.telefone,
        'email': cliente.email,
        'origem': cliente.get_origem_display()
    }
    
    return JsonResponse(data)


@login_required
def tipo_unidade_list(request, empreendimento_pk):
    """Lista de tipos de unidade de um empreendimento"""
    empreendimento = get_object_or_404(Empreendimento, pk=empreendimento_pk)
    tipos = empreendimento.tipos_unidade.all()
    
    # Verificar permissão de edição
    pode_editar = request.user.nivel == 'administrador'
    
    return render(request, 'contratus/tipo_unidades/tipo_unidade_list.html', {  # ✅ CORRIGIDO
        'empreendimento': empreendimento,
        'tipos': tipos,
        'pode_editar': pode_editar
    })




@login_required
def tipo_unidade_create(request, empreendimento_pk):
    """Criar tipo de unidade - apenas administrador"""
    if request.user.nivel != 'administrador':
        messages.error(request, 'Acesso negado. Apenas administradores podem criar tipos de unidade.')
        return redirect('empreendimento_detail', pk=empreendimento_pk)
    
    empreendimento = get_object_or_404(Empreendimento, pk=empreendimento_pk)
    
    if request.method == 'POST':
        form = TipoUnidadeForm(request.POST, request.FILES, empreendimento_id=empreendimento_pk)
        
        # ✅ DEBUG: Imprimir erros
        if not form.is_valid():
            print("❌ ERROS DO FORMULÁRIO:")
            print(form.errors)
            print("📦 DADOS RECEBIDOS:")
            print(request.POST)
        
        if form.is_valid():
            tipo = form.save()
            messages.success(request, f'Tipo "{tipo.nome}" criado com sucesso!')
            return redirect('tipo_unidade_list', empreendimento_pk=empreendimento_pk)
    else:
        form = TipoUnidadeForm(empreendimento_id=empreendimento_pk)
    
    return render(request, 'contratus/tipo_unidades/tipo_unidade_form.html', {  # ✅ CORRIGIDO
        'form': form,
        'title': f'Novo Tipo de Unidade - {empreendimento.nome}',
        'empreendimento': empreendimento
    })


@login_required
def tipo_unidade_edit(request, pk):
    """Editar tipo de unidade - apenas administrador"""
    if request.user.nivel != 'administrador':
        messages.error(request, 'Acesso negado.')
        return redirect('empreendimento_list')
    
    tipo = get_object_or_404(TipoUnidade, pk=pk)
    
    if request.method == 'POST':
        form = TipoUnidadeForm(request.POST, request.FILES, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo atualizado com sucesso!')
            return redirect('tipo_unidade_list', empreendimento_pk=tipo.empreendimento.pk)
    else:
        form = TipoUnidadeForm(instance=tipo)
    
    return render(request, 'contratus/tipo_unidades/tipo_unidade_form.html', {  # ✅ CORRIGIDO
        'form': form,
        'title': f'Editar Tipo: {tipo.nome}',
        'empreendimento': tipo.empreendimento
    })

@login_required
def tipo_unidade_delete(request, pk):
    """Excluir tipo de unidade - apenas administrador"""
    if request.user.nivel != 'administrador':
        messages.error(request, 'Acesso negado.')
        return redirect('empreendimento_list')
    
    tipo = get_object_or_404(TipoUnidade, pk=pk)
    empreendimento_pk = tipo.empreendimento.pk
    
    # Verificar se há unidades usando este tipo
    if tipo.unidades.exists():
        messages.error(
            request,
            f'Não é possível excluir este tipo pois há {tipo.unidades.count()} unidade(s) associada(s).'
        )
    else:
        nome = tipo.nome
        tipo.delete()
        messages.success(request, f'Tipo "{nome}" excluído com sucesso!')
    
    return redirect('tipo_unidade_list', empreendimento_pk=empreendimento_pk)

@login_required
def unidade_create(request, empreendimento_pk):
    """Criar unidade - apenas administrador"""
    if request.user.nivel != 'administrador':
        messages.error(request, 'Acesso negado. Apenas administradores podem criar unidades.')
        return redirect('empreendimento_detail', pk=empreendimento_pk)
    
    empreendimento = get_object_or_404(Empreendimento, pk=empreendimento_pk)
    
    if request.method == 'POST':
        # Passa o empreendimento_id para o form
        form = UnidadeForm(request.POST, empreendimento_id=empreendimento_pk)
        if form.is_valid():
            # Agora salva diretamente, o empreendimento já está definido pelo form
            unidade = form.save()
            messages.success(request, f'Unidade "{unidade.numero}" criada com sucesso!')
            return redirect('empreendimento_detail', pk=empreendimento_pk)
        else:
            # Para debug, exibe os erros do form
            messages.error(request, f'Erro ao salvar: {form.errors}')
    else:
        # Form vazio, mas com empreendimento já definido
        form = UnidadeForm(empreendimento_id=empreendimento_pk)
    
    return render(request, 'contratus/unidades/unidade_form.html', {
        'form': form,
        'title': f'Nova Unidade - {empreendimento.nome}',
        'empreendimento': empreendimento
    })


@login_required
def unidade_edit(request, pk):
    """Editar unidade - apenas administrador"""
    if request.user.nivel != 'administrador':
        messages.error(request, 'Acesso negado.')
        return redirect('empreendimento_list')
    
    unidade = get_object_or_404(UnidadeEmpreendimento, pk=pk)
    
    if request.method == 'POST':
        form = UnidadeForm(request.POST, instance=unidade)
        if form.is_valid():
            form.save()
            messages.success(request, f'Unidade "{unidade.numero}" atualizada com sucesso!')  # ✅ CORRIGIDO
            return redirect('empreendimento_detail', pk=unidade.empreendimento.pk)
    else:
        form = UnidadeForm(instance=unidade)
    
    return render(request, 'contratus/unidades/unidade_form.html', {
        'form': form,
        'title': f'Editar Unidade: {unidade.numero}',  # ✅ CORRIGIDO
        'empreendimento': unidade.empreendimento
    })

@login_required
def unidades_em_lote_create(request, empreendimento_pk):
    """✅ CORRIGIDO: Criar múltiplas unidades"""
    if request.user.nivel != 'administrador':
        messages.error(request, 'Acesso negado.')
        return redirect('empreendimento_detail', pk=empreendimento_pk)
    
    empreendimento = get_object_or_404(Empreendimento, pk=empreendimento_pk)
    
    if request.method == 'POST':
        form = UnidadesEmLoteForm(request.POST, empreendimento_id=empreendimento_pk)
        
        if form.is_valid():
            # ✅ OBTER DADOS DO FORMULÁRIO
            tipo = form.cleaned_data.get('tipo')
            prefixo = form.cleaned_data.get('prefixo', '')
            numero_inicial = form.cleaned_data['numero_inicial']
            numero_final = form.cleaned_data['numero_final']
            bloco = form.cleaned_data.get('bloco', '')
            andar = form.cleaned_data.get('andar', '')
            area_privativa = form.cleaned_data['area_privativa']
            quartos = form.cleaned_data['quartos']
            suites = form.cleaned_data['suites']
            banheiros = form.cleaned_data['banheiros']
            vagas_garagem = form.cleaned_data['vagas_garagem']
            valor_imovel = form.cleaned_data['valor_imovel']
            valor_engenharia = form.cleaned_data['valor_engenharia']
            
            # ✅ VALIDAR QUANTIDADE
            quantidade = numero_final - numero_inicial + 1
            if quantidade > 100:
                messages.error(request, 'Máximo de 100 unidades por vez.')
                return redirect('empreendimento_detail', pk=empreendimento_pk)
            
            # ✅ CRIAR UNIDADES
            unidades_criadas = []
            unidades_duplicadas = []
            
            for numero in range(numero_inicial, numero_final + 1):
                # Gerar identificação
                if prefixo:
                    identificacao = f"{prefixo} {numero:02d}"
                else:
                    identificacao = f"{numero:02d}"
                
                # Verificar duplicata
                if UnidadeEmpreendimento.objects.filter(
                    empreendimento=empreendimento,
                    numero=identificacao
                ).exists():
                    unidades_duplicadas.append(identificacao)
                    continue
                
                # ✅ CRIAR UNIDADE COM TODOS OS CAMPOS
                UnidadeEmpreendimento.objects.create(
                    empreendimento=empreendimento,
                    tipo=tipo,
                    numero=identificacao,
                    bloco=bloco,
                    andar=andar,
                    area_privativa=area_privativa,
                    quartos=quartos,
                    suites=suites,
                    banheiros=banheiros,
                    vagas_garagem=vagas_garagem,
                    valor_imovel=valor_imovel,
                    valor_engenharia=valor_engenharia,
                    status='disponivel'
                )
                unidades_criadas.append(identificacao)
            
            # ✅ MENSAGENS DE FEEDBACK
            if unidades_criadas:
                messages.success(
                    request,
                    f'✅ {len(unidades_criadas)} unidade(s) criada(s) com sucesso!'
                )
            
            if unidades_duplicadas:
                messages.warning(
                    request,
                    f'⚠️ {len(unidades_duplicadas)} unidade(s) já existem: '
                    f'{", ".join(unidades_duplicadas[:5])}'
                    f'{"..." if len(unidades_duplicadas) > 5 else ""}'
                )
            
            return redirect('empreendimento_detail', pk=empreendimento_pk)
        else:
            # ✅ EXIBIR ERROS DO FORMULÁRIO
            messages.error(request, f'Erro no formulário: {form.errors}')
    else:
        form = UnidadesEmLoteForm(empreendimento_id=empreendimento_pk)
    
    return render(request, 'contratus/unidades/unidade_form_lote.html', {
        'form': form,
        'title': f'Criar Unidades em Lote - {empreendimento.nome}',
        'empreendimento': empreendimento
    })

    """Criar múltiplas unidades de uma vez - apenas administrador"""
    if request.user.nivel != 'administrador':
        messages.error(request, 'Acesso negado.')
        return redirect('empreendimento_detail', pk=empreendimento_pk)
    
    empreendimento = get_object_or_404(Empreendimento, pk=empreendimento_pk)
    
    if request.method == 'POST':
        # ✅ PASSAR empreendimento_id NO POST TAMBÉM
        form = UnidadesEmLoteForm(request.POST, empreendimento_id=empreendimento_pk)
        
        if form.is_valid():
            prefixo = form.cleaned_data.get('prefixo', '')
            numero_inicial = form.cleaned_data['numero_inicial']
            numero_final = form.cleaned_data['numero_final']
            tipo_unidade = form.cleaned_data.get('tipo_unidade')
            andar = form.cleaned_data.get('andar', '')
            bloco = form.cleaned_data.get('bloco', '')
            
            # Criar unidades
            unidades_criadas = []
            unidades_duplicadas = []
            
            for numero in range(numero_inicial, numero_final + 1):
                if prefixo:
                    identificacao = f"{prefixo} {numero:02d}"
                else:
                    identificacao = f"{numero:02d}"
                
                # Verificar se já existe
                if UnidadeEmpreendimento.objects.filter(
                    empreendimento=empreendimento,
                    identificacao=identificacao
                ).exists():
                    unidades_duplicadas.append(identificacao)
                    continue
                
                # Criar unidade
                UnidadeEmpreendimento.objects.create(
                    empreendimento=empreendimento,
                    tipo_unidade=tipo_unidade,
                    identificacao=identificacao,
                    andar=andar,
                    bloco=bloco,
                    status='disponivel'
                )
                unidades_criadas.append(identificacao)
            
            # Mensagens
            if unidades_criadas:
                messages.success(
                    request,
                    f'✅ {len(unidades_criadas)} unidade(s) criada(s) com sucesso!'
                )
            
            if unidades_duplicadas:
                messages.warning(
                    request,
                    f'⚠️ {len(unidades_duplicadas)} unidade(s) não criada(s) por já existirem: '
                    f'{", ".join(unidades_duplicadas[:5])}'
                    f'{"..." if len(unidades_duplicadas) > 5 else ""}'
                )
            
            return redirect('empreendimento_detail', pk=empreendimento_pk)
    else:
        # ✅ PASSAR empreendimento_id NO GET
        form = UnidadesEmLoteForm(empreendimento_id=empreendimento_pk)
    
    return render(request, 'contratus/unidades/unidade_form_lote.html', {
        'form': form,
        'title': f'Criar Unidades em Lote - {empreendimento.nome}',
        'empreendimento': empreendimento
    })

@login_required
def unidade_delete(request, pk):
    """Excluir unidade - apenas administrador"""
    if request.user.nivel != 'administrador':
        messages.error(request, 'Acesso negado.')
        return redirect('empreendimento_list')
    
    unidade = get_object_or_404(UnidadeEmpreendimento, pk=pk)
    empreendimento_pk = unidade.empreendimento.pk
    
    # Verificar se a unidade já foi usada em propostas/contratos
    if unidade.propostas.exists() or unidade.contratos.exists():
        messages.error(
            request,
            'Não é possível excluir esta unidade pois já foi usada em propostas ou contratos.'
        )
    else:
        numero = unidade.numero  # ✅ CORRIGIDO
        unidade.delete()
        messages.success(request, f'Unidade "{numero}" excluída com sucesso!')  # ✅ CORRIGIDO
    
    return redirect('empreendimento_detail', pk=empreendimento_pk)

@login_required
def ajax_unidades_disponiveis(request):
    """
    ✅ Retorna unidades disponíveis de um empreendimento (para AJAX)
    
    Usado no formulário de proposta para filtrar unidades dinamicamente
    """
    empreendimento_id = request.GET.get('empreendimento')
    
    if not empreendimento_id:
        return JsonResponse({'unidades': []})
    
    try:
        # Buscar unidades disponíveis do empreendimento
        unidades = UnidadeEmpreendimento.objects.filter(
            empreendimento_id=empreendimento_id,
            status='disponivel'
        ).select_related('tipo', 'empreendimento').order_by('numero')
        
        # Formatar para JSON
        unidades_data = []
        for unidade in unidades:
            # Montar texto descritivo
            tipo_nome = unidade.tipo.nome if unidade.tipo else 'Sem tipo'
            valor_formatado = f"R$ {unidade.valor_imovel:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            # Informações adicionais
            info_adicional = f"{unidade.quartos}Q"
            if unidade.suites > 0:
                info_adicional += f" ({unidade.suites}S)"
            info_adicional += f", {unidade.banheiros}B"
            if unidade.vagas_garagem > 0:
                info_adicional += f", {unidade.vagas_garagem}V"
            info_adicional += f" - {unidade.area_privativa}m²"
            
            # Texto completo
            texto = f"Unidade {unidade.numero}"
            if unidade.bloco:
                texto += f" - Bloco {unidade.bloco}"
            if unidade.andar:
                texto += f" - {unidade.andar}º andar"
            texto += f" | {tipo_nome} | {info_adicional} | {valor_formatado}"
            
            unidades_data.append({
                'id': unidade.id,
                'text': texto
            })
        
        return JsonResponse({'unidades': unidades_data})
    
    except Exception as e:
        # Logar erro para debug
        import traceback
        print(f"Erro em ajax_unidades_disponiveis: {str(e)}")
        print(traceback.format_exc())
        
        return JsonResponse({
            'error': str(e),
            'unidades': []
        }, status=400)




@login_required
def get_tipo_unidade_data(request, tipo_id):
    """
    API para buscar dados de um tipo de unidade
    Usado para auto-preencher formulários
    """
    try:
        tipo = TipoUnidade.objects.get(pk=tipo_id)
        data = {
            'success': True,
            'data': {
                'nome': tipo.nome,
                'quartos': tipo.quartos,
                'banheiros': tipo.banheiros,
                'vagas_garagem': tipo.vagas_garagem,
                'area_util': float(tipo.area_util),
                'valor_imovel': float(tipo.valor_imovel),
                'valor_engenharia_necessaria': float(tipo.valor_engenharia_necessaria or 0),
            }
        }
        return JsonResponse(data)
    except TipoUnidade.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Tipo de unidade não encontrado'
        }, status=404)