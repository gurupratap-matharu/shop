from typing import Optional

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Category, Product


class ProductList(ListView):
    model = Product
    context_object_name: Optional[str] = 'products'
    paginate_by: int = 9
    template_name: str = 'shop/product_list.html'

    def get_queryset(self):
        products = Product.objects.filter(available=True)
        categories = Category.objects.all()
        category_slug = self.kwargs.get('category_slug')

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
            self.extra_context = {'category': category, 'categories': categories}

        return products


class ProductDetail(DetailView):
    model = Product
    context_object_name: Optional[str] = 'product'
    template_name: str = 'shop/product_detail.html'

    def get_object(self, queryset=None):
        product = get_object_or_404(Product, id=self.kwargs['id'], slug=self.kwargs['category_slug'], available=True)
        return product
