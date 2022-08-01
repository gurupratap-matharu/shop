from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CouponApplyForm
from .models import Coupon


@require_POST
def coupon_apply(request):
    """
    View that allows users to apply coupon code to a shopping cart to get a discount.
    """

    # 1 Get coupon code from post data and retrieve coupon object from database
    # 2 Check if coupon is valid
    # 3 If yes apply discount to total cart price, notify user and redirect
    # 4 else notify user of invalid coupon and redirect

    now = timezone.now()

    form = CouponApplyForm(request.POST)

    if form.is_valid():
        code = form.cleaned_data["code"]

        try:
            coupon = Coupon.objects.get(
                code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True
            )
            request.session["coupon_id"] = coupon.id

        except Coupon.DoesNotExist:
            request.session["coupon_id"] = None

    return redirect("cart:cart_detail")
