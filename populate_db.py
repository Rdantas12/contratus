"""
Script para popular o banco de dados do sistema Contratus
Cria: 1 administrador, 4 gerentes, 12 corretores (3 por equipe)
Além de dados de construtoras, empreendimentos e unidades para testes
"""

import os
import django
import random
from decimal import Decimal
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from contratus.models import (
    User, Equipe, Construtora, Empreendimento, UnidadeEmpreendimento,
    Cliente, TipoUnidade
)

User = get_user_model()


def limpar_dados():
    """Limpa dados existentes (CUIDADO!)"""
    print("⚠️  Limpando dados existentes...")
    User.objects.all().delete()
    Equipe.objects.all().delete()
    Construtora.objects.all().delete()
    Empreendimento.objects.all().delete()
    UnidadeEmpreendimento.objects.all().delete()
    Cliente.objects.all().delete()
    TipoUnidade.objects.all().delete()
    print("✅ Dados limpos!")


def criar_administrador():
    """Cria 1 administrador"""
    print("\n📌 Criando Administrador...")
    
    admin = User.objects.create_user(
        username='admin',
        password='admin123',
        email='admin@contratus.com',
        first_name='Administrador',
        last_name='Sistema',
        cpf='000.000.000-00',
        telefone='(11) 99999-0000',
        nivel='administrador',
        is_staff=True,
        is_superuser=True
    )
    
    print(f"✅ Administrador criado: {admin.username} / senha: admin123")
    return admin


def criar_equipes_gerentes_corretores():
    """Cria 4 equipes, cada uma com 1 gerente e 3 corretores"""
    print("\n📌 Criando Equipes, Gerentes e Corretores...")
    
    equipes_nomes = ['Equipe Alpha', 'Equipe Beta', 'Equipe Gamma', 'Equipe Delta']
    
    todos_usuarios = []
    
    for i, nome_equipe in enumerate(equipes_nomes, start=1):
        # Criar equipe
        equipe = Equipe.objects.create(
            nome=nome_equipe,
            ativa=True
        )
        print(f"\n🏢 Equipe criada: {nome_equipe}")
        
        # Criar gerente da equipe
        gerente = User.objects.create_user(
            username=f'gerente{i}',
            password='gerente123',
            email=f'gerente{i}@contratus.com',
            first_name=f'Gerente',
            last_name=f'Equipe {i}',
            cpf=f'111.111.11{i}-{i}0',
            creci=f'CRECI-{10000 + i}',
            telefone=f'(11) 9888{i}-000{i}',
            nivel='gerente',
            equipe=equipe
        )
        
        # Definir líder da equipe
        equipe.lider = gerente
        equipe.save()
        
        print(f"  👔 Gerente: {gerente.username} / senha: gerente123")
        todos_usuarios.append(gerente)
        
        # Criar 3 corretores para essa equipe
        for j in range(1, 4):
            corretor_numero = (i - 1) * 3 + j
            corretor = User.objects.create_user(
                username=f'corretor{corretor_numero}',
                password='corretor123',
                email=f'corretor{corretor_numero}@contratus.com',
                first_name=f'Corretor',
                last_name=f'{corretor_numero}',
                cpf=f'222.222.{corretor_numero:03d}-{corretor_numero:02d}',
                creci=f'CRECI-{20000 + corretor_numero}',
                telefone=f'(11) 9777{corretor_numero}-{corretor_numero:04d}',
                nivel='corretor',
                equipe=equipe
            )
            
            print(f"    👤 Corretor: {corretor.username} / senha: corretor123")
            todos_usuarios.append(corretor)
    
    print(f"\n✅ Total: 4 gerentes e 12 corretores criados!")
    return todos_usuarios


def criar_construtoras():
    """Cria construtoras de exemplo"""
    print("\n📌 Criando Construtoras...")
    
    construtoras_data = [
        {
            'nome': 'Construtora Prime',
            'cnpj': '11.111.111/0001-11',
            'telefone': '(11) 3000-1111',
            'email': 'contato@prime.com.br',
            'endereco': 'Av. Paulista, 1000 - São Paulo/SP'
        },
        {
            'nome': 'Construtora Excellence',
            'cnpj': '22.222.222/0001-22',
            'telefone': '(11) 3000-2222',
            'email': 'contato@excellence.com.br',
            'endereco': 'Av. Faria Lima, 2000 - São Paulo/SP'
        },
        {
            'nome': 'Construtora Moderna',
            'cnpj': '33.333.333/0001-33',
            'telefone': '(11) 3000-3333',
            'email': 'contato@moderna.com.br',
            'endereco': 'R. dos Três Irmãos, 500 - São Paulo/SP'
        }
    ]
    
    construtoras = []
    for data in construtoras_data:
        construtora = Construtora.objects.create(**data)
        construtoras.append(construtora)
        print(f"  🏗️  {construtora.nome}")
    
    print(f"✅ {len(construtoras)} construtoras criadas!")
    return construtoras


