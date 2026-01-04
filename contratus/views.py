from django.db.models.functions import TruncMonth, TruncWeek
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Sum, Avg
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import io

from num2words import num2words

from .models import (
    User, Equipe, Construtora, Empreendimento, UnidadeEmpreendimento,
    Cliente, Proposta, Contrato, HistoricoContrato, Comissao, Configuracao, TipoUnidade
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
                if user.ativo:
                    login(request, user)
                    messages.success(request, f'Bem-vindo, {user.get_full_name()}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Usuário inativo. Contate o administrador.')
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
        contratos_query = Contrato.objects.all()
        propostas_query = Proposta.objects.all()
        usuarios_query = User.objects.filter(ativo=True)
        equipes_disponiveis = Equipe.objects.filter(ativa=True)
        pode_ver_todas_equipes = True
        
    elif user.nivel == 'gerente':
        # GERENTE vê apenas sua equipe
        if user.equipe:
            corretores_equipe = user.equipe.membros.filter(nivel='corretor', ativo=True)
            contratos_query = Contrato.objects.filter(corretor__in=corretores_equipe)
            propostas_query = Proposta.objects.filter(corretor__in=corretores_equipe)
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
        contratos_query = Contrato.objects.filter(corretor=user)
        propostas_query = Proposta.objects.filter(corretor=user)
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
            contratos_query = contratos_query.filter(corretor__in=corretores_equipe)
            propostas_query = propostas_query.filter(corretor__in=corretores_equipe)
        except:
            pass
    
    # Filtro de corretor (admin e gerente)
    if corretor_filtro != 'todos' and user.nivel in ['administrador', 'gerente']:
        contratos_query = contratos_query.filter(corretor_id=int(corretor_filtro))
        propostas_query = propostas_query.filter(corretor_id=int(corretor_filtro))
    
    # Filtro de empreendimento
    if empreendimento_filtro != 'todos':
        contratos_query = contratos_query.filter(empreendimento_id=int(empreendimento_filtro))
        propostas_query = propostas_query.filter(empreendimento_id=int(empreendimento_filtro))
    
    # ============================================
    # ESTATÍSTICAS GERAIS (CARDS)
    # ============================================
    
    total_contratos = contratos_query.count()
    total_propostas = propostas_query.count()
    
    contratos_ativos = contratos_query.filter(status__in=['ativo', 'em_andamento', 'assinado']).count()
    contratos_finalizados = contratos_query.filter(status='finalizado').count()
    contratos_cancelados = contratos_query.filter(status__in=['cancelado', 'distratado']).count()
    
    propostas_pendentes = propostas_query.filter(status='enviada').count()
    propostas_aprovadas = propostas_query.filter(status='aprovada').count()
    propostas_recusadas = propostas_query.filter(status='recusada').count()
    
    # Valores financeiros
    valor_total_contratos = contratos_query.aggregate(
        total=Sum('valor_imovel')
    )['total'] or Decimal('0')
    
    valor_total_comissoes = contratos_query.filter(
        status__in=['ativo', 'finalizado']
    ).aggregate(
        total=Sum('valor_imovel')
    )['total'] or Decimal('0')
    
    # Calcular comissão estimada (5% padrão)
    config = Configuracao.load()
    comissao_estimada = (valor_total_comissoes * config.taxa_corretagem_padrao) / 100
    
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
        valor=Sum('valor_imovel')
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
        ranking_corretores = usuarios_query.annotate(
            total_contratos=Count('contratos_criados', filter=Q(contratos_criados__in=contratos_query)),
            total_propostas=Count('propostas_criadas', filter=Q(propostas_criadas__in=propostas_query)),
            valor_total=Sum('contratos_criados__valor_imovel', filter=Q(contratos_criados__in=contratos_query))
        ).order_by('-total_contratos')[:10]
    else:
        ranking_corretores = None
    
    # ============================================
    # EMPREENDIMENTOS MAIS VENDIDOS
    # ============================================
    
    empreendimentos_top = contratos_query.values(
        'empreendimento__nome'
    ).annotate(
        total=Count('id'),
        valor_total=Sum('valor_imovel')
    ).order_by('-total')[:5]
    
    # ============================================
    # CONTRATOS RECENTES
    # ============================================
    
    contratos_recentes = contratos_query.select_related(
        'cliente', 'corretor', 'empreendimento', 'unidade'
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
                corretor__in=corretores_equipe,
                data_criacao__date__range=[data_inicio_anterior, data_fim_anterior]
            ).count()
        else:
            contratos_anterior = Contrato.objects.filter(
                corretor=user,
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
        'empreendimentos_disponiveis': Empreendimento.objects.filter(ativo=True),
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
    unidades = empreendimento.unidades.select_related('tipo_unidade').all()
    
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
        clientes = Cliente.objects.filter(cadastrado_por=user)
    
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
    """Criar proposta"""
    if request.method == 'POST':
        form = PropostaForm(request.POST, user=request.user)
        if form.is_valid():
            proposta = form.save(commit=False)
            proposta.corretor = request.user
            proposta.save()
            messages.success(request, f'Proposta {proposta.numero_proposta} criada com sucesso!')
            return redirect('proposta_detail', pk=proposta.pk)
    else:
        form = PropostaForm(user=request.user)
    
    return render(request, 'contratus/propostas/form.html', {'form': form, 'title': 'Nova Proposta'})


@login_required
def proposta_detail(request, pk):
    """Detalhes da proposta"""
    proposta = get_object_or_404(Proposta, pk=pk)
    
    # Verificar permissão
    user = request.user
    if user.nivel == 'corretor' and proposta.corretor != user:
        messages.error(request, 'Você não tem permissão para visualizar esta proposta.')
        return redirect('proposta_list')
    elif user.nivel == 'gerente':
        if not user.equipe or proposta.corretor not in user.equipe.membros.all():
            messages.error(request, 'Você não tem permissão para visualizar esta proposta.')
            return redirect('proposta_list')
    
    return render(request, 'contratus/propostas/detail.html', {'proposta': proposta})


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
    
    config = Configuracao.load()
    
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


@login_required
def proposta_aprovar(request, pk):
    """Aprovar uma proposta"""
    proposta = get_object_or_404(Proposta, pk=pk)

    # Permissões: apenas administrador, gerente ou corretor dono da proposta
    user = request.user
    if user.nivel == 'corretor' and proposta.corretor != user:
        messages.error(request, 'Você não tem permissão para aprovar esta proposta.')
        return redirect('proposta_list')
    elif user.nivel == 'gerente':
        if not user.equipe or proposta.corretor not in user.equipe.membros.all():
            messages.error(request, 'Você não tem permissão para aprovar esta proposta.')
            return redirect('proposta_list')

    if request.method == 'POST':
        proposta.status = 'aprovada'
        proposta.save()
        messages.success(request, f'Proposta {proposta.numero_proposta} aprovada com sucesso!')
    
    return redirect('proposta_list')



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
            contratos = Contrato.objects.filter(corretor__in=corretores_equipe)
        else:
            contratos = Contrato.objects.none()
    else:
        contratos = Contrato.objects.filter(corretor=user)
    
    return render(request, 'contratus/contratos/list.html', {'contratos': contratos})


@login_required
def contrato_create_from_proposta(request, proposta_pk):
    """
    ✅ VERSÃO ATUALIZADA: Criar contrato a partir de uma proposta aprovada
    
    FUNCIONAMENTO:
    1. Busca a proposta aprovada
    2. Pré-preenche AUTOMATICAMENTE todos os dados do contrato
    3. Corretor preenche apenas:
       - Data de assinatura (obrigatório)
       - Testemunhas (opcional)
       - Observações (opcional)
    4. Salva o contrato e atualiza o status da unidade
    """
    
    
    proposta = get_object_or_404(Proposta, pk=proposta_pk)
    
    # ========================================
    # VALIDAÇÕES
    # ========================================
    
    # Verificar se proposta está aprovada
    if proposta.status != 'aprovada':
        messages.error(request, 'Apenas propostas aprovadas podem gerar contratos.')
        return redirect('proposta_detail', pk=proposta_pk)
    
    # Verificar se já existe contrato
    if hasattr(proposta, 'contrato'):
        messages.warning(request, 'Esta proposta já possui um contrato.')
        return redirect('contrato_detail', pk=proposta.contrato.pk)
    
    # Verificar permissão
    user = request.user
    if user.nivel == 'corretor' and proposta.corretor != user:
        messages.error(request, 'Você não tem permissão para criar contrato desta proposta.')
        return redirect('proposta_list')
    elif user.nivel == 'gerente':
        if not user.equipe or proposta.corretor not in user.equipe.membros.all():
            messages.error(request, 'Você não tem permissão para criar contrato desta proposta.')
            return redirect('proposta_list')
    
    # ========================================
    # PROCESSAMENTO DO FORMULÁRIO
    # ========================================
    
    if request.method == 'POST':
        form = ContratoForm(request.POST)
        
        if form.is_valid():
            contrato = form.save(commit=False)
            
            # ✅ COPIAR AUTOMATICAMENTE TODOS OS DADOS DA PROPOSTA
            contrato.proposta = proposta
            contrato.empreendimento = proposta.empreendimento
            contrato.unidade = proposta.unidade
            contrato.cliente = proposta.cliente
            contrato.corretor = proposta.corretor
            
            # ✅ COPIAR VALORES FINANCEIROS
            contrato.valor_imovel = proposta.valor_imovel
            contrato.valor_financiamento = proposta.valor_financiamento
            contrato.valor_subsidio = proposta.valor_subsidio
            contrato.valor_fgts = proposta.valor_fgts
            contrato.valor_entrada = proposta.valor_entrada
            contrato.valor_parcelamento = proposta.valor_parcelamento_sem_juros
            contrato.numero_parcelas = proposta.numero_parcelas
            contrato.valor_parcela = proposta.valor_parcela
            
            # ✅ CALCULAR DATA DE VENCIMENTO AUTOMATICAMENTE
            config = Configuracao.load()
            contrato.validade_dias = config.validade_contrato_padrao
            contrato.prorrogacao_dias = config.prorrogacao_contrato_padrao
            
            if contrato.data_assinatura:
                contrato.data_vencimento = contrato.data_assinatura + timedelta(days=contrato.validade_dias)
            
            # ✅ DEFINIR STATUS INICIAL
            contrato.status = 'ativo'
            
            # Salvar contrato
            contrato.save()
            
            # ✅ ATUALIZAR STATUS DA UNIDADE
            contrato.unidade.status = 'vendida'
            contrato.unidade.save()
            
            messages.success(
                request,
                f'✅ Contrato {contrato.numero_contrato} criado com sucesso! '
                f'Todos os dados foram importados da proposta {proposta.numero_proposta}.'
            )
            
            return redirect('contrato_detail', pk=contrato.pk)
    
    else:
        # ========================================
        # FORMULÁRIO INICIAL (GET)
        # ========================================
        
        # Pré-preencher data de assinatura com hoje
        initial = {
            'data_assinatura': timezone.now().date(),
        }
        form = ContratoForm(initial=initial)
    
    # ========================================
    # CONTEXTO PARA O TEMPLATE
    # ========================================
    
    context = {
        'form': form,
        'title': 'Criar Contrato a partir da Proposta',
        'proposta': proposta,
        
        # ✅ ENVIAR DADOS DA PROPOSTA PARA EXIBIÇÃO NO TEMPLATE
        'dados_proposta': {
            'empreendimento': proposta.empreendimento.nome,
            'unidade': proposta.unidade.identificacao,
            'cliente': proposta.cliente.nome_completo,
            'cliente_cpf': proposta.cliente.cpf,
            'cliente_endereco': proposta.cliente.get_endereco_completo(),
            'corretor': proposta.corretor.get_full_name(),
            'corretor_creci': proposta.corretor.creci,
            'valor_imovel': proposta.valor_imovel,
            'valor_financiamento': proposta.valor_financiamento,
            'valor_subsidio': proposta.valor_subsidio,
            'valor_fgts': proposta.valor_fgts,
            'valor_entrada': proposta.valor_entrada,
            'valor_parcelamento': proposta.valor_parcelamento_sem_juros,
            'numero_parcelas': proposta.numero_parcelas,
            'valor_parcela': proposta.valor_parcela,
        }
    }
    
    return render(request, 'contratus/contratos/contrato_form.html', context)


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
    
    config = Configuracao.load()
    
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
    """API para retornar tipos de unidade de um empreendimento (AJAX)"""
    tipos = TipoUnidade.objects.filter(
        empreendimento_id=empreendimento_pk,
        ativo=True
    )
    
    data = [
        {
            'id': tipo.id,
            'nome': tipo.nome,
            'descricao': tipo.get_descricao_completa(),
            'valor_imovel': str(tipo.valor_imovel),
            'valor_engenharia': str(tipo.valor_engenharia_necessaria or 0),
            'quartos': tipo.quartos,
            'banheiros': tipo.banheiros,
            'area_util': str(tipo.area_util) if tipo.area_util else None,
        }
        for tipo in tipos
    ]
    
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
        form = UnidadeForm(request.POST, empreendimento_id=empreendimento_pk)
        if form.is_valid():
            unidade = form.save(commit=False)  # ✅ NÃO salva ainda
            unidade.empreendimento = empreendimento  # ✅ Define o empreendimento
            unidade.save()  # ✅ Agora salva
            messages.success(request, f'Unidade "{unidade.identificacao}" criada com sucesso!')
            return redirect('empreendimento_detail', pk=empreendimento_pk)
        else:
            # ✅ ADICIONAR para debug
            messages.error(request, f'Erro ao salvar: {form.errors}')
    else:
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
            messages.success(request, f'Unidade "{unidade.identificacao}" atualizada com sucesso!')
            return redirect('empreendimento_detail', pk=unidade.empreendimento.pk)
    else:
        form = UnidadeForm(instance=unidade)
    
    return render(request, 'contratus/unidades/unidade_form.html', {  # ✅ CORRIGIDO
        'form': form,
        'title': f'Editar Unidade: {unidade.identificacao}',
        'empreendimento': unidade.empreendimento
    })


@login_required
def unidades_em_lote_create(request, empreendimento_pk):
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
        identificacao = unidade.identificacao
        unidade.delete()
        messages.success(request, f'Unidade "{identificacao}" excluída com sucesso!')
    
    return redirect('empreendimento_detail', pk=empreendimento_pk)