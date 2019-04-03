from django.contrib import admin

from ecomapp.models import Category, Brand, Product, CartItem, Cart, Order, MiddlwareNotification, Cupon

# Register your models here.
admin.site.register(Category)
admin.site.register(Brand)
# admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(MiddlwareNotification)
admin.site.register(Cupon)


def make_available(modeladmin, request, queryset):
    queryset.update(available=True)
    make_available.short_description = ("Set available and notify all subscribers")

    MiddlwareNotification.notify_all_subs()


class ProductAdmin(admin.ModelAdmin):
    actions = [make_available, ]


admin.site.register(Product, ProductAdmin)
