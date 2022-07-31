import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Order, OrderItem


def export_to_csv(modeladmin, request, queryset):
    """Custom OrderAdmin action to export selected orders to a CSV file."""

    opts = modeladmin.model._meta
    content_disposition = f"attachment; filename={opts.verbose_name_plural}.csv"

    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]

    header_row = [field.verbose_name for field in fields]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition

    writer = csv.writer(response)
    writer.writerow(header_row)

    for obj in queryset:
        data_row = []

        for field in fields:
            value = getattr(obj, field.name)

            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")

            data_row.append(value)

        writer.writerow(data_row)

    return response


export_to_csv.short_description = "Export to CSV"


def order_detail(obj):
    """Returns the custom admin order detail page link"""

    url = reverse("orders:admin_order_detail", args=[obj.id])
    return mark_safe(f"<a href='{url}'>View</a>")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "first_name",
        "last_name",
        "email",
        "address",
        "postal_code",
        "city",
        "paid",
        "created",
        "updated",
        order_detail,
    ]
    list_filter = ["paid", "created", "updated"]
    inlines = [OrderItemInline]
    actions = [export_to_csv]  # type: ignore
