import pytest
from django.contrib.auth import get_user_model

from src.questions.models import Python
from . import fail_messages

User = get_user_model()


@pytest.mark.django_db
def test_user_create():
    current_count = User.objects.count()
    User.objects.create(username='Пользователь', password='12345678')
    assert User.objects.count() == current_count + 1, (
        fail_messages.FAIL_CREATE_OBJECT % 'User'
    )
    assert User.objects.get(username='Пользователь')


@pytest.mark.django_db
def test_question_create():
    # assert Python.objects.count() == 0
    pass


@pytest.mark.django_db
def test_answer_create():
    ...
