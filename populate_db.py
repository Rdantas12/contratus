# populate_db.py
import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # MUDE AQUI
django.setup()

from django.contrib.auth import get_user_model
from contratus.models import (
    Equipe, Construtora, Empreendimento, UnidadeEmpreendimento,
    Cliente, Proposta, Configuracao
)

User = get_user_model()

def limpar_dados():
    """Limpa dados de teste anteriores"""
    print("🧹 Limpando dados anteriores...")
    Proposta.objects.all().delete()
    Cliente.objects.all().delete()
    UnidadeEmpreendimento.objects.all().delete()
    Empreendimento.objects.all().delete()
    Construtora.objects.all().delete()
    User.objects.filter(nivel__in=['gerente', 'corretor']).delete()
    Equipe.objects.all().delete()
    print("✅ Dados limpos com sucesso!\n")

def criar_equipes():
    """Cria equipes"""
    print("👥 Criando equipes...")
    
    equipe1 = Equipe.objects.create(
        nome="Equipe Centro",
        descricao="Equipe responsável pela região central",
        ativa=True
    )
    
    equipe2 = Equipe.objects.create(
        nome="Equipe Zona Sul",
        descricao="Equipe responsável pela zona sul",
        ativa=True
    )
    
    print(f"✅ Criadas {Equipe.objects.count()} equipes\n")
    return equipe1, equipe2

def criar_usuarios(equipe1, equipe2):
    """Cria usuários de teste"""
    print("👤 Criando usuários...")
    
    # Administrador
    admin = User.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@clickgr2.com',
        first_name='Administrador',
        last_name='Sistema',
        cpf='111.111.111-11',
        telefone='(21) 99999-9999',
        nivel='administrador',
        ativo=True
    )
    print(f"   ✓ Admin: {admin.username} / admin123")
    
    # Gerente 1
    gerente1 = User.objects.create_user(
        username='gerente1',
        password='gerente123',
        email='gerente1@clickgr2.com',
        first_name='Carlos',
        last_name='Silva',
        cpf='222.222.222-22',
        creci='CRECI 54321',
        telefone='(21) 98888-8888',
        nivel='gerente',
        equipe=equipe1,
        ativo=True
    )
    equipe1.gerente = gerente1
    equipe1.save()
    print(f"   ✓ Gerente: {gerente1.username} / gerente123")
    
    # Gerente 2
    gerente2 = User.objects.create_user(
        username='gerente2',
        password='gerente123',
        email='gerente2@clickgr2.com',
        first_name='Mariana',
        last_name='Oliveira',
        cpf='333.333.333-33',
        creci='CRECI 54322',
        telefone='(21) 98777-7777',
        nivel='gerente',
        equipe=equipe2,
        ativo=True
    )
    equipe2.gerente = gerente2
    equipe2.save()
    print(f"   ✓ Gerente: {gerente2.username} / gerente123")
    
    # Corretores Equipe 1
    corretor1 = User.objects.create_user(
        username='corretor1',
        password='corretor123',
        email='corretor1@clickgr2.com',
        first_name='João',
        last_name='Santos',
        cpf='444.444.444-44',
        creci='CRECI 12345',
        telefone='(21) 97777-7777',
        nivel='corretor',
        equipe=equipe1,
        ativo=True
    )
    print(f"   ✓ Corretor: {corretor1.username} / corretor123")
    
    corretor2 = User.objects.create_user(
        username='corretor2',
        password='corretor123',
        email='corretor2@clickgr2.com',
        first_name='Maria',
        last_name='Costa',
        cpf='555.555.555-55',
        creci='CRECI 12346',
        telefone='(21) 97666-6666',
        nivel='corretor',
        equipe=equipe1,
        ativo=True
    )
    print(f"   ✓ Corretor: {corretor2.username} / corretor123")
    
    # Corretores Equipe 2
    corretor3 = User.objects.create_user(
        username='corretor3',
        password='corretor123',
        email='corretor3@clickgr2.com',
        first_name='Pedro',
        last_name='Almeida',
        cpf='666.666.666-66',
        creci='CRECI 12347',
        telefone='(21) 97555-5555',
        nivel='corretor',
        equipe=equipe2,
        ativo=True
    )
    print(f"   ✓ Corretor: {corretor3.username} / corretor123")
    
    corretor4 = User.objects.create_user(
        username='corretor4',
        password='corretor123',
        email='corretor4@clickgr2.com',
        first_name='Ana',
        last_name='Ferreira',
        cpf='777.777.777-77',
        creci='CRECI 12348',
        telefone='(21) 97444-4444',
        nivel='corretor',
        equipe=equipe2,
        ativo=True
    )
    print(f"   ✓ Corretor: {corretor4.username} / corretor123")
    
    print(f"✅ Criados {User.objects.count()} usuários\n")
    return admin, gerente1, gerente2, corretor1, corretor2, corretor3, corretor4

