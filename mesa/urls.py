# mesa/urls.py
from django.urls import path
from . import views, htmx_views

app_name = 'mesa'

urlpatterns = [
    path('', views.MesaListView.as_view(), name='list_mesa'),
    path('<int:id_mesa>/', views.AbrirMesaView.as_view(), name='abrir_mesa'),
    path('abrir/<int:id_mesa>/', views.AbrirMesaView.as_view(), name='abrir_mesa'),
    path('update_user/<int:pk>/', views.UpdateUserView.as_view(), name='update_user'),
    path('gerar_comanda_pdf/<int:id_mesa>/', views.GerarComandaPDFView.as_view(), name='gerar_comanda_pdf'),
    path('excluir_item/<int:id_mesa>/', views.ExcluirItemView.as_view(), name='excluir_item'),
    path('cancelar_pedido/<int:id_mesa>/', views.CancelarPedidoView.as_view(), name='cancelar_pedido'),
    path('enviar_para_cozinha/<int:id_mesa>/', views.EnviarParaCozinhaView.as_view(), name='enviar_para_cozinha'),
    path('realizar_pagamento/<int:id_mesa>/', views.RealizarPagamentoView.as_view(), name='realizar_pagamento'),
    path('pagamento_pessoa/<int:id_mesa>/', views.PagamentoPorPessoaView.as_view(), name='pagamento_pessoa'),
    path('confirmacao_pagamento/<int:id_mesa>/', views.ConfirmacaoPagamentoView.as_view(), name='confirmacao_pagamento'),
    path('imprimir_recibo/<int:id_mesa>/', views.GerarReciboPDFView.as_view(), name='imprimir_recibo'),
]


# urls exclusiva para receber requisição do htmx
htmx_urlpatterns = [
    path('adicionar_item/<int:id_mesa>/', htmx_views.AdicionarItemView.as_view(), name='adicionar_item'),
    path('adicionar_item/<int:id_mesa>/<int:produto_id>/', htmx_views.AdicionarItemView.as_view(), name='adicionar_item'),
    path('nova/', htmx_views.MesaCreateView.as_view(), name='nova_mesa'),
]

urlpatterns += htmx_urlpatterns

