import logging
from typing import Any, Dict

from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.edit import FormView

from cart.cart import Cart

from .forms import OrderCreateForm
from .models import OrderItem
from .tasks import send_order_creation_mail

logger = logging.getLogger(__name__)


class OrderCreateView(FormView):
    form_class = OrderCreateForm
    template_name = "orders/order_form.html"

    def form_valid(self, form):
        logger.info("Order form is valid :)")
        order = form.save()
        cart = Cart(self.request)

        # Think of putting this Orderline creation as a method in the Order model. View should not handle it
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                price=item["price"],
                quantity=item["quantity"],
            )

        cart.clear()

        # Send email asynchronously using celery
        send_order_creation_mail.delay(order.id)

        # Set the order_id in the session
        self.request.session["order_id"] = order.id # TODO WHY DO WE DO THIS?

        # Redirect for payment
        return redirect(reverse("payment:process"))

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart(self.request)
        return context
