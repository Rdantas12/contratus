# urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Construtoras (apenas admin)
    path('construtoras/', views.construtora_list, name='construtora_list'),
    path('construtoras/nova/', views.construtora_create, name='construtora_create'),
    path('construtoras/<int:pk>/editar/', views.construtora_edit, name='construtora_edit'),
    
    # Empreendimentos (apenas admin)
    path('empreendimentos/', views.empreendimento_list, name='empreendimento_list'),
    path('empreendimentos/novo/', views.empreendimento_create, name='empreendimento_create'),
    path('empreendimentos/<int:pk>/', views.empreendimento_detail, name='empreendimento_detail'),
    path('empreendimentos/<int:pk>/editar/', views.empreendimento_edit, name='empreendimento_edit'),
    
    # Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/novo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_edit, name='cliente_edit'),
    
    # Propostas
    path('propostas/', views.proposta_list, name='proposta_list'),
    path('propostas/nova/', views.proposta_create, name='proposta_create'),
    path('propostas/<int:pk>/', views.proposta_detail, name='proposta_detail'),
    path('propostas/<int:pk>/pdf/', views.proposta_gerar_pdf, name='proposta_gerar_pdf'),
    path('propostas/<int:pk>/aprovar/', views.proposta_aprovar, name='proposta_aprovar'),
    
    # Contratos
    path('contratos/', views.contrato_list, name='contrato_list'),
    path('contratos/criar/<int:proposta_pk>/', views.contrato_create_from_proposta, name='contrato_create_from_proposta'),
    path('contratos/<int:pk>/', views.contrato_detail, name='contrato_detail'),
    path('contratos/<int:pk>/pdf/', views.contrato_gerar_pdf, name='contrato_gerar_pdf'),
    path('contratos/<int:pk>/alterar-status/', views.contrato_alterar_status, name='contrato_alterar_status'),
    
    # API AJAX
    path('api/empreendimento/<int:pk>/', views.api_empreendimento_info, name='api_empreendimento_info'),
    path('api/cliente/<int:pk>/', views.api_cliente_info, name='api_cliente_info'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


     path('empreendimentos/<int:empreendimento_pk>/tipos/', 
         views.tipo_unidade_list, 
         name='tipo_unidade_list'),
    
    path('empreendimentos/<int:empreendimento_pk>/tipos/novo/', 
         views.tipo_unidade_create, 
         name='tipo_unidade_create'),
    
    path('tipos-unidade/<int:pk>/editar/', 
         views.tipo_unidade_edit, 
         name='tipo_unidade_edit'),
    
    path('tipos-unidade/<int:pk>/excluir/', 
         views.tipo_unidade_delete, 
         name='tipo_unidade_delete'),
    
    # =====================================================
    # UNIDADES
    # =====================================================
    path('empreendimentos/<int:empreendimento_pk>/unidades/nova/', 
         views.unidade_create, 
         name='unidade_create'),
    
    path('unidades/<int:pk>/editar/', 
         views.unidade_edit, 
         name='unidade_edit'),
    
    path('empreendimentos/<int:empreendimento_pk>/unidades/lote/', 
         views.unidades_em_lote_create, 
         name='unidades_em_lote_create'),
    
    # =====================================================
    # API AJAX
    # =====================================================
    path('api/empreendimentos/<int:empreendimento_pk>/tipos/', 
         views.api_tipos_unidade, 
         name='api_tipos_unidade'),



]
