# mesa/views.py
import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.generic import ListView, View
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from .models import Mesa, Pedido
from produto.models import Produto
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone

# pip install reportlab - para imprimir comanda
# from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.units import mm


from django.conf import settings
from empresa.models import Empresa

def get_empresa_padrao():
    return Empresa.objects.get(cnpj=settings.DEFAULT_EMPRESA_CNPJ)

class MesaListView(LoginRequiredMixin, ListView):
    model = Mesa
    template_name = 'mesa/list_mesa.html'
    context_object_name = 'mesas'
    paginate_by = 10

    def get_queryset(self):
        # Ordena o queryset antes da paginação
        return Mesa.objects.all().order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['mesas_abertas'] = Mesa.objects.filter(status='Aberta').order_by('nome')
        context['mesas_fechadas'] = Mesa.objects.filter(status='Fechada').order_by('nome')
        
        # Obtém as mesas já existentes no banco de dados
        mesas_existentes = set(Mesa.objects.values_list('nome', flat=True))

        # Gera uma lista de mesas entre 1 e 30 que não estão no banco de dados
        context['mesas_disponiveis'] = [f'{str(i).zfill(2)}' for i in range(1, 31) if f'{str(i).zfill(2)}' not in mesas_existentes]

        # Adiciona o usuário logado ao contexto
        # Não precisamos do modelo Usuario, podemos usar request.user diretamente
        context['usuario_logado'] = self.request.user if self.request.user.is_authenticated else None

        # Chama o método para excluir mesas fechadas fora do intervalo 01-11
        self.excluir_mesas_fechadas()

        return context

    def excluir_mesas_fechadas(self):
        # Exclui mesas fechadas que não estão no intervalo de 01 a 11
        mesas_para_excluir = Mesa.objects.filter(status='Fechada').exclude(nome__in=[f'{str(i).zfill(2)}' for i in range(1, 12)])
        mesas_para_excluir.delete()

class AbrirMesaView(LoginRequiredMixin, View):
    def get(self, request, id_mesa):
        mesa = get_object_or_404(Mesa, id=id_mesa)
        usuarios = User.objects.all()  # Listando todos os usuários

        # Filtrar produtos com estoque maior que 0
        produtos = Produto.objects.filter(estoque__gt=0)

        # Cálculo do total de cada item no pedido e o total geral no backend
        itens_calculados = []
        total_geral = 0       

        # Agora, ao invés de acessar `mesa.itens`, acesse os pedidos relacionados
        pedidos = Pedido.objects.filter(mesa=mesa)

        for pedido in pedidos:
            total_item = pedido.quantidade * pedido.produto.venda
            itens_calculados.append({
                'nome_produto': pedido.produto.nome_produto,
                'quantidade': pedido.quantidade,
                'preco_unitario': pedido.produto.venda,
                'total_item': total_item,
                'categoria': pedido.produto.categoria.nome,
                'codigo': pedido.produto.codigo,
                'estoque': pedido.produto.estoque,
                'estoque_total': pedido.produto.estoque_total,
                'descricao': pedido.produto.descricao,
                'imagem': pedido.produto.imagem.url if pedido.produto.imagem else '',
            })
            total_geral += total_item

        # Obter a data e hora atual
        now = timezone.now()

        # Usando request.user diretamente sem depender do modelo Usuario
        usuario_atual = request.user if request.user.is_authenticated else None

        return render(request, 'mesa/abrir_mesa.html', {
            'mesa': mesa, 
            'usuarios': usuarios, 
            'usuario_atual_nome': usuario_atual,
            'produtos': produtos,            
            'itens_calculados': itens_calculados,  
            'total_geral': total_geral,  
            'now': now,  
        })

