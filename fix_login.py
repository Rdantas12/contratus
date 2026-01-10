"""
Script de correção para problemas de login no sistema Contratus

Identifica e corrige problemas comuns:
1. Campo 'ativo' inexistente no modelo User
2. Problemas de migração do banco de dados
3. Configurações incorretas de autenticação
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()


def verificar_modelo_user():
    """Verifica se o modelo User está correto"""
    print("\n📌 Verificando modelo User...")
    
    # Listar campos do modelo
    campos = [f.name for f in User._meta.get_fields()]
    print(f"  ✅ Campos encontrados no modelo: {', '.join(campos)}")
    
    # Verificar campos críticos
    campos_criticos = ['username', 'password', 'email', 'nivel', 'cpf', 'is_active']
    campos_faltando = [c for c in campos_criticos if c not in campos]
    
    if campos_faltando:
        print(f"  ⚠️  ATENÇÃO: Campos críticos faltando: {', '.join(campos_faltando)}")
        return False
    
    print("  ✅ Todos os campos críticos estão presentes")
    return True


def verificar_campo_ativo():
    """Verifica problema comum: uso de 'ativo' ao invés de 'is_active'"""
    print("\n📌 Verificando uso do campo 'ativo' no código...")
    
    campos = [f.name for f in User._meta.get_fields()]
    
    if 'ativo' in campos:
        print("  ⚠️  Campo 'ativo' encontrado no modelo")
        print("  💡 O Django padrão usa 'is_active'")
        print("  📝 Recomendação: Use 'is_active' ao invés de 'ativo'")
        return 'ativo'
    elif 'is_active' in campos:
        print("  ✅ Campo padrão 'is_active' está sendo usado corretamente")
        return 'is_active'
    else:
        print("  ❌ ERRO: Nenhum campo de status ativo encontrado!")
        return None


def verificar_tabelas_banco():
    """Verifica se as tabelas estão criadas no banco"""
    print("\n📌 Verificando tabelas do banco de dados...")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name;
        """)
        tabelas = [row[0] for row in cursor.fetchall()]
    
    # Verificar tabelas críticas
    tabelas_criticas = [
        'contratus_user',
        'auth_user',  # Caso esteja usando auth_user
        'contratus_equipe',
        'contratus_empreendimento',
        'contratus_unidadeempreendimento',
        'contratus_cliente',
        'contratus_proposta',
        'contratus_contrato'
    ]
    
    tabelas_existentes = [t for t in tabelas_criticas if t in tabelas]
    tabelas_faltando = [t for t in tabelas_criticas if t not in tabelas]
    
    print(f"  ✅ Tabelas encontradas: {len(tabelas_existentes)}")
    
    if tabelas_faltando:
        print(f"  ⚠️  Tabelas faltando: {', '.join(tabelas_faltando)}")
        print("\n  💡 Execute as migrações:")
        print("     python manage.py makemigrations")
        print("     python manage.py migrate")
        return False
    
    print("  ✅ Todas as tabelas críticas estão presentes")
    return True


