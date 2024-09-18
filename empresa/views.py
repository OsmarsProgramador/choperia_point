# empresa/views.py
from django.views.generic import ListView, DetailView
from .models import Empresa, NotaFiscal
from django.contrib.auth.mixins import LoginRequiredMixin

class EmpresaListView(LoginRequiredMixin, ListView):
    model = Empresa
    template_name = 'empresa/empresa_list.html'
    context_object_name = 'empresas'
    paginate_by = 10

    def get_queryset(self): # garantir que os objetos sejam ordenados antes de serem paginados.
        return Empresa.objects.all().order_by('nome')

class EmpresaDetailView(LoginRequiredMixin, DetailView):
    model = Empresa
    template_name = 'empresa/empresa_detail.html'
    context_object_name = 'empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notas'] = NotaFiscal.objects.filter(empresa=self.get_object())
        return context