def criar_construtoras(admin):
    """Cria construtoras de teste"""
    print("🏗️ Criando construtoras...")
    
    construtora1 = Construtora.objects.create(
        razao_social="RJZ Cyrela Incorporações Ltda",
        nome_fantasia="RJZ Cyrela",
        cnpj="12.345.678/0001-90",
        rua="Av. das Américas",
        numero="5000",
        bairro="Barra da Tijuca",
        cidade="Rio de Janeiro",
        estado="RJ",
        cep="22640-100",
        telefone="(21) 3333-3333",
        email="contato@rjzcyrela.com.br",
        responsavel_legal="Roberto Silva",
        ativa=True,
        cadastrado_por=admin
    )
    print(f"   ✓ {construtora1.nome_fantasia}")
    
    construtora2 = Construtora.objects.create(
        razao_social="Tenda Construções S.A.",
        nome_fantasia="Tenda",
        cnpj="98.765.432/0001-10",
        rua="Rua da Construção",
        numero="100",
        bairro="Centro",
        cidade="São Gonçalo",
        estado="RJ",
        cep="24440-000",
        telefone="(21) 2222-2222",
        email="contato@tenda.com.br",
        responsavel_legal="José Oliveira",
        ativa=True,
        cadastrado_por=admin
    )
    print(f"   ✓ {construtora2.nome_fantasia}")
    
    construtora3 = Construtora.objects.create(
        razao_social="MRV Engenharia e Participações S.A.",
        nome_fantasia="MRV",
        cnpj="11.222.333/0001-44",
        rua="Av. Brasil",
        numero="2500",
        bairro="Penha",
        cidade="Rio de Janeiro",
        estado="RJ",
        cep="21020-000",
        telefone="(21) 4444-4444",
        email="contato@mrv.com.br",
        responsavel_legal="Maria Santos",
        ativa=True,
        cadastrado_por=admin
    )
    print(f"   ✓ {construtora3.nome_fantasia}")
    
    print(f"✅ Criadas {Construtora.objects.count()} construtoras\n")
    return construtora1, construtora2, construtora3