def criar_tipos_unidade():
    """Cria tipos de unidade"""
    print("\n📌 Criando Tipos de Unidade...")
    
    tipos = [
        {'nome': 'Apartamento Padrão', 'descricao': 'Apartamento com acabamento padrão'},
        {'nome': 'Apartamento Premium', 'descricao': 'Apartamento com acabamento de luxo'},
        {'nome': 'Cobertura', 'descricao': 'Cobertura duplex com área privativa'},
        {'nome': 'Studio', 'descricao': 'Unidade compacta tipo studio'},
    ]
    
    tipos_criados = []
    for tipo_data in tipos:
        tipo = TipoUnidade.objects.create(**tipo_data)
        tipos_criados.append(tipo)
        print(f"  🏠 {tipo.nome}")
    
    print(f"✅ {len(tipos_criados)} tipos de unidade criados!")
    return tipos_criados


def criar_empreendimentos(construtoras, tipos_unidade):
    """Cria empreendimentos com unidades"""
    print("\n📌 Criando Empreendimentos...")
    
    empreendimentos_data = [
        {
            'nome': 'Residencial Parque das Flores',
            'endereco': 'Rua das Flores, 100',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'data_lancamento': date(2024, 1, 15),
            'data_entrega_prevista': date(2026, 6, 30),
            'descricao': 'Condomínio completo com área de lazer',
            'percentual_corretor': Decimal('2.50'),
            'percentual_gerente': Decimal('1.00')
        },
        {
            'nome': 'Edifício Vista Verde',
            'endereco': 'Av. Verde, 500',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'data_lancamento': date(2024, 3, 20),
            'data_entrega_prevista': date(2026, 12, 31),
            'descricao': 'Vista privilegiada para área verde',
            'percentual_corretor': Decimal('3.00'),
            'percentual_gerente': Decimal('1.50')
        },
        {
            'nome': 'Condomínio Solar do Itaim',
            'endereco': 'Rua Itaim, 250',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'data_lancamento': date(2024, 5, 10),
            'data_entrega_prevista': date(2027, 3, 15),
            'descricao': 'Localização premium no Itaim Bibi',
            'percentual_corretor': Decimal('2.00'),
            'percentual_gerente': Decimal('0.80')
        }
    ]
    
    empreendimentos = []
    
    for i, emp_data in enumerate(empreendimentos_data):
        # Atribuir construtora rotativa
        construtora = construtoras[i % len(construtoras)]
        
        empreendimento = Empreendimento.objects.create(
            construtora=construtora,
            **emp_data
        )
        empreendimentos.append(empreendimento)
        print(f"\n  🏢 {empreendimento.nome}")
        
        # Criar unidades para este empreendimento
        criar_unidades(empreendimento, tipos_unidade)
    
    print(f"\n✅ {len(empreendimentos)} empreendimentos criados!")
    return empreendimentos


def criar_unidades(empreendimento, tipos_unidade):
    """Cria unidades para um empreendimento"""
    print(f"    📦 Criando unidades para {empreendimento.nome}...")
    
    # Criar 20 unidades variadas
    unidades_criadas = 0
    
    for andar in range(1, 6):  # 5 andares
        for numero in range(1, 5):  # 4 unidades por andar
            tipo = random.choice(tipos_unidade)
            
            # Variar características baseado no tipo
            if tipo.nome == 'Studio':
                quartos = 1
                suites = 0
                banheiros = 1
                vagas = 0
                area = Decimal(random.randint(30, 45))
                valor_base = Decimal('180000.00')
            elif tipo.nome == 'Cobertura':
                quartos = 4
                suites = 2
                banheiros = 3
                vagas = 3
                area = Decimal(random.randint(150, 200))
                valor_base = Decimal('850000.00')
            elif tipo.nome == 'Apartamento Premium':
                quartos = 3
                suites = 1
                banheiros = 2
                vagas = 2
                area = Decimal(random.randint(80, 120))
                valor_base = Decimal('550000.00')
            else:  # Padrão
                quartos = 2
                suites = 1
                banheiros = 2
                vagas = 1
                area = Decimal(random.randint(60, 80))
                valor_base = Decimal('350000.00')
            
            # Adicionar variação de 10% no valor
            variacao = Decimal(random.uniform(0.9, 1.1))
            valor_imovel = (valor_base * variacao).quantize(Decimal('0.01'))
            valor_engenharia = (valor_imovel * Decimal('0.85')).quantize(Decimal('0.01'))
            
            unidade = UnidadeEmpreendimento.objects.create(
                empreendimento=empreendimento,
                tipo=tipo,
                numero=f'{andar}{numero:02d}',
                bloco='A',
                andar=str(andar),
                area_privativa=area,
                quartos=quartos,
                suites=suites,
                banheiros=banheiros,
                vagas_garagem=vagas,
                valor_imovel=valor_imovel,
                valor_engenharia=valor_engenharia,
                status='disponivel'
            )
            unidades_criadas += 1
    
    print(f"      ✅ {unidades_criadas} unidades criadas")


