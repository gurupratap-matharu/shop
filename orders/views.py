import logging
from typing import Any, Dict

import weasyprint
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic.edit import FormView

from cart.cart import Cart

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .tasks import send_order_creation_mail

logger = logging.getLogger(__name__)


class OrderCreateView(FormView):
    form_class = OrderCreateForm
    template_name = "orders/order_form.html"

    def form_valid(self, form):
        logger.info("Order form is valid :)")
        order = form.save()  # type: ignore
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
        self.request.session["order_id"] = order.id  # TODO WHY DO WE DO THIS?

        # Redirect for payment
        return redirect(reverse("payment:process"))

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart(self.request)
        return context


@staff_member_required
def admin_order_detail(request, order_id):
    """
    Custom django admin view to see the detail of any order. This view is meant to be
    used by staff members.
    """

    order = get_object_or_404(Order, id=order_id)
    return render(request, "admin/orders/order_detail.html", {"order": order})


@staff_member_required
def admin_order_pdf(request, order_id):
    """
    Custom django admin view that generates a PDF for a single order. This view is meant
    to be used by staff members.
    """

    order = get_object_or_404(Order, id=order_id)
    html = render_to_string("orders/order_pdf.html", {"order": order})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=order_{order.id}.pdf"  # type: ignore

    weasyprint.HTML(string=html).write_pdf(
        response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + "css/pdf.css")]
    )

    return response
