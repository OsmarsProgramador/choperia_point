# core/views.py

from django.views.generic import TemplateView  # TemplateView funciona só para renderizar
from django.contrib.auth.mixins import LoginRequiredMixin  # Serve para verificar se um usuario está logado

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

