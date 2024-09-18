# usuario/admin.py
from django.contrib import admin

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo')  # Ajuste para campos reais do modelo Usuario
    list_editable = ('ativo',)  # Ajuste para campos que existem
    readonly_fields = ('user',)  # Se você precisar de algum campo readonly, ajuste aqui # naõ permite que no campoa admin altere, tornando o compo somente para leitura



