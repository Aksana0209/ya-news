from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Новый текст'}


def test_anonymous_user_cant_create_comment(client, detail_url):
    initial_count = Comment.objects.count()
    client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == initial_count


def test_user_can_create_comment(author_client, author, news, detail_url):
    Comment.objects.all().delete()
    response = author_client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_use_bad_words(author_client, detail_url):
    initial_count = Comment.objects.count()
    bad_data = {'text': f'Текст, {BAD_WORDS[0]}'}
    response = author_client.post(detail_url, data=bad_data)
    assert Comment.objects.count() == initial_count
    assertFormError(
        response.context['form'],
        'text',
        WARNING
    )


def test_author_can_delete_comment(author_client, delete_url, detail_url):
    initial_count = Comment.objects.count()
    response = author_client.post(delete_url)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == initial_count - 1


def test_author_can_edit_comment(author_client, comment, edit_url, detail_url):
    author_client.post(edit_url, data=FORM_DATA)
    updated = Comment.objects.get(pk=comment.pk)
    assert updated.text == FORM_DATA['text']
    assert updated.author == comment.author
    assert updated.news == comment.news


def test_user_cant_delete_comment_of_another_user(
    not_author_client,
    delete_url
):
    initial_count = Comment.objects.count()
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count


def test_user_cant_edit_comment_of_another_user(
    not_author_client,
    comment,
    edit_url
):
    not_author_client.post(edit_url, data=FORM_DATA)
    from_db = Comment.objects.get(pk=comment.pk)
    assert from_db.text == comment.text
    assert from_db.author == comment.author
    assert from_db.news == comment.news
