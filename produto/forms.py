# produto/forms.py
from django import forms
from .models import Produto

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome_produto', 'categoria', 'descricao', 'custo', 'venda', 'codigo', 'estoque', 'estoque_total', 'imagem']
        widgets = {
            'custo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'venda': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            # outros widgets...
        }

from .models import Categoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']

     
        