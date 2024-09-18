# produto/models.py
from django.db import models
from empresa.models import Empresa

class Categoria(models.Model):
    nome = models.CharField(max_length=255)
    # descricao = models.TextField(blank=True, null=True)
    # empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='categorias')

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome_produto = models.CharField(max_length=255)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='produtos')
    descricao = models.TextField(blank=True, null=True)
    custo = models.DecimalField(max_digits=10, decimal_places=2)
    venda = models.DecimalField(max_digits=10, decimal_places=2)
    codigo = models.CharField(max_length=20, unique=True)
    estoque = models.PositiveIntegerField(default=0)
    estoque_total = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to='imagens/', blank=True, null=True)
    # empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='produtos')

    def __str__(self):
        return self.nome_produto

