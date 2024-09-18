from django.contrib import admin
from .models import Empresa

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['nome']  
    list_filter = ['nome']  
    search_fields = ['nome']