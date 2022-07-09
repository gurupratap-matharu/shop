import pytest


@pytest.mark.django_db
def test_homepage_works(client):
    response = client.get("/")
    assert response.status_code == 200
