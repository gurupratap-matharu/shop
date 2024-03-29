from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from coupons.forms import CouponApplyForm
from shop.models import Product
from shop.recommender import Recommender

from .cart import Cart
from .forms import CartAddProductForm


def cart_detail(request):
    """Displays the contents of the cart."""

    cart = Cart(request)

    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override": True}
        )
    coupon_apply_form = CouponApplyForm()

    cart_products = [item["product"] for item in cart]

    r = Recommender()
    recommended_products = r.suggest_products_for(cart_products, max_results=4)

    return render(
        request=request,
        template_name="cart/cart_detail.html",
        context={
            "cart": cart,
            "coupon_apply_form": coupon_apply_form,
            "recommended_products": recommended_products,
        },
    )


@require_POST
def cart_add(request, product_id):
    """Add a product to the cart."""

    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product, quantity=cd["quantity"], override_quantity=cd["override"]
        )
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    """Remove a product from the cart."""

    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart:cart_detail")
