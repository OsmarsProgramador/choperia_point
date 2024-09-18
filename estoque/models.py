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

