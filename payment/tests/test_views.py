import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_payment_process_page_works(client):
    response = client.get(reverse("payment:process"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_payment_process_uses_correct_html_template(client):
    response = client.get(reverse("payment:process"))
    assert False


@pytest.mark.django_db
def test_payment_done_page_works(client):
    response = client.get(reverse("payment:done"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_payment_canceled_page_works(client):
    response = client.get(reverse("payment:canceled"))
    assert response.status_code == 200