def criar_clientes():
    """Cria clientes de exemplo"""
    print("\n📌 Criando Clientes de Exemplo...")
    
    clientes_data = [
        {
            'nome': 'João Silva Santos',
            'cpf': '123.456.789-01',
            'rg': '12.345.678-9',
            'data_nascimento': date(1985, 5, 15),
            'estado_civil': 'casado',
            'profissao': 'Engenheiro',
            'renda_mensal': Decimal('12000.00'),
            'telefone': '(11) 98765-4321',
            'email': 'joao.silva@email.com',
            'endereco': 'Rua das Acácias, 123',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01234-567'
        },
        {
            'nome': 'Maria Oliveira Costa',
            'cpf': '234.567.890-12',
            'rg': '23.456.789-0',
            'data_nascimento': date(1990, 8, 20),
            'estado_civil': 'solteiro',
            'profissao': 'Médica',
            'renda_mensal': Decimal('15000.00'),
            'telefone': '(11) 97654-3210',
            'email': 'maria.oliveira@email.com',
            'endereco': 'Av. Paulista, 456',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01310-100'
        },
        {
            'nome': 'Carlos Eduardo Pereira',
            'cpf': '345.678.901-23',
            'rg': '34.567.890-1',
            'data_nascimento': date(1988, 3, 10),
            'estado_civil': 'divorciado',
            'profissao': 'Advogado',
            'renda_mensal': Decimal('18000.00'),
            'telefone': '(11) 96543-2109',
            'email': 'carlos.pereira@email.com',
            'endereco': 'Rua Augusta, 789',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01305-100'
        },
        {
            'nome': 'Ana Paula Rodrigues',
            'cpf': '456.789.012-34',
            'rg': '45.678.901-2',
            'data_nascimento': date(1992, 11, 25),
            'estado_civil': 'casado',
            'profissao': 'Arquiteta',
            'renda_mensal': Decimal('10000.00'),
            'telefone': '(11) 95432-1098',
            'email': 'ana.rodrigues@email.com',
            'endereco': 'Rua Haddock Lobo, 321',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01414-001'
        },
        {
            'nome': 'Pedro Henrique Alves',
            'cpf': '567.890.123-45',
            'rg': '56.789.012-3',
            'data_nascimento': date(1987, 7, 8),
            'estado_civil': 'solteiro',
            'profissao': 'Empresário',
            'renda_mensal': Decimal('25000.00'),
            'telefone': '(11) 94321-0987',
            'email': 'pedro.alves@email.com',
            'endereco': 'Av. Faria Lima, 654',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '04538-132'
        }
    ]
    
    # Pegar um corretor aleatório para atribuir aos clientes
    corretores = User.objects.filter(nivel='corretor')
    
    clientes = []
    for cliente_data in clientes_data:
        corretor = random.choice(corretores)
        cliente = Cliente.objects.create(
            corretor_cadastro=corretor,
            **cliente_data
        )
        clientes.append(cliente)
        print(f"  👤 {cliente.nome}")
    
    print(f"✅ {len(clientes)} clientes criados!")
    return clientes


def main():
    """Função principal"""
    print("\n" + "="*60)
    print("🚀 SCRIPT DE POPULAÇÃO DO BANCO DE DADOS - CONTRATUS")
    print("="*60)
    
    resposta = input("\n⚠️  Este script irá LIMPAR todos os dados existentes. Continuar? (s/n): ")
    if resposta.lower() != 's':
        print("❌ Operação cancelada.")
        return
    
    try:
        # Limpar dados existentes
        limpar_dados()
        
        # Criar estrutura
        admin = criar_administrador()
        usuarios = criar_equipes_gerentes_corretores()
        construtoras = criar_construtoras()
        tipos_unidade = criar_tipos_unidade()
        empreendimentos = criar_empreendimentos(construtoras, tipos_unidade)
        clientes = criar_clientes()
        
        print("\n" + "="*60)
        print("✅ BANCO DE DADOS POPULADO COM SUCESSO!")
        print("="*60)
        print("\n📊 RESUMO:")
        print(f"  • 1 Administrador")
        print(f"  • 4 Gerentes (1 por equipe)")
        print(f"  • 12 Corretores (3 por equipe)")
        print(f"  • {len(construtoras)} Construtoras")
        print(f"  • {len(tipos_unidade)} Tipos de Unidade")
        print(f"  • {len(empreendimentos)} Empreendimentos")
        print(f"  • {UnidadeEmpreendimento.objects.count()} Unidades")
        print(f"  • {len(clientes)} Clientes")
        
        print("\n🔐 CREDENCIAIS DE ACESSO:")
        print("  Administrador:")
        print("    usuário: admin | senha: admin123")
        print("\n  Gerentes:")
        print("    usuário: gerente1 a gerente4 | senha: gerente123")
        print("\n  Corretores:")
        print("    usuário: corretor1 a corretor12 | senha: corretor123")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
