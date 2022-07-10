import logging

import braintree
from django.conf import settings
from django.shortcuts import render

logger = logging.getLogger(__name__)
gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)


def payment_process(request):
    logger.info("processing payment...")
    return render(request, "payment/payment_process.html")


def payment_done(request):
    logger.info("payment done...")
    return render(request, "payment/payment_done.html")


def payment_canceled(request):
    logger.info("payment canceled...")
    return render(request, "payment/payment_canceled.html")
