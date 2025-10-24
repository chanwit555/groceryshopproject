from django.contrib import admin
from .models import Product, Sale, SaleItem
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','category','price','stock','updated_at')
    list_filter = ('category',)
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    readonly_fields = ('product','price','quantity')
    can_delete = False
    extra = 0
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id','cashier','total','payment_method','timestamp')
    inlines = [SaleItemInline]
