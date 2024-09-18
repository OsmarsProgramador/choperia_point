Bom dia! Me responda em português. Preciso de um sistema de choperia baseado em classes em suas views, e tem objetivo criar um gerenciamento de notas fiscais/comandas, para prover o gerenciamento de notas fiscais de uma empresa e comandas de mesas. Escolha um local para implementar essa lógica. 

Esse projeto deverá ter um controle para que as páginas dos aplicativos empresa, produto, mesa, estoque sejam acessadas se um usuário estiver conectado.

Outros modelos que o projeto deve ter é o de Categoria (nome), Produto com os atributos (nome_produto, categoria, descricao, custo, venda, codigo, estoque, estoque_total e imagem com caminho upload_to='imagens/') e Mesa (id, nome, itens (default=list), status (default='Fechada') e pedido(default=0). Onde itens, será cada produto que for adicionado a mesa

**O nome do projeto**
    - choperia
    será representado por choperia (urls.py para as rotas que chegarao aos app)

**Os aplicativos**
   - core (base.html, index.html)
    A base.html deverá ter uma nav do bootstrep 5.3.3, com links para a página principal index.html e também um link para cada templates dos aplicativos empresa, produto, mesa, estoque. Se um aplicativo tiver mais de um template, deverá ser um dropdow. Toda teg deverá acessar a URL por meio de um namespace.
    A model dde core terá campos para controle de entrada e saída de estoque.
        # core/models.py
        from django.db import models # type: ignore


        class TimeStampedModel(models.Model):
            created = models.DateTimeField(
                'criado em',
                auto_now_add=True,
                auto_now=False
            )
            modified = models.DateTimeField(
                'modificado em',
                auto_now_add=False,
                auto_now=True
            )

            class Meta:
                abstract = True


   - usuario (para autenticação e cadastro)
    # usuario/models.py
    from django.db import models

    class Usuario(models.Model):
        nome = models.CharField(max_length=30)
        email = models.EmailField()
        senha = models.CharField(max_length=64) # sha256 vai transforma em uma hash unica e exclusiva de 64 caracteres
        ativo = models.BooleanField(default=False)

        def __str__(self) -> str:
            return self.nome

   - estoque com entrada e saída
    # estoque/models.py
    from django.db import models
    from core.models import TimeStampedModel

    class Estoque(TimeStampedModel):
        empresa = models.ForeignKey('empresa.Empresa', on_delete=models.CASCADE, related_name='estoques')
        produto = models.ForeignKey('produto.Produto', on_delete=models.CASCADE, related_name='entradas_saidas')
        quantidade = models.PositiveIntegerField()
        tipo = models.CharField(max_length=10)  # 'entrada' ou 'saída'
        data = models.DateField()

        def __str__(self):
            return f'{self.produto.nome_produto} - {self.quantidade} ({self.tipo})'

   - produto
    # produto/models.py
    from django.db import models

    class Categoria(models.Model):
        nome = models.CharField(max_length=255)

        def __str__(self):
            return self.nome


    class Produto(models.Model):
        nome_produto = models.CharField(max_length=255)
        categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
        descricao = models.TextField(blank=True, null=True)
        custo = models.DecimalField(max_digits=10, decimal_places=2)
        venda = models.DecimalField(max_digits=10, decimal_places=2)
        codigo = models.CharField(max_length=20, unique=True)
        estoque = models.PositiveIntegerField()
        estoque_total = models.PositiveIntegerField()
        imagem = models.ImageField(upload_to='imagens/', blank=True, null=True)

        def __str__(self):
            return self.nome_produto



   - mesa com criação de 10 mesas iniciais 
        # mesa/models.py
        from django.db import models

        class Mesa(models.Model):
            nome = models.CharField(max_length=50)
            itens = models.JSONField(default=list)
            status = models.CharField(max_length=10, default='Fechada')
            pedido = models.PositiveIntegerField(default=0)

            def __str__(self):
                return self.nome

   

   - empresa
    # empresa/models.py
    from django.db import models
    from django.core.validators import MinLengthValidator

    class Empresa(models.Model):
        nome = models.CharField(max_length=255)
        endereco = models.CharField(max_length=255, blank=True, null=True)
        telefone = models.CharField(max_length=20, blank=True, null=True)
        email = models.EmailField(blank=True, null=True)
        cnpj = models.CharField(max_length=18, unique=True, validators=[MinLengthValidator(18)])  # Adicionado campo CNPJ

        def __str__(self):
            return self.nome

    class NotaFiscal(models.Model):
        empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='notas')
        serie = models.CharField(max_length=10)
        numero = models.PositiveIntegerField()
        descricao = models.TextField()
        data = models.DateField()

        def __str__(self):
            return f"{self.serie} - {self.numero}"
   

    Crie uma página para exibir a listagem de empresas. Ao abrir os detalhes da empresa deve ser aberta a listagem de notas fiscais daquela empresa.

    - [x] Adicione à listagem de notas fiscais um campo de busca por número, nome do produto e data. A busca deve funcionar via GET.

    - [x] Paginação é bem vinda, utilize com boostrep 5.3.3 em todas tabela que forem exibidas.
    Você pode usar qualquer formato de Django views para este teste (CBV)

    Para a apresentação cadastre ao menos 10 empresas com 20 notas fiscais cada uma, que serão exibida por paginação. O nome de cada empresa pode ser gerado com um lorem ipsum e os dados das notas fiscais podem ser randomicos, porém válidos, com dados do Brasil e escrito em português.

    - [x] Inclua o script de geração das empresas no anexo do projeto
    - [x] Utilize arquivos externos para os dados de entrada
    - [x] Inclua um CSS à página para uma aparencia agradável (pode ser Bootstrap 5.3.3)
    - [x] A listagem de notas fiscais deve ser feita em uma tabela (HTML/boostrep 5.3.3)

    Para popular o banco de dados da aplicação utilizamos a biblioteca [Faker]. Os scripts de geração das empresas se encontram no diretório scripts, com dados do Brasil e escrito em português.

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

    fake = Faker('pt_BR')
    cnpj_generator = CNPJ()

    def create_empresas_and_notas():
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


    from django.shortcuts import render, redirect
    from django.conf import settings
    import os
    import pandas as pd
    def create_produtos():
        """if Produto.objects.exists():
            return redirect('produto:produto_list')
        else:"""
        # caminho do arquivo
        file_path = os.path.join(settings.BASE_DIR, 'produto', 'tabelas/produtos.xlsx')
        df = pd.read_excel(file_path, header=1)  # Lendo o cabeçalho a partir da linha 2

        for index, item in df.iterrows():
            categoria_nome = item['categoria']
            # Categoria.objects.create(nome=nome)
            categoria, created = Categoria.objects.get_or_create(nome=categoria_nome)
            Produto.objects.create( # já cria no BD direto
                nome_produto=item['nome_produto'],
                categoria=categoria,
                descricao=item['descricao'],
                custo=item['custo'],
                venda=item['venda'],
                codigo=item['codigo'],
                estoque=item['estoque'],
                estoque_total=item['estoque_total'],
                imagem=item['imagem']
            )
            # Redirecionar para a listagem de produtos na visualização de cards após a importação
            # return redirect('prodoto:produto_list')

    def create_mesas():
        for i in range(1, 11):
            Mesa.objects.create(nome=f'Mesa {i}')

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
        add_produtos_to_mesas()
        create_estoque()


