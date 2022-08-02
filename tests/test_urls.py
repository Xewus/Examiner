import pytest
from django.http import HttpResponse
from django.test.client import Client
from django.urls import reverse

FREE_URLS = {
    'INDEX': reverse('questions:index'),
    'RATING': reverse('questions:rating')
}

ONLY_AUTHTORIZATED_URLS = {
    'RESULTS': reverse('questions:my_results'),
}

REDIRECT_WITHOUT_RESULTS_URLS = {
    'QUESTIONS': reverse('questions:questions'),
    'FINISH': reverse('questions:finish_test')
}


def test_404(client: Client):
    response: HttpResponse = client.get('/answer/')
    assert response.status_code == 404


@pytest.mark.django_db
def test_free_urls(client: Client):
    for name, url in FREE_URLS.items():
        response: HttpResponse = client.get(url)
        assert response.status_code == 200, name


@pytest.mark.django_db
def test_non_authtorizated_urls(client: Client):
    for name, url in ONLY_AUTHTORIZATED_URLS.items():
        response: HttpResponse = client.get(url)
        assert response.status_code == 302, name


@pytest.mark.django_db
def test_for_authtorizated_urls(admin_client: Client):
    for name, url in ONLY_AUTHTORIZATED_URLS.items():
        response: HttpResponse = admin_client.get(url)
        assert response.status_code == 200, name


@pytest.mark.django_db
def test_redirect_urls(admin_client: Client):
    for name, url in REDIRECT_WITHOUT_RESULTS_URLS.items():
        response: HttpResponse = admin_client.get(url)
        assert response.status_code == 302, name
