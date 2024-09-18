from django.contrib import admin
from .models import Mesa, Pedido  # Certifique-se de importar os modelos corretos

class MesaAdmin(admin.ModelAdmin):
    # O campo 'nome' deve existir em 'Mesa', que parece estar correto.
    list_display = ['nome', 'status', 'pedido', 'usuario']  # Use os campos existentes em 'Mesa'
    list_filter = ['status', 'usuario']  # Certifique-se de que os campos referenciados estão corretos

class PedidoAdmin(admin.ModelAdmin):
    list_display = ['mesa', 'produto', 'quantidade']
    list_filter = ['mesa', 'produto']

# Registre os modelos no Django Admin
admin.site.register(Mesa, MesaAdmin)
admin.site.register(Pedido, PedidoAdmin)

