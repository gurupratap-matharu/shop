import logging

import braintree
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from orders.models import Order

logger = logging.getLogger(__name__)
gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)


def payment_process(request):
    logger.info("processing payment...")

    order_id = request.session.get("order_id")
    order = get_object_or_404(Order, id=order_id)
    total_cost = order.get_total_cost()

    if request.method == "POST":
        # retrieve nonce
        nonce = request.POST.get("payment_method_nonce", None)

        logger.info("Received Nonce from braintree: %s", nonce)
        logger.info("Generating sale hold on...")

        # create and submit transaction
        result = gateway.transaction.sale(
            {
                "amount": f"{total_cost: .2f}",
                "payment_method_nonce": nonce,
                "options": {"submit_for_settlement": True},
            }
        )

        if result.is_success:
            logger.info("Payment received !!!")
            order.paid = True
            order.braintree_id = result.transaction.id
            order.save()
            return redirect("payment:done")
        else:
            return redirect("payment:canceled")

    else:
        # Get Request, so generate token
        client_token = gateway.client_token.generate()

        return render(
            request,
            "payment/payment_process.html",
            {"order": order, "client_token": client_token},
        )


def payment_done(request):
    logger.info("payment done...")
    return render(request, "payment/payment_done.html")


def payment_canceled(request):
    logger.info("payment canceled...")
    return render(request, "payment/payment_canceled.html")
