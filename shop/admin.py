from typing import Sequence

from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields: dict[str, Sequence[str]] = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display: list[str] = [
        "name",
        "slug",
        "price",
        "available",
        "created",
        "updated",
    ]
    list_filter: list[str] = ["available", "created", "updated"]
    list_editable: list[str] = ["price", "available"]
    prepopulated_fields: dict[str, Sequence[str]] = {"slug": ("name",)}