def criar_empreendimentos(construtoras, admin):
    """Cria empreendimentos de teste"""
    print("🏘️ Criando empreendimentos...")
    
    c1, c2, c3 = construtoras
    hoje = datetime.now().date()
    
    # Empreendimento 1 - RJZ Cyrela
    emp1 = Empreendimento.objects.create(
        nome="Residencial Vista Mar",
        construtora=c1,
        tipo_imovel="apartamento",
        rua="Rua das Palmeiras",
        numero="500",
        bairro="Barra da Tijuca",
        cidade="Rio de Janeiro",
        estado="RJ",
        cep="22640-200",
        descricao_completa="Apartamento com 2 quartos, sala, cozinha, banheiro e área de serviço. Condomínio com piscina, churrasqueira e salão de festas.",
        quartos=2,
        banheiros=1,
        vagas_garagem=1,
        area_util=Decimal("65.00"),
        total_unidades=50,
        unidades_disponiveis=50,
        valor_imovel=Decimal("280000.00"),
        valor_engenharia_necessaria=Decimal("250000.00"),
        taxa_corretagem_percentual=Decimal("5.00"),
        status="lancamento",
        data_lancamento=hoje,
        data_entrega_prevista=hoje + timedelta(days=730),
        ativo=True,
        cadastrado_por=admin
    )
    print(f"   ✓ {emp1.nome}")
    
    # Empreendimento 2 - Tenda
    emp2 = Empreendimento.objects.create(
        nome="Condomínio Vila Verde",
        construtora=c2,
        tipo_imovel="casa",
        rua="Rua João Pessoa",
        numero="1200",
        bairro="Centro",
        cidade="São Gonçalo",
        estado="RJ",
        cep="24440-300",
        descricao_completa="Casa linear com 2 quartos, sala, cozinha, banheiro e quintal. Área de lazer comunitária.",
        quartos=2,
        banheiros=1,
        vagas_garagem=0,
        area_util=Decimal("55.00"),
        total_unidades=30,
        unidades_disponiveis=30,
        valor_imovel=Decimal("220000.00"),
        valor_engenharia_necessaria=Decimal("200000.00"),
        taxa_corretagem_percentual=Decimal("5.00"),
        status="em_obras",
        data_lancamento=hoje - timedelta(days=90),
        data_entrega_prevista=hoje + timedelta(days=540),
        ativo=True,
        cadastrado_por=admin
    )
    print(f"   ✓ {emp2.nome}")
    
    # Empreendimento 3 - MRV
    emp3 = Empreendimento.objects.create(
        nome="Residencial Parque das Flores",
        construtora=c3,
        tipo_imovel="apartamento",
        rua="Av. Central",
        numero="800",
        bairro="Vila Iara",
        cidade="São Gonçalo",
        estado="RJ",
        cep="24465-100",
        descricao_completa="Apartamento com 3 quartos sendo 1 suíte, sala, cozinha americana, 2 banheiros e área de serviço. Lazer completo.",
        quartos=3,
        banheiros=2,
        vagas_garagem=1,
        area_util=Decimal("75.00"),
        total_unidades=80,
        unidades_disponiveis=80,
        valor_imovel=Decimal("320000.00"),
        valor_engenharia_necessaria=Decimal("290000.00"),
        taxa_corretagem_percentual=Decimal("5.00"),
        status="lancamento",
        data_lancamento=hoje,
        data_entrega_prevista=hoje + timedelta(days=900),
        ativo=True,
        cadastrado_por=admin
    )
    print(f"   ✓ {emp3.nome}")
    
    # Empreendimento 4 - Tenda (Kitnet)
    emp4 = Empreendimento.objects.create(
        nome="Smart Living São Gonçalo",
        construtora=c2,
        tipo_imovel="kitnet",
        rua="Rua Feliciano Sodré",
        numero="350",
        bairro="Centro",
        cidade="São Gonçalo",
        estado="RJ",
        cep="24440-400",
        descricao_completa="Kitnet moderna com área integrada, banheiro completo. Ideal para estudantes e solteiros.",
        quartos=1,
        banheiros=1,
        vagas_garagem=0,
        area_util=Decimal("32.00"),
        total_unidades=40,
        unidades_disponiveis=40,
        valor_imovel=Decimal("150000.00"),
        valor_engenharia_necessaria=Decimal("135000.00"),
        taxa_corretagem_percentual=Decimal("5.00"),
        status="pronto",
        data_lancamento=hoje - timedelta(days=180),
        data_entrega_prevista=hoje + timedelta(days=30),
        ativo=True,
        cadastrado_por=admin
    )
    print(f"   ✓ {emp4.nome}")
    
    print(f"✅ Criados {Empreendimento.objects.count()} empreendimentos\n")
    return emp1, emp2, emp3, emp4

