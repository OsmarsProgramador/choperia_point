

# produto/urls.py

from django.urls import path
from . import views, htmx_views

app_name = 'produto'

urlpatterns = [
    path('', views.ProdutoListView.as_view(), name='list_produto'),
    path('categorias/', views.CategoriaListView.as_view(), name='list_categoria'),
    
]

# urls exclusiva para receber requisição do htmx
htmx_urlpatterns = [
    path('check_produto/', htmx_views.CheckProdutoView.as_view(), name='check_produto'),
    path('save_produto/', htmx_views.SaveProdutoView.as_view(), name='save_produto'),
    path('create_produto/', htmx_views.CreateProdutoView.as_view(), name='create_produto'),
    path('delete_produto/<int:id>/', htmx_views.DeleteProdutoView.as_view(), name='delete_produto'),
    path('edit_produto/<int:id>/', htmx_views.EditProdutoView.as_view(), name='edit_produto'),  # Adicionada URL para edição
    path('update_produto/', htmx_views.UpdateProdutoView.as_view(), name='update_produto'),  # URL para atualizar
    path('search-produto/', htmx_views.search_produto, name='search-produto'),
        
    # Adicionando as rotas para edição de categorias
    path('criar_categoria_modal/', htmx_views.AddCategoriaModalView.as_view(), name='criar_categoria_modal'),
    path('edit_categoria/<int:id>/', htmx_views.EditCategoriaView.as_view(), name='edit_categoria'),
    path('update_categoria/', htmx_views.UpdateCategoriaView.as_view(), name='update_categoria'),
    path('delete_categoria/<int:id>/', htmx_views.DeleteCategoriaView.as_view(), name='delete_categoria'),
    path('check_categoria/', htmx_views.CheckCategoriaView.as_view(), name='check_categoria'),
    path('search-categoria/', htmx_views.search_categoria, name='search-categoria'),
]

urlpatterns += htmx_urlpatterns