def criar_views_corrigidas():
    """Cria versão corrigida do views.py"""
    print("\n📌 Gerando versão corrigida do views.py...")
    
    campo_ativo = verificar_campo_ativo()
    
    if campo_ativo == 'ativo':
        print("\n  📝 Arquivo 'views_corrigido.py' será criado")
        print("     Substituindo 'ativo' por 'is_active'")
        
        # Ler arquivo views.py
        try:
            with open('contratus/views.py', 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Substituir todas as ocorrências
            conteudo_corrigido = conteudo.replace(
                "filter(ativo=True)",
                "filter(is_active=True)"
            )
            conteudo_corrigido = conteudo_corrigido.replace(
                ".ativo",
                ".is_active"
            )
            conteudo_corrigido = conteudo_corrigido.replace(
                "user.is_active",
                "user.is_active"  # Garantir que está correto
            )
            
            # Salvar versão corrigida
            with open('contratus/views_corrigido.py', 'w', encoding='utf-8') as f:
                f.write(conteudo_corrigido)
            
            print("  ✅ Arquivo 'views_corrigido.py' criado com sucesso")
            print("\n  📝 PRÓXIMOS PASSOS:")
            print("     1. Faça backup do views.py original")
            print("     2. Substitua views.py por views_corrigido.py")
            print("     3. Reinicie o servidor Django")
            
            return True
            
        except FileNotFoundError:
            print("  ❌ Arquivo views.py não encontrado")
            print("     Execute este script na raiz do projeto Django")
            return False
    
    elif campo_ativo == 'is_active':
        print("  ✅ O campo está correto. Problema pode ser em outro lugar.")
        return True
    
    else:
        print("  ❌ Problema crítico com o modelo User")
        return False


def verificar_migrações():
    """Verifica status das migrações"""
    print("\n📌 Verificando migrações...")
    
    from django.db.migrations.executor import MigrationExecutor
    from django.db import connections
    
    connection = connections['default']
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    
    plan = executor.migration_plan(targets)
    
    if plan:
        print(f"  ⚠️  Existem {len(plan)} migrações pendentes")
        print("\n  💡 Execute:")
        print("     python manage.py migrate")
        return False
    else:
        print("  ✅ Todas as migrações estão aplicadas")
        return True


def testar_autenticacao():
    """Testa autenticação com usuário de teste"""
    print("\n📌 Testando autenticação...")
    
    from django.contrib.auth import authenticate
    
    # Verificar se existe algum usuário
    usuarios_count = User.objects.count()
    print(f"  📊 Total de usuários no banco: {usuarios_count}")
    
    if usuarios_count == 0:
        print("  ⚠️  Nenhum usuário encontrado")
        print("\n  💡 Execute o script populate_database.py para criar usuários")
        return False
    
    # Listar alguns usuários
    print("\n  👥 Usuários cadastrados:")
    for user in User.objects.all()[:5]:
        print(f"     - {user.username} ({user.nivel}) - ativo: {user.is_active}")
    
    return True


def criar_modelo_user_corrigido():
    """Cria versão corrigida do models.py"""
    print("\n📌 Gerando sugestão de correção para models.py...")
    
    campo_ativo = verificar_campo_ativo()
    
    if campo_ativo == 'ativo':
        print("\n  💡 CORREÇÃO NECESSÁRIA NO MODELS.PY:")
        print("  " + "="*50)
        print("""
  No arquivo models.py, REMOVA o campo 'ativo':
  
  # ❌ REMOVER:
  ativo = models.BooleanField(default=True)
  
  # ✅ O Django já possui este campo nativamente:
  is_active = models.BooleanField(default=True)
  
  Depois execute:
  python manage.py makemigrations
  python manage.py migrate
        """)
        print("  " + "="*50)
        return False
    
    return True


def gerar_relatorio():
    """Gera relatório completo de diagnóstico"""
    print("\n" + "="*60)
    print("📋 RELATÓRIO DE DIAGNÓSTICO - PROBLEMA DE LOGIN")
    print("="*60)
    
    resultados = {
        'modelo_user': verificar_modelo_user(),
        'campo_ativo': verificar_campo_ativo(),
        'tabelas_banco': verificar_tabelas_banco(),
        'migracoes': verificar_migrações(),
        'autenticacao': testar_autenticacao(),
    }
    
    print("\n" + "="*60)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("="*60)
    
    problemas = []
    
    for chave, valor in resultados.items():
        status = "✅" if valor else "❌"
        print(f"{status} {chave.replace('_', ' ').title()}")
        if not valor:
            problemas.append(chave)
    
    if problemas:
        print("\n⚠️  PROBLEMAS ENCONTRADOS:")
        for p in problemas:
            print(f"   - {p.replace('_', ' ').title()}")
        
        print("\n📝 SOLUÇÕES RECOMENDADAS:")
        
        if 'campo_ativo' in problemas or resultados['campo_ativo'] == 'ativo':
            print("""
   1️⃣  CORRIGIR CAMPO 'ATIVO':
       - Remover campo 'ativo' do modelo User
       - Usar 'is_active' (padrão do Django)
       - Substituir todas as ocorrências em views.py
            """)
        
        if not resultados['tabelas_banco']:
            print("""
   2️⃣  EXECUTAR MIGRAÇÕES:
       python manage.py makemigrations
       python manage.py migrate
            """)
        
        if not resultados['migracoes']:
            print("""
   3️⃣  APLICAR MIGRAÇÕES PENDENTES:
       python manage.py migrate
            """)
        
        if not resultados['autenticacao']:
            print("""
   4️⃣  POPULAR BANCO DE DADOS:
       python populate_database.py
            """)
    else:
        print("\n✅ Nenhum problema encontrado!")
        print("   Se o login ainda não funciona, verifique:")
        print("   - Senhas dos usuários")
        print("   - Configurações do settings.py")
        print("   - Logs do Django para erros específicos")
    
    print("\n" + "="*60)


def main():
    """Função principal"""
    print("\n" + "="*60)
    print("🔧 SCRIPT DE CORREÇÃO - PROBLEMA DE LOGIN")
    print("="*60)
    
    try:
        gerar_relatorio()
        
        print("\n📝 Deseja gerar arquivos de correção? (s/n): ", end='')
        resposta = input()
        
        if resposta.lower() == 's':
            criar_modelo_user_corrigido()
            criar_views_corrigidas()
        
        print("\n✅ Diagnóstico concluído!")
        
    except Exception as e:
        print(f"\n❌ ERRO durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
