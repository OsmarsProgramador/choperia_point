# mesa/models.py
from decimal import Decimal
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from produto.models import Produto
from empresa.models import Empresa
from django.conf import settings

def get_empresa_padrao():
    return Empresa.objects.get(cnpj=settings.DEFAULT_EMPRESA_CNPJ)

class Mesa(models.Model):
    nome = models.CharField(max_length=50)
    status = models.CharField(max_length=10, default='Fechada')
    pedido = models.PositiveIntegerField(default=0)
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    produtos = models.ManyToManyField(Produto, through='Pedido')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='mesas', default=get_empresa_padrao)  # Define a empresa padrão

    # Para o caso de haver divião de pessoa e para armazenar o valor já pago e o número de pessoas que pagaram
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    pessoas_pagaram = models.IntegerField(default=0)
    # Para controlar o valor que falta ser pago
    # faltante = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    numero_pessoas = models.IntegerField(default=1)  # O número de pessoas que vão dividir o pagamento

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse('mesa:abrir_mesa', args=[self.id])

    def calcular_total(self):
        total = 0
        # Iterar sobre os pedidos relacionados à mesa para calcular o total
        for pedido in self.pedidos.all():  # Usar o related_name 'pedidos' definido na classe Pedido
            total += pedido.quantidade * pedido.produto.venda  # Quantidade * preço de venda do produto
        return total

class Pedido(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='pedidos')  # Adicione related_name
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Mesa {self.mesa.nome})"


