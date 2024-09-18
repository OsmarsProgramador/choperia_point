# scripts/gerar_dados.py
import os
import sys
import django
import random
from faker import Faker
from validate_docbr import CNPJ

# Adicione o caminho do diretório do projeto ao sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'choperia.settings')
django.setup()

from empresa.models import Empresa, NotaFiscal
from produto.models import Categoria, Produto
from mesa.models import Mesa
from estoque.models import Estoque
from django.utils import timezone
from django.shortcuts import render, redirect
import os
import pandas as pd
import decimal

from django.conf import settings
from empresa.models import Empresa

def get_empresa_padrao():
    return Empresa.objects.get(cnpj=settings.DEFAULT_EMPRESA_CNPJ)

fake = Faker('pt_BR')
cnpj_generator = CNPJ()

def create_empresas_and_notas():
    # Verificar e criar a empresa padrão apenas se ela não existir
    if not Empresa.objects.filter(cnpj='57.851.872/3504-08').exists():
        Empresa.objects.create(
            nome='Choperia Point do Morro',
            endereco='Avenida Cumbica, 784 Vila Gilda 04954-203 Bairro Bom / SP',
            telefone='945876323',
            email='choperia@example.net',
            cnpj='57.851.872/3504-08'
        )

    # Criar empresas fakes e notas fiscais associadas
    for _ in range(10):
        cnpj = cnpj_generator.generate()
        empresa = Empresa.objects.create(
            nome=fake.company(),
            endereco=fake.address(),
            telefone=fake.phone_number(),
            email=fake.email(),
            cnpj=cnpj
        )
        for _ in range(20):
            NotaFiscal.objects.create(
                empresa=empresa,
                serie=fake.bothify(text='??###'),
                numero=fake.random_int(min=1000, max=9999),
                descricao=fake.text(max_nb_chars=200),
                data=fake.date_this_decade()
            )

def create_produtos():
    # caminho do arquivo
    file_path = os.path.join(settings.BASE_DIR, 'produto', 'tabelas/produtos.xlsx')
    df = pd.read_excel(file_path, header=1)  # Lendo o cabeçalho a partir da linha 2

    # Obter a empresa padrão (substitua pela lógica de obter a empresa correta)
    empresa_padrao = Empresa.objects.first()  # Ou uma lógica para selecionar a empresa correta

    for index, item in df.iterrows():
        categoria_nome = item['categoria']
        # Obter ou criar a categoria
        categoria, created = Categoria.objects.get_or_create(nome=categoria_nome)
        
        # Convertendo os valores para decimal
        custo = decimal.Decimal(str(item['custo']).replace(',', '.'))
        venda = decimal.Decimal(str(item['venda']).replace(',', '.'))
        
        # Criar o produto
        produto = Produto.objects.create(
            nome_produto=item['nome_produto'],
            categoria=categoria,
            descricao=item['descricao'],
            custo=custo,
            venda=venda,
            codigo=item['codigo'],
            estoque=item['estoque'],
            estoque_total=item['estoque_total'],
            imagem=item['imagem']
        )
        
        # Criar registro de entrada no estoque
        try:
            Estoque.objects.create(
                empresa=get_empresa_padrao(),
                produto=produto,
                quantidade=produto.estoque,  # Quantidade inicial
                tipo='entrada',
                data=timezone.now()
            )
        except Exception as e:
            print(f"Erro ao registrar entrada no estoque para {produto.nome_produto}: {e}")
        # Redirecionar para a listagem de produtos na visualização de cards após a importação
        # return redirect('prodoto:produto_list')

def create_mesas():
    for i in range(1, 11):
        Mesa.objects.create(nome=f'{str(i).zfill(2)}') # Cria um numero com 2 digitos


def add_produtos_to_mesas():
    produtos = list(Produto.objects.all())
    for mesa in Mesa.objects.all():
        itens = random.sample(produtos, k=random.randint(1, 5))
        mesa.itens = [{"produto_id": produto.id, "quantidade": random.randint(1, 5)} for produto in itens]
        mesa.save()

def create_estoque():
    empresas = list(Empresa.objects.all())
    produtos = list(Produto.objects.all())
    for _ in range(100):
        empresa = random.choice(empresas)
        produto = random.choice(produtos)
        tipo = random.choice(['entrada', 'saida'])
        quantidade = fake.random_int(min=1, max=50)
        Estoque.objects.create(
            empresa=empresa,
            produto=produto,
            quantidade=quantidade,
            tipo=tipo,
            data=fake.date_this_year()
        )

if __name__ == '__main__':
    create_empresas_and_notas()
    create_produtos()
    create_mesas()
    # add_produtos_to_mesas()
    # create_estoque()


