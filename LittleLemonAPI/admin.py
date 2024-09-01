from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user',  'menuitem']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','user','delivery_crew','status']

@admin.register(OrderItem)
class OrderItem(admin.ModelAdmin):
    order_id = OrderItem.id
    list_display = ['id', 'order_id', 'order', 'menuitem']