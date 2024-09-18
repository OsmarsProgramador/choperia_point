# mesa/forms.py
from django import forms
from .models import Mesa
from produto.models import Produto
from .models import Pedido

class MesaForm(forms.ModelForm):
    """Simplesmente manipula os dados da mesa, sem lidar diretamente com os produtos. 
    Os campos principais são nome, status, pedido e usuario."""
    class Meta:
        model = Mesa
        # fields = ['nome']
        fields = ['nome', 'status', 'pedido', 'usuario', 'empresa']  # O campo 'produtos' é gerenciado via 'Pedido', então não é incluído aqui.

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if nome.isdigit():
            nome = str(nome).zfill(2)
        if Mesa.objects.filter(nome=nome).exists():
            raise forms.ValidationError("Já existe uma mesa com este nome.")
        return nome

class AdicionarItemForm(forms.ModelForm):
    """Este formulário lida com a adição de produtos à mesa. 
    Ele usa o modelo Pedido para vincular a mesa com os produtos e a quantidade de cada produto.
    O campo produto é filtrado para exibir apenas produtos com estoque disponível (estoque > 0)."""
    class Meta:
        model = Pedido
        fields = ['produto', 'quantidade']  # O campo 'mesa' é definido pela view e não precisa estar no formulário
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produto'].queryset = Produto.objects.filter(estoque__gt=0)  # Apenas produtos com estoque disponível