def criar_unidades(empreendimentos):
    """Cria unidades dos empreendimentos"""
    print("🏠 Criando unidades...")
    
    total_unidades = 0
    
    for emp in empreendimentos:
        # Criar unidades baseadas no tipo de imóvel
        if emp.tipo_imovel == 'apartamento':
            # Criar apartamentos por andar
            for andar in range(1, 11):  # 10 andares
                for apto in range(1, 6):  # 5 aptos por andar
                    UnidadeEmpreendimento.objects.create(
                        empreendimento=emp,
                        identificacao=f"Apto {andar}0{apto}",
                        andar=str(andar),
                        bloco="A",
                        status='disponivel'
                    )
                    total_unidades += 1
                    if total_unidades >= emp.total_unidades:
                        break
                if total_unidades >= emp.total_unidades:
                    break
        
        elif emp.tipo_imovel == 'casa':
            # Criar casas numeradas
            for num in range(1, emp.total_unidades + 1):
                UnidadeEmpreendimento.objects.create(
                    empreendimento=emp,
                    identificacao=f"Casa {num:02d}",
                    status='disponivel'
                )
                total_unidades += 1
        
        elif emp.tipo_imovel == 'kitnet':
            # Criar kitnets
            for num in range(1, emp.total_unidades + 1):
                UnidadeEmpreendimento.objects.create(
                    empreendimento=emp,
                    identificacao=f"Kitnet {num:02d}",
                    andar=str((num-1) // 4 + 1),
                    status='disponivel'
                )
                total_unidades += 1
    
    print(f"✅ Criadas {UnidadeEmpreendimento.objects.count()} unidades\n")

def criar_clientes(corretores):
    """Cria clientes de teste"""
    print("👨‍👩‍👧‍👦 Criando clientes...")
    
    hoje = datetime.now().date()
    
    clientes_data = [
        {
            'nome': 'Roberto da Silva',
            'cpf': '100.100.100-10',
            'rg': '10.000.000-1',
            'telefone': '(21) 98000-0001',
            'email': 'roberto.silva@email.com',
            'origem': 'impulsionamento',
            'corretor': corretores[0]
        },
        {
            'nome': 'Fernanda Oliveira Santos',
            'cpf': '200.200.200-20',
            'rg': '20.000.000-2',
            'telefone': '(21) 98000-0002',
            'email': 'fernanda.santos@email.com',
            'origem': 'indicacao',
            'corretor': corretores[0]
        },
        {
            'nome': 'Carlos Eduardo Pereira',
            'cpf': '300.300.300-30',
            'rg': '30.000.000-3',
            'telefone': '(21) 98000-0003',
            'email': 'carlos.pereira@email.com',
            'origem': 'walkin',
            'corretor': corretores[1]
        },
        {
            'nome': 'Juliana Costa Almeida',
            'cpf': '400.400.400-40',
            'rg': '40.000.000-4',
            'telefone': '(21) 98000-0004',
            'email': 'juliana.almeida@email.com',
            'origem': 'site',
            'corretor': corretores[1]
        },
        {
            'nome': 'Marcos Vinícius Souza',
            'cpf': '500.500.500-50',
            'rg': '50.000.000-5',
            'telefone': '(21) 98000-0005',
            'email': 'marcos.souza@email.com',
            'origem': 'redes_sociais',
            'corretor': corretores[2]
        },
        {
            'nome': 'Patricia Lima Rodrigues',
            'cpf': '600.600.600-60',
            'rg': '60.000.000-6',
            'telefone': '(21) 98000-0006',
            'email': 'patricia.rodrigues@email.com',
            'origem': 'telefone',
            'corretor': corretores[2]
        },
        {
            'nome': 'André Luiz Martins',
            'cpf': '700.700.700-70',
            'rg': '70.000.000-7',
            'telefone': '(21) 98000-0007',
            'email': 'andre.martins@email.com',
            'origem': 'impulsionamento',
            'corretor': corretores[3]
        },
        {
            'nome': 'Camila Ferreira Gomes',
            'cpf': '800.800.800-80',
            'rg': '80.000.000-8',
            'telefone': '(21) 98000-0008',
            'email': 'camila.gomes@email.com',
            'origem': 'indicacao',
            'corretor': corretores[3]
        },
        {
            'nome': 'Ricardo Alves da Costa',
            'cpf': '900.900.900-90',
            'rg': '90.000.000-9',
            'telefone': '(21) 98000-0009',
            'email': 'ricardo.costa@email.com',
            'origem': 'site',
            'corretor': corretores[0]
        },
        {
            'nome': 'Vanessa Cristina Santos',
            'cpf': '101.101.101-01',
            'rg': '11.000.000-1',
            'telefone': '(21) 98000-0010',
            'email': 'vanessa.santos@email.com',
            'origem': 'redes_sociais',
            'corretor': corretores[1]
        },
    ]
    
    clientes = []
    for data in clientes_data:
        cliente = Cliente.objects.create(
            nome_completo=data['nome'],
            cpf=data['cpf'],
            rg=data['rg'],
            data_nascimento=hoje - timedelta(days=365*30),  # 30 anos atrás
            estado_civil='Solteiro(a)',
            telefone=data['telefone'],
            email=data['email'],
            rua='Rua Exemplo',
            numero='100',
            bairro='Centro',
            cidade='São Gonçalo',
            estado='RJ',
            cep='24440-000',
            origem=data['origem'],
            cadastrado_por=data['corretor']
        )
        clientes.append(cliente)
        print(f"   ✓ {cliente.nome_completo}")
    
    print(f"✅ Criados {Cliente.objects.count()} clientes\n")
    return clientes

def criar_configuracao():
    """Cria/atualiza configuração do sistema"""
    print("⚙️ Criando configuração do sistema...")
    config = Configuracao.load()
    print(f"✅ Configuração criada/atualizada\n")
    return config

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 POPULANDO BANCO DE DADOS - CONTRATUS")
    print("=" * 60)
    print()
    
    # Perguntar se deseja limpar dados anteriores
    resposta = input("⚠️ Deseja limpar dados anteriores? (s/n): ")
    if resposta.lower() == 's':
        limpar_dados()
    
    # Criar dados
    equipe1, equipe2 = criar_equipes()
    admin, gerente1, gerente2, corretor1, corretor2, corretor3, corretor4 = criar_usuarios(equipe1, equipe2)
    construtoras = criar_construtoras(admin)
    empreendimentos = criar_empreendimentos(construtoras, admin)
    criar_unidades(empreendimentos)
    clientes = criar_clientes([corretor1, corretor2, corretor3, corretor4])
    criar_configuracao()
    
    print("=" * 60)
    print("✅ BANCO DE DADOS POPULADO COM SUCESSO!")
    print("=" * 60)
    print()
    print("📊 RESUMO:")
    print(f"   • {User.objects.count()} usuários")
    print(f"   • {Equipe.objects.count()} equipes")
    print(f"   • {Construtora.objects.count()} construtoras")
    print(f"   • {Empreendimento.objects.count()} empreendimentos")
    print(f"   • {UnidadeEmpreendimento.objects.count()} unidades")
    print(f"   • {Cliente.objects.count()} clientes")
    print()
    print("👤 CREDENCIAIS DE ACESSO:")
    print("   Administrador:")
    print("      Usuário: admin")
    print("      Senha: admin123")
    print()
    print("   Gerentes:")
    print("      Usuário: gerente1 / Senha: gerente123")
    print("      Usuário: gerente2 / Senha: gerente123")
    print()
    print("   Corretores:")
    print("      Usuário: corretor1 / Senha: corretor123")
    print("      Usuário: corretor2 / Senha: corretor123")
    print("      Usuário: corretor3 / Senha: corretor123")
    print("      Usuário: corretor4 / Senha: corretor123")
    print()
    print("=" * 60)

if __name__ == '__main__':
    main()
