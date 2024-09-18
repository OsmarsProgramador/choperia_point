# produto/views.py
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Categoria, Produto

"""class ProdutoListView(LoginRequiredMixin, ListView):
    def get(self, request):
        produtos_list = Produto.objects.all().order_by('nome_produto')
        categorias = Categoria.objects.all()
        
        paginator = Paginator(produtos_list, 10)  # 10 produtos por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'produto/list_produto.html', {
            'produtos': page_obj.object_list,
            'categorias': categorias,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        })"""

class ProdutoListView(LoginRequiredMixin, ListView):
    def get(self, request):
        produtos_list = Produto.objects.all().order_by('nome_produto')
        categorias = Categoria.objects.all()
        
        return render(request, 'produto/list_produto.html', {
            'produtos': produtos_list,
            'categorias': categorias,
        })


class CategoriaListView(LoginRequiredMixin, ListView):
    def get(self, request):
        categorias_list = Categoria.objects.all().order_by('nome')

        paginator = Paginator(categorias_list, 10)  # 10 categorias por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'produto/list_categoria.html', {
            'categorias': page_obj.object_list,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        })

