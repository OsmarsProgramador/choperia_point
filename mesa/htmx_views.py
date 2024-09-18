# mesa/htmx_views.py
from django.contrib import messages
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from .models import Mesa, Pedido
from .forms import MesaForm
from produto.models import Produto

from django.utils import timezone

# TODO: Sempre que um modal que adiciona produto a mesa for fechado ele deve 
# ter os dados incicial sem quantidade > 1. Isso deve ser feito no template abrir_mesa 

""" implementar a lógica para adicionar produtos à mesa, considerando a manipulação do estoque e a atualização da lista de itens da mesa. """   
class AdicionarItemView(View):
    def post(self, request, id_mesa, produto_id):
        mesa = get_object_or_404(Mesa, pk=id_mesa)
        produto = get_object_or_404(Produto, pk=produto_id)

        # Captura a quantidade do POST
        quantidade = int(request.POST.get('quantidade', 1))
        print(f'Quantidade enviada: {quantidade}')
        print(f'Estoque: {produto.estoque}')
        if produto.estoque >= quantidade:
            produto.estoque -= quantidade
            produto.save()

            # Verifica se já existe um pedido para este produto na mesa
            try:
                # Tenta buscar um pedido existente
                pedido = Pedido.objects.get(mesa=mesa, produto=produto)
                pedido.quantidade += quantidade  # Atualiza a quantidade
            except Pedido.DoesNotExist:
                # Se não houver pedido, crie um novo sem salvar ainda
                pedido = Pedido(mesa=mesa, produto=produto, quantidade=quantidade)
            
            # Agora podemos salvar o pedido com a quantidade correta
            pedido.save()

            # Numera o pedido em andamento de uma mesa
            mesa.status = 'Aberta'
            if mesa.pedido == 0:
                ultimo_pedido = Mesa.objects.order_by('-pedido').first()
                mesa.pedido = (ultimo_pedido.pedido + 1) if ultimo_pedido else 1
            mesa.save()

            """# Cálculo do total
            total_geral = mesa.calcular_total()"""

            # Cálculo do total
            total_geral = 0
            itens_calculados = []
            
            # Obter todos os pedidos relacionados à mesa
            pedidos = Pedido.objects.filter(mesa=mesa)
            for p in pedidos:
                total_item = p.quantidade * p.produto.venda
                itens_calculados.append({
                    'nome_produto': p.produto.nome_produto,
                    'quantidade': p.quantidade,
                    'preco_unitario': p.produto.venda,
                    'total_item': total_item,
                    'codigo': p.produto.codigo
                })
                total_geral += total_item

            # Obter a data e hora atual
            now = timezone.now()

            # Verificar se o estoque do produto zerou
            if produto.estoque == 0 and request.headers.get('HX-Request'):
                messages.warning(request, f'O produto "{produto.nome_produto}" está esgotado no estoque.')
                # Se o estoque zerar e a requisição for HTMX, forçar um redirecionamento completo
                response = HttpResponse(status=204)  # Resposta vazia para HTMX
                response['HX-Redirect'] = reverse('mesa:abrir_mesa', kwargs={'id_mesa': id_mesa})
                return response

            # Se a requisição for via HTMX, renderizar apenas o componente parcial
            if request.headers.get('HX-Request'):
                return render(request, 'mesa/partials/htmx_componentes/item_list.html', {
                    'mesa': mesa,
                    'itens_calculados': itens_calculados,  # Enviar itens calculados
                    'total_geral': total_geral,  # Enviar o total geral para o template
                })

            # Se não for via HTMX, redirecionar normalmente
            return redirect('mesa:abrir_mesa', id_mesa=id_mesa)

        else:
            if request.headers.get('HX-Request'):
                messages.warning(request, f'O produto "{produto.nome_produto}" está esgotado no estoque.')
                # Se o estoque zerar e a requisição for HTMX, forçar um redirecionamento completo
                response = HttpResponse(status=204)  # Resposta vazia para HTMX
                response['HX-Redirect'] = reverse('mesa:abrir_mesa', kwargs={'id_mesa': id_mesa})
                return response
            # Se o estoque não for suficiente, recarregar a página inteira
            return redirect('mesa:abrir_mesa', id_mesa=id_mesa)

class MesaCreateView(CreateView):
    model = Mesa
    form_class = MesaForm
    success_url = reverse_lazy('mesa:list_mesa')  # Não será mais necessário, já que redirecionaremos para a view de abrir mesa.

    def post(self, request, *args, **kwargs):
        nome_mesa = request.POST.get('nome')

        if nome_mesa:
            # Verifica se o nome da mesa é numérico (Nova Mesa Numerada)
            if nome_mesa.isdigit():
                mesa_nome = f'{nome_mesa}'
            else:
                # Caso contrário, trata como nome de pessoa (Pedido no Balcão)
                mesa_nome = nome_mesa

            # Cria a nova mesa com o nome ou número fornecido
            nova_mesa = Mesa.objects.create(nome=mesa_nome, status='Fechada')
            nova_mesa.save()

            # Redireciona para a tela de inserção de itens da mesa recém-criada
            return redirect('mesa:abrir_mesa', id_mesa=nova_mesa.id)

        # Caso o nome da mesa não seja fornecido, retorna um erro
        return JsonResponse({'error': 'Nome da mesa não fornecido'}, status=400)


