
# Register your models here.
from django.contrib import admin

from product import models


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "sku")
    search_fields = ("title",)


@admin.register(models.Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "active")
    search_fields = ("title",)


@admin.register(models.ProductVariantPrice)
class ProductVariantPriceAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "price", "stock")


@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product",)


@admin.register(models.ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "variant_title", "product", "variant")
