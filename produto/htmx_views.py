# produto/htmx_views.py
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import Produto, Categoria
from estoque.models import Estoque
from .forms import ProdutoForm, CategoriaForm
from django.http import QueryDict
from django.utils import timezone

from django.conf import settings
from empresa.models import Empresa

def get_empresa_padrao():
    return Empresa.objects.get(cnpj=settings.DEFAULT_EMPRESA_CNPJ)
class CheckProdutoView(View):
    def get(self, request):
        produto_nome = request.GET.get('nome_produto')
        produtos = Produto.objects.filter(nome_produto__icontains=produto_nome)
        return render(request, 'produto/partials/htmx_componentes/check_produto.html', {'produtos': produtos})

class CreateProdutoView(View):  # equivalente a SaveProdutoView
    def post(self, request):
        form = ProdutoForm(request.POST)
        if form.is_valid():
            # Salvar o produto
            produto = form.save()
            
            # Criar registro de entrada no estoque
            try:
                Estoque.objects.create(
                    empresa=get_empresa_padrao(),  # Assumindo que Produto tem uma relação com Empresa
                    produto=produto,
                    quantidade=produto.estoque,  # Quantidade inicial no estoque
                    tipo='entrada',
                    data=timezone.now()
                )
            except Exception as e:
                return JsonResponse({'error': f'Erro ao registrar entrada no estoque: {e}'}, status=400)
            
            # Atualizar a lista de produtos
            produtos_list = Produto.objects.all().order_by('nome_produto')
            paginator = Paginator(produtos_list, 10)  # 10 produtos por página
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            return render(request, 'produto/partials/htmx_componentes/list_all_produtos.html', {
                'produtos': page_obj.object_list,
                'page_obj': page_obj,
                'is_paginated': page_obj.has_other_pages(),
            })
        return JsonResponse({'error': form.errors}, status=400)
    
class SaveProdutoView(View):
    def post(self, request):
        nome = request.POST.get('produto')
        preco = request.POST.get('preco')

        produto = Produto(nome=nome, preco=preco)
        produto.save()

        produtos = Produto.objects.all()
        return render(request, 'produto/partials/htmx_componentes/list_all_produtos.html', {'produtos': produtos})

def get_put_data(request):
    # Cria um QueryDict a partir dos dados do corpo da requisição
    return QueryDict(request.body)

class EditProdutoView(View):
    def get(self, request, id):
        produto = get_object_or_404(Produto, id=id)
        form = ProdutoForm(instance=produto)
        categorias = Categoria.objects.all()
        return render(request, 'produto/partials/htmx_componentes/edit_produto_form.html', {
            'form': form,
            'produto': produto,
            'categorias': categorias
        })
    
class UpdateProdutoView(View):
    def post(self, request):
        produto_id = request.POST.get('produto_id')
        produto = get_object_or_404(Produto, id=produto_id)
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            # Renderiza apenas a linha do produto atualizado
            return render(request, 'produto/partials/htmx_componentes/produto_row.html', {'produto': produto})
        return JsonResponse({'error': form.errors}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteProdutoView(View):
    def delete(self, request, id):
        produto = Produto.objects.get(id=id)
        produto.delete()
        produtos_list = Produto.objects.all().order_by('nome_produto')
        paginator = Paginator(produtos_list, 10)  # 10 produtos por página
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        return render(request, 'produto/partials/htmx_componentes/list_all_produtos.html', {
            'produtos': page_obj.object_list,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        })
    
def search_produto(request):
    search_text = request.POST.get('search', '')

    produtos_list = Produto.objects.filter(nome_produto__icontains=search_text).order_by('nome_produto')

    paginator = Paginator(produtos_list, 10)  # 10 produtos por página
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    print(f'paginator = {paginator}\npage_number = {page_number}\npage_obj = {page_obj}\nprodutos = {page_obj.object_list}\nis_paginated = {page_obj.has_other_pages()}')

    return render(request, 'produto/partials/htmx_componentes/list_all_produtos.html', {
        'produtos': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    })

class AddCategoriaModalView(View):
    def post(self, request):
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            categorias_list = Categoria.objects.all().order_by('nome')
            paginator = Paginator(categorias_list, 10)  # 10 categorias por página
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            return render(request, 'produto/partials/htmx_componentes/list_all_categoria.html', {
                'categorias': page_obj.object_list,
                'page_obj': page_obj,
                'is_paginated': page_obj.has_other_pages(),
            })
        return JsonResponse({'error': form.errors}, status=400)
    
@method_decorator(csrf_exempt, name='dispatch')
class EditCategoriaView(View):
    def get(self, request, id):
        categoria = get_object_or_404(Categoria, id=id)
        form = CategoriaForm(instance=categoria)
        return render(request, 'produto/partials/htmx_componentes/edit_categoria_form.html', {
            'form': form,
            'categoria': categoria
        })

    def put(self, request, id):
        categoria = get_object_or_404(Categoria, id=id)
        put_data = get_put_data(request)
        form = CategoriaForm(put_data, instance=categoria)
        if form.is_valid():
            form.save()
            categorias_list = Categoria.objects.all().order_by('nome')
            paginator = Paginator(categorias_list, 10)  # 10 categorias por página
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            return render(request, 'produto/partials/htmx_componentes/list_all_categoria.html', {
                'categorias': page_obj.object_list,
                'page_obj': page_obj,
                'is_paginated': page_obj.has_other_pages(),
            })
        return render(request, 'produto/partials/htmx_componentes/edit_categoria_form.html', {
            'form': form,
            'categoria': categoria,
        })

class UpdateCategoriaView(View):
    def post(self, request):
        categoria_id = request.POST.get('categoria_id')
        categoria = get_object_or_404(Categoria, id=categoria_id)
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            # Paginação
            page_number = request.POST.get('page', 1)
            categorias_list = Categoria.objects.all()
            paginator = Paginator(categorias_list, 10)  # 10 categorias por página
            page_obj = paginator.get_page(page_number)
            return render(request, 'produto/partials/htmx_componentes/list_all_categoria.html', {'categorias': page_obj})
        return JsonResponse({'error': form.errors}, status=400)
    
@method_decorator(csrf_exempt, name='dispatch')
class DeleteCategoriaView(View):
    def delete(self, request, id):
        categoria = Categoria.objects.get(id=id)
        categoria.delete()
        categorias_list = Categoria.objects.all().order_by('nome')
        paginator = Paginator(categorias_list, 10)  # 10 categorias por página
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'produto/partials/htmx_componentes/list_all_categoria.html', {
            'categorias': page_obj.object_list,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        })

class CheckCategoriaView(View):
    def get(self, request):
        categoria = request.GET.get('nome')
        categorias = Categoria.objects.filter(nome__icontains=categoria)
        return render(request, 'produto/partials/htmx_componentes/check_categoria.html', {'categorias': categorias})

def search_categoria(request): 
    search_text = request.POST.get('search', '')

    categorias_list = Categoria.objects.filter(nome__icontains=search_text).order_by('nome')

    paginator = Paginator(categorias_list, 10)  # 10 produtos por página
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'produto/partials/htmx_componentes/list_all_categoria.html', {
        'categorias': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    })

