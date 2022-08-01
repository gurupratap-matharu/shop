from io import BytesIO

import weasyprint
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from orders.models import Order


@shared_task
def payment_completed(order_id):
    """
    Task to send a PDF invoice of the order via e-mail when the payment is successfully completed.
    """

    # 1 Get Order detail
    order = Order.objects.get(id=order_id)

    # 2 Generate Email object
    subject = f"My Shop - EE invoice no. {order.id}"
    message = "Please, find attached the invoice for your recent purchase."
    email = EmailMessage(subject, message, settings.COMPANY_EMAIL, [order.email])

    # 3 Create pdf doc using weasy print
    out = BytesIO()
    html = render_to_string("orders/order_pdf.html", {"order": order})
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT / "css/pdf.css")]

    weasyprint.HTML(string=html).write_pdf(out, stylesheets)

    # 4 Attach pdf to email object
    email.attach(
        filename=f"order_{order.id}.pdf",
        content=out.getvalue(),
        mimetype="application/pdf",
    )

    # 5 Send email
    email.send()
