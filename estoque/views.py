# estoque/views.py
from django.views.generic import ListView, CreateView
from .models import Estoque
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class EstoqueListView(LoginRequiredMixin, ListView):
    model = Estoque
    template_name = 'estoque/estoque_list.html'
    context_object_name = 'estoques'
    paginate_by = 10

class EstoqueCreateView(LoginRequiredMixin, CreateView):
    model = Estoque
    fields = '__all__'
    template_name = 'estoque/estoque_form.html'
    success_url = reverse_lazy('estoque:estoque_list')