Outros diretórios deverão está na raiz do projeto , tais como: além de scripts, media e static


Use Django CRUD (criar, recuperar, atualizar, excluir) visualizações genéricas baseadas em classe: -

CreateView – Visualizações baseadas em classe Django
DetailView – Visualizações baseadas em classe Django
UpdateView – Visualizações baseadas em classe Django
DeleteView – Visualizações baseadas em classe Django
FormView – Visualizações baseadas em classe Django



Se achar necessário use Apps de terceiros:
    'django_extensions', # pip install django_extensions
    'widget_tweaks', # pip install widget_tweaks   
    'bootstrapform', # pip install django-bootstrap-form

O projeto deverá ter a seguinte Estrutura:
.
├── .gitignore
├── Planilha de Controle de Estoque.xlsx
├── choperia/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── core/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   ├── __init__.py
│   ├── models.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
├── db.sqlite3
├── empresa/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   ├── models.py
│   ├── templates/
│   │   ├── empresa/
│   │   │   ├── empresa_detail.html
│   │   │   ├── empresa_list.html
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
├── estoque/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   ├── models.py
│   ├── templates/
│   │   ├── estoque/
│   │   │   ├── estoque_entrada_list.html
│   │   │   ├── estoque_saida_list.html
│   │   │   ├── protocolo_entrega_list.html
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
├── list_structure_clean.py
├── manage.py
├── media/
│   ├── imagens/
├── mesa/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   ├── models.py
│   ├── templates/
│   │   ├── mesa/
│   │   │   ├── abrir_mesa.html
│   │   │   ├── mesa_list.html
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
├── popular os bancos.txt
├── produto/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   ├── models.py
│   ├── tabelas/
│   │   ├── produtos.xlsx
│   ├── templates/
│   │   ├── produto/
│   │   │   ├── index.html
│   │   │   ├── produto_list.html
│   │   │   ├── produto_list_cards.html
│   │   │   ├── produto_list_fragment.html
│   │   │   ├── produto_list_table.html
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
├── scripts/
│   ├── gerar_dados.py
├── static/
│   ├── css/
│   │   ├── style.css
│   ├── img/
│   ├── js/
│   │   ├── script.js
├── testes.py
├── usuarios/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   ├── models.py
│   ├── templates/
│   │   ├── cadastro.html
│   │   ├── login.html
│   ├── tests.py
│   ├── urls.py
│   ├── views.py


Podemos usar 
# core/index.html
index.html: {% extends "base.html" %}

{% block content %}

  <div class="jumbotron">
    <div class="container">
      <h1>Bem-vindo!</h1>
      <p>Este é um sistema para controle de estoque para Choperia.</p>
      <p>
        <a href="https://github.com/rg3915/estoque">Veja no GitHub</a>
      </p>
    </div>
  </div>

{% endblock content %}

#   c h o p e r i a _ p o i n t  
 