from django.db import models
class ExcluirItemView(LoginRequiredMixin, View):
    def post(self, request, id_mesa):
        mesa = get_object_or_404(Mesa, pk=id_mesa)
        item_codigo = request.POST.get('item_codigo')
        quantidade = int(request.POST.get('quantidade', 1))
        item_removido = False

        # Obter o pedido relacionado ao item
        pedido = get_object_or_404(Pedido, mesa=mesa, produto__codigo=item_codigo)
        
        if pedido.quantidade > quantidade:
            pedido.quantidade -= quantidade
            pedido.save()  # Atualiza a quantidade no banco de dados
        else:
            # Se a quantidade é menor ou igual ao pedido, exclui o item
            pedido.delete()
        
        # Atualiza o estoque do produto
        try:
            produto = Produto.objects.get(codigo=item_codigo)
            produto.estoque += quantidade
            produto.save()
        except Produto.DoesNotExist:
            pass

        # Verifica se restam itens na mesa
        total_itens = mesa.pedidos.aggregate(total=models.Sum('quantidade'))['total'] or 0

        if total_itens <= 0:
            # Se não restam itens, reseta o valor_pago e pessoas_pagaram
            mesa.status = 'Fechada'
            mesa.pedido = 0
            mesa.valor_pago = Decimal('0.00')  # Resetar valor pago
            mesa.pessoas_pagaram = 0  # Resetar pessoas pagaram

        mesa.save()

        return redirect('mesa:abrir_mesa', id_mesa=id_mesa)

class CancelarPedidoView(LoginRequiredMixin, View):
    def post(self, request, id_mesa):
        mesa = get_object_or_404(Mesa, pk=id_mesa)
        
        # Percorre todos os pedidos da mesa
        for pedido in mesa.pedidos.all():
            # Atualiza o estoque do produto
            try:
                produto = pedido.produto
                produto.estoque += pedido.quantidade
                produto.save()
            except Produto.DoesNotExist:
                pass
        
        # Excluindo todos os pedidos relacionados à mesa
        mesa.pedidos.all().delete()
        
        # Resetar a mesa
        mesa.status = 'Fechada'
        mesa.pedido = 0
        mesa.valor_pago = Decimal('0.00')  # Resetar valor pago
        mesa.pessoas_pagaram = 0  # Resetar pessoas pagaram
        mesa.save()
        # Redirecionar para a lista de mesas
        return redirect('mesa:list_mesa')

from usuario.forms import PasswordForm

class UpdateUserView(View):
    def post(self, request, pk):
        try:
            # Obtenha a mesa associada
            mesa = get_object_or_404(Mesa, pk=pk)
        except Exception as e:
            print(f"Erro ao obter a mesa: {e}")
            return render(request, 'usuario/login.html', {'error': 'Erro ao obter a mesa.'})

        try:
            # Obtenha o ID do usuário e a senha do POST
            user_id = request.POST.get('usuario')
            password = request.POST.get('password')
            print(f"ID do Usuário Selecionado: {user_id}")
        except Exception as e:
            print(f"Erro ao obter dados do formulário: {e}")
            return render(request, 'usuario/login.html', {'error': 'Erro ao obter dados do formulário.'})

        try:
            # Obtenha o objeto User diretamente pelo ID
            user = get_object_or_404(User, pk=user_id)
            print(f"Usuário relacionado obtido: {user.username}")
        except Exception as e:
            print(f"Erro ao obter o User: {e}")
            return render(request, 'usuario/login.html', {'error': 'Usuário relacionado não encontrado.'})

        try:
            # Tente autenticar o usuário com a senha fornecida
            user_authenticated = authenticate(request, username=user.username, password=password)
            print(f"Nome do usuário para atualização: {user.username}")
        except Exception as e:
            print(f"Erro ao autenticar o usuário: {e}")
            return render(request, 'usuario/login.html', {'error': 'Erro ao autenticar o usuário.'})

        if user_authenticated is not None:
            try:
                # Aqui, o nome do usuário não é alterado no banco de dados, 
                # já que estamos utilizando diretamente o modelo User
                # Você pode atualizar outros campos se necessário, mas no exemplo, não há mudanças
                print(f"Usuário autenticado: {user.username}")
            except Exception as e:
                print(f"Erro ao salvar o User: {e}")
                return render(request, 'usuario/login.html', {'error': 'Erro ao salvar o usuário.'})

            try:
                # Realize o login do usuário autenticado
                login(request, user_authenticated)
                print(f"Usuário logado: {user.username}")
            except Exception as e:
                print(f"Erro ao realizar login: {e}")
                return render(request, 'usuario/login.html', {'error': 'Erro ao realizar login.'})

            # Redireciona para a página com a mesa atualizada
            return redirect('mesa:abrir_mesa', id_mesa=pk)
        else:
            # Se a autenticação falhar, mostre uma mensagem de erro
            print("Falha na autenticação. Senha incorreta.")
            return render(request, 'usuario/login.html', {'error': 'Senha incorreta. Tente novamente.'})

