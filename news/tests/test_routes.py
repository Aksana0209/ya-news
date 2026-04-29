from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (lf('home_url'), lf('client'), HTTPStatus.OK),
        (lf('detail_url'), lf('client'), HTTPStatus.OK),
        (lf('login_url'), lf('client'), HTTPStatus.OK),
        (lf('signup_url'), lf('client'), HTTPStatus.OK),
        (lf('edit_url'), lf('author_client'), HTTPStatus.OK),
        (lf('edit_url'), lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('delete_url'), lf('author_client'), HTTPStatus.OK),
        (lf('delete_url'), lf('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability(url, parametrized_client, expected_status):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


def test_logout_availability_for_anonymous_user(client, logout_url):
    response = client.post(logout_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (lf('edit_url'), lf('delete_url')),
)
def test_redirect_for_anonymous_user(client, url, login_url):
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
