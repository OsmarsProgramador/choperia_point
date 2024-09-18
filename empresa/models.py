# empresa/models.py
from django.db import models
from django.core.validators import MinLengthValidator

class Empresa(models.Model):
    nome = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    cnpj = models.CharField(max_length=18, unique=True, validators=[MinLengthValidator(18)])

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