"""
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Modelo usado para uma visão do usuário, não indicado para impressão térmica
class GerarComandaPDFView(LoginRequiredMixin, View):
    def get(self, request, id_mesa):
        mesa = get_object_or_404(Mesa, pk=id_mesa)

        # Configura o response para PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="comanda_{id_mesa}.pdf"'

        # Define o tamanho do papel: 80mm de largura, altura ajustável
        largura = 80 * mm
        altura = 200 * mm  # Ajuste a altura conforme necessário
        p = canvas.Canvas(response, pagesize=(largura, altura))

        # Define a posição inicial para o texto
        y = altura - 10 * mm  # Margem superior

        # Cabeçalho da comanda
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredString(largura / 2.0, y, "[Nome da Loja]")
        y -= 5 * mm
        p.setFont("Helvetica", 8)
        p.drawCentredString(largura / 2.0, y, "[Endereço]")
        y -= 4 * mm
        p.drawCentredString(largura / 2.0, y, "[Telefone]")
        y -= 4 * mm
        p.drawCentredString(largura / 2.0, y, "[CNPJ]")
        y -= 6 * mm
        p.drawString(5 * mm, y, f"Data: {timezone.now().strftime('%d/%m/%Y')}    Hora: {timezone.now().strftime('%H:%M')}")
        y -= 6 * mm

        p.drawString(5 * mm, y, "-" * 32)
        y -= 6 * mm

        # Tabela de itens
        p.setFont("Helvetica-Bold", 8)
        p.drawString(5 * mm, y, "Item")
        p.drawString(40 * mm, y, "Qtde")
        p.drawString(50 * mm, y, "Valor Unit.")
        p.drawString(65 * mm, y, "Total")
        y -= 5 * mm
        p.setFont("Helvetica", 8)
        p.drawString(5 * mm, y, "-" * 32)
        y -= 5 * mm

        # Listar os itens da mesa
        for item in mesa.itens:
            nome_produto = item['nome_produto']
            quantidade = item['quantidade']
            preco_unitario = item['preco_unitario']
            valor_total = quantidade * preco_unitario

            preco_unitario_str = f"R$ {preco_unitario:,.2f}".replace('.', ',')
            valor_total_str = f"R$ {valor_total:,.2f}".replace('.', ',')

            p.drawString(5 * mm, y, nome_produto[:12]) # Limite o nome do produto a 12 caracteres
            p.drawString(43 * mm, y, f"{quantidade}")
            p.drawString(50 * mm, y, f"{preco_unitario_str}")
            p.drawString(65 * mm, y, f"{valor_total_str}")
            y -= 5 * mm

            if y < 10 * mm:  # Evita ultrapassar o final da página
                p.showPage()
                y = altura - 10 * mm

        # Subtotal, Desconto e Total
        subtotal = sum(item['quantidade'] * item['preco_unitario'] for item in mesa.itens)
        desconto = 0  # Ajuste conforme necessário
        total = subtotal - desconto

        p.drawString(5 * mm, y, "-" * 32)
        y -= 6 * mm
        p.drawString(5 * mm, y, f"Subtotal: R$ {subtotal:.2f}")
        y -= 5 * mm
        p.drawString(5 * mm, y, f"Desconto: R$ {desconto:.2f}")
        y -= 5 * mm
        p.drawString(5 * mm, y, f"Total:    R$ {total:.2f}")
        y -= 6 * mm
        p.drawString(5 * mm, y, "-" * 32)
        y -= 6 * mm
        p.drawString(5 * mm, y, "Forma de Pagamento: Dinheiro")
        y -= 6 * mm
        p.drawString(5 * mm, y, "-" * 32)
        y -= 6 * mm

        # Mensagem de agradecimento
        p.setFont("Helvetica-Bold", 10)
        p.drawCentredString(largura / 2.0, y, "Obrigado pela preferência!")

        # Finaliza o PDF
        p.showPage()
        p.save()

        return response

"""
from reportlab.lib.pagesizes import A4
from datetime import datetime  # Adicione esta linha
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle

# Modelo adequado para enviar para uma impreeora térmica
# Fonte Monoespaçada: É necessário garantir que o texto enviado para 
# a impressora esteja formatado para uma fonte monoespaçada (como Courier). 
# Isso alinha corretamente os dados.

# Método que gera a comanda do caixa em PDF
from decimal import Decimal

