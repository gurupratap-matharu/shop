from typing import Optional

from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import Category, Product


class ProductList(ListView):
    model = Product
    context_object_name: Optional[str] = 'product_list'
    paginate_by: int = 9
    template_name: str = 'shop/product_list.html'


class ProductDetail(DetailView):
    model = Product
    context_object_name: Optional[str] = 'product'
    template_name: str = 'shop/product_detail.html'