class GerarComandaPDFView(LoginRequiredMixin, View):
    def get(self, request, id_mesa):
        # Obtenha o usuário autenticado
        user = request.user      
        
        # Obtenha a mesa e a empresa associada
        mesa = get_object_or_404(Mesa, pk=id_mesa)
        empresa = get_empresa_padrao()        

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="comanda_{id_mesa}.pdf"'

        p = canvas.Canvas(response)

        largura = 80 * mm
        altura = 297 * mm  # Tamanho A4 para o exemplo, ajustar conforme a necessidade

        # Fonte monoespaçada
        p.setFont("Courier", 10)

        # Cabeçalho
        p.drawString(5, altura - 20, "------------------------------")
        p.drawString(5, altura - 30, empresa.nome)
        p.drawString(5, altura - 40, empresa.endereco)
        p.drawString(5, altura - 50, f"CNPJ: {empresa.cnpj}")
        p.drawString(5, altura - 60, f"Telefone: {empresa.telefone}")
        p.drawString(5, altura - 70, "------------------------------")

        # Exibindo a Mesa e Funcionário
        p.drawString(5, altura - 80, f"Mesa: {mesa.nome}")
        p.drawString(5, altura - 90, f"Funcionário: {user.username}")  # Usando o nome do usuário autenticado
        p.drawString(5, altura - 100, "------------------------------")
        
        # Data e Hora
        p.drawString(5, altura - 120, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
        p.drawString(5, altura - 130, f"Hora: {datetime.now().strftime('%H:%M:%S')}")
        p.drawString(5, altura - 140, "------------------------------")

        # Cabeçalho da Tabela
        p.drawString(5, altura - 150, "Item        Qtde  Unit   Total")
        p.drawString(5, altura - 160, "------------------------------")

        y = altura - 170
        total = Decimal(0)  # Certifique-se de usar Decimal para cálculos financeiros

        # Itens (acessar os pedidos relacionados)
        for pedido in mesa.pedidos.all():
            nome = pedido.produto.nome_produto
            quantidade = str(pedido.quantidade).rjust(4)
            preco_unitario = pedido.produto.venda
            preco_total = pedido.quantidade * pedido.produto.venda
            total += Decimal(preco_total)  # Certifique-se de que o total seja Decimal
            preco_unitario_str = f"{preco_unitario:,.2f}".replace('.', ',').rjust(6)
            preco_total_str = f"{preco_total:,.2f}".replace('.', ',').rjust(7)

            # Quebra o nome em múltiplas linhas se necessário
            linhas_nome = [nome[i:i+10] for i in range(0, len(nome), 10)]

            for linha in linhas_nome:
                p.drawString(5, y, f"{linha.ljust(10)} {quantidade} {preco_unitario_str} {preco_total_str}")
                y -= 10
                quantidade = ""
                preco_unitario_str = ""
                preco_total_str = ""

        p.drawString(5, y, "------------------------------")
        y -= 10

        # Subtotal e Total
        p.drawString(5, y, f"Subtotal:           R$ {total:.2f}".replace('.', ','))
        y -= 10

        # Exemplo de desconto
        desconto = Decimal(0.00)  # Certifique-se de que o desconto também seja Decimal
        p.drawString(5, y, f"Desconto:           R$ {desconto:.2f}".replace('.', ','))
        y -= 10

        # Calcula o total final após o desconto
        total_final = total - desconto  # Ambos são Decimal agora
        p.drawString(5, y, f"Total:              R$ {total_final:.2f}".replace('.', ','))
        y -= 10

        p.drawString(5, y, "------------------------------")
        y -= 10

        # Forma de Pagamento
        p.drawString(5, y, "Forma de Pagamento: Dinheiro")
        y -= 20

        # Agradecimento
        p.drawCentredString(largura / 2, y, "Obrigado pela preferência!")
        p.showPage()
        p.save()

        # Gera a comanda PDF e envia para a impressora da cozinha
        self.enviar_para_cozinha(request, mesa.id)

        return response

    def enviar_para_cozinha(self, request, id_mesa):
        response = EnviarParaCozinhaView().post(request, id_mesa)
        return response
    
    
from escpos.printer import Network
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Mesa
from datetime import datetime

"""class EnviarParaCozinhaView(View): # Envia via ip
    def post(self, request, id_mesa):
        mesa = get_object_or_404(Mesa, pk=id_mesa)
        
        try:
            # Conecte-se à impressora via IP
            impressora = Network("192.168.0.100")  # IP da impressora de cozinha
            
            # Cabeçalho do Pedido
            impressora.set(align='center', bold=True)
            impressora.text("Pedido de Cozinha\n")
            impressora.text(f"Mesa: {mesa.nome}\n")
            impressora.text(f"Data: {datetime.now().strftime('%d/%m/%Y')}\n")
            impressora.text(f"Hora: {datetime.now().strftime('%H:%M:%S')}\n")
            impressora.text("-----------------------------\n")
            
            # Itens do Pedido
            impressora.set(align='left', bold=False)
            for item in mesa.itens:
                impressora.text(f"{item['nome_produto']}\n")
                impressora.text(f"Quantidade: {item['quantidade']}\n")
                if 'descricao' in item:
                    impressora.text(f"Descrição: {item['descricao']}\n")
                impressora.text("-----------------------------\n")

            # Finalizar o Pedido
            impressora.set(align='center', bold=True)
            impressora.text("----- FIM DO PEDIDO -----\n")
            impressora.cut()  # Comando para cortar o papel
            
            impressora.close()
            return HttpResponse("Pedido enviado para a cozinha com sucesso!")
        
        except Exception as e:
            return HttpResponse(f"Erro ao enviar para a cozinha: {str(e)}", status=500)"""

class EnviarParaCozinhaView(View): # Envia via arquivo txt
    def post(self, request, id_mesa):
        mesa = get_object_or_404(Mesa, pk=id_mesa)
        pedidos = mesa.pedidos.all()  # Acessa os pedidos relacionados à mesa

        itens_calculados = [
            {
                'nome_produto': pedido.produto.nome_produto,
                'quantidade': pedido.quantidade,
                'descricao': pedido.produto.descricao if hasattr(pedido.produto, 'descricao') else 'N/A'
            }
            for pedido in pedidos
        ]

        # Simulação de impressão em arquivo
        try:
            caminho_arquivo = os.path.join(os.path.dirname(__file__), "saida_cozinha.txt")
            with open(caminho_arquivo, "w") as file:
                file.write("---- COMANDA DE COZINHA ----\n")
                file.write(f"Mesa: {mesa.nome}  Pedido: {mesa.pedido}\n")
                file.write(f"Data: {datetime.now().strftime('%d/%m/%Y')}\n")
                file.write(f"Hora: {datetime.now().strftime('%H:%M:%S')}\n")
                file.write("-----------------------------\n")
                for item in itens_calculados:
                    file.write(f"{item['nome_produto']} - {item['quantidade']}\n")
                    file.write(f"Descrição: {item['descricao']}\n")
                file.write("-----------------------------\n")
                file.write("Preparar com atenção!\n")

        except Exception as e:
            return HttpResponse(f"Erro ao enviar para a cozinha: {str(e)}", status=500)

        return HttpResponse("Comanda enviada para a cozinha (simulada).")

class RealizarPagamentoView(LoginRequiredMixin, View):
    def get(self, request, id_mesa):
        mesa = get_object_or_404(Mesa, id=id_mesa)
        usuarios = User.objects.all()  # Listando todos os usuários

        # Filtrar produtos com estoque maior que 0
        produtos = Produto.objects.filter(estoque__gt=0)

        # Cálculo do total de cada item no pedido e o total geral no backend
        itens_calculados = []
        total_geral = 0       

        # Agora, ao invés de acessar `mesa.itens`, acesse os pedidos relacionados
        pedidos = Pedido.objects.filter(mesa=mesa)

        for pedido in pedidos:
            total_item = pedido.quantidade * pedido.produto.venda
            itens_calculados.append({
                'nome_produto': pedido.produto.nome_produto,
                'quantidade': pedido.quantidade,
                'preco_unitario': pedido.produto.venda,
                'total_item': total_item,
                'categoria': pedido.produto.categoria.nome,
                'codigo': pedido.produto.codigo,
                'estoque': pedido.produto.estoque,
                'estoque_total': pedido.produto.estoque_total,
                'descricao': pedido.produto.descricao,
                'imagem': pedido.produto.imagem.url if pedido.produto.imagem else '',
            })
            total_geral += total_item

        # Obter a data e hora atual
        now = timezone.now()

        # Calcular valor faltante
        faltante = total_geral - mesa.valor_pago

        # Usando request.user diretamente sem depender do modelo Usuario
        usuario_atual = request.user if request.user.is_authenticated else None

        return render(request, 'mesa/realizar_pagamento.html', {
            'mesa': mesa, 
            'usuarios': usuarios, 
            'usuario_atual_nome': usuario_atual,
            'produtos': produtos,            
            'itens_calculados': itens_calculados,  
            'total_geral': total_geral,  
            'faltante': total_geral,  # Passando o valor faltante para o template
            'now': now,  
        })

from django.http import JsonResponse
from estoque.models import Estoque

class PagamentoPorPessoaView(LoginRequiredMixin, View):
    def get(self, request, id_mesa):
        mesa = get_object_or_404(Mesa, id=id_mesa)
        forma_pagamento = request.GET.get('forma')
        total_geral = mesa.calcular_total()
        pessoas = int(request.GET.get('pessoas', 1))
        
        # Divisão da conta por pessoa
        total_por_pessoa = total_geral / pessoas
        faltante = total_geral - mesa.valor_pago  # Valor que ainda precisa ser pago

        return render(request, 'mesa/pagamento_por_pessoa.html', {
            'mesa': mesa,
            'total_por_pessoa': total_por_pessoa,
            'faltante': faltante,
            'pessoas_restantes': pessoas - mesa.pessoas_pagaram,
            'forma_pagamento': forma_pagamento,
        })

    def post(self, request, id_mesa):
        mesa = get_object_or_404(Mesa, id=id_mesa)
        valor_pago = Decimal(request.POST.get('valor_pago'))  # Convertendo para Decimal
        mesa.valor_pago += valor_pago
        mesa.pessoas_pagaram += 1  # Atualizar o número de pessoas que pagaram

        # Verificar se o total foi pago
        total_geral = mesa.calcular_total()
        faltante = total_geral - mesa.valor_pago

        if faltante <= 0:
            # Registrar saída no estoque para todos os produtos do pedido
            for pedido in mesa.pedidos.all():
                try:
                    Estoque.objects.create(
                        empresa=get_empresa_padrao(),  # Assumindo que a mesa tem um campo 'empresa'
                        produto=pedido.produto,
                        quantidade=pedido.quantidade,
                        tipo='saida',
                        data=timezone.now()
                    )
                except Exception as e:
                    print(f"Erro ao registrar saída no estoque: {e}")
            
            # Excluir todos os pedidos relacionados à mesa
            mesa.pedidos.all().delete()
            
            # Fechar a mesa e resetar valores
            mesa.status = 'Fechada'
            mesa.pedido = 0
            mesa.valor_pago = Decimal('0.00')
            mesa.pessoas_pagaram = 0
            mesa.save()

            return JsonResponse({'status': 'concluido'})
        else:
            mesa.save()
            return JsonResponse({
                'status': 'parcial',
                'valor_pago': float(mesa.valor_pago),
                'faltante': float(faltante)
            })


        """# Se todos tiverem pago, redireciona para uma página de confirmação
        if mesa.pessoas_pagaram >= mesa.numero_pessoas:
            return redirect('mesa:confirmacao_pagamento', id_mesa=mesa.id)

        return redirect('mesa:pagamento_pessoa', id_mesa=mesa.id)"""

class ConfirmacaoPagamentoView(LoginRequiredMixin, View):
    def get(self, request, id_mesa):
        mesa = get_object_or_404(Mesa, id=id_mesa)
        return render(request, 'mesa/confirmacao_pagamento.html', {'mesa': mesa})

    def post(self, request, id_mesa):
        mesa = get_object_or_404(Mesa, pk=id_mesa)
        desconto = float(request.POST.get('desconto', 0))
        divisao = int(request.POST.get('divisao', 1))

        total = mesa.calcular_total() - desconto
        total_por_pessoa = total / divisao

        # Processar o pagamento...

        return render(request, 'mesa/pagamento_confirmacao.html', {
            'mesa': mesa,
            'total': total,
            'total_por_pessoa': total_por_pessoa,
            'divisao': divisao,
            'desconto': desconto
        })
    
class GerarReciboPDFView(LoginRequiredMixin, View):
    def get(self, request, id_mesa):
        mesa = get_object_or_404(Mesa, pk=id_mesa)
        total = mesa.calcular_total()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="recibo_{id_mesa}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)

        p.setFont("Courier", 10)
        p.drawString(100, 800, f"Recibo - Mesa {mesa.nome}")
        p.drawString(100, 780, f"Total: R$ {total:.2f}")

        p.showPage()
        p.save()

        return response





