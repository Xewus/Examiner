from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.decorators import login_required
from django.http import (HttpRequest, HttpResponse, HttpResponseNotFound,
                         HttpResponseRedirect)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page

from core import constants as const
from core.db_queries import Query

INDEX_URL     = reverse_lazy('questions:index')
QUESTIONS_URL = reverse_lazy('questions:questions')
FINISH_URL    = reverse_lazy('questions:finish_test')


# @cache_page(timeout=20, key_prefix='index')  # 10 minutes
def index(request: HttpRequest):
    """Обработчик для главной страницы.
    """
    context = {
        'title'           : const.TITLE,
        'card_header'     : const.INDEX_CARD_HEADER,
        'index_page_text' : const.INDEX_PAGE_TEXT,
        'maximum_grade'   : Query.get_maximum_grade(),
    }
    return render(request, 'index.html', context)


# @cache_page(timeout=60, key_prefix='rating')  # 1 minute
def rating(request: HttpRequest):
    """Показывает рейтинг пользователей.
    """
    context = {
        'title'   : const.TITLE,
        'header'  : const.ALL_RESULTS_CARD_HEADER,
        'results' : Query.get_users_rating()
    }
    return render(request, 'questions/results.html', context)


@login_required
def my_results(request: HttpRequest):
    """Показывает все результаты текущего пользователя.
    """
    user: AbstractBaseUser = request.user
    context = {
        'title'   : const.TITLE,
        'header'  : const.MY_RESULTS_CARD_HEADER,
        'results' : Query.get_user_results(user)
    }
    return render(request, 'questions/results.html', context)


def get_question(
    request: HttpRequest
):
    """Выводит очередной вопрос и учитывает ответы.
    Если предыдущий тест был случайно прерван, продолжит предыдущий тест.
    """
    user: AbstractBaseUser = request.user
    if user.is_anonymous:
        return redirect(INDEX_URL)

    question = Query.get_next_question(user=user)
    if question is None:
        return redirect(FINISH_URL)

    context = {
        'title'       : const.TITLE,
        'question'    : question,
        'button_type' : ('radio', 'checkbox')[question.many_answers]
    }

    return render(request, 'questions/question.html', context)


@login_required
def add_answer(
    request: HttpRequest,
    question_pk: int
):
    """Учитывает переданные пользователем ответы.
    """
    question = Query.get_current_question(
        question_pk=question_pk
    )
    if question is None:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    context = {
        'title'       : const.TITLE,
        'question'    : question,
        'button_type' : ('radio', 'checkbox')[question.many_answers]

    }
    choice = request.POST.getlist('answer')

    if not choice:
        context['error_message'] = const.ERR_NO_ANSWERS
        return render(request, 'questions/question.html', context)

    if not Query.update_result(
        user        =request.user,
        question_pk =question_pk,
        choice      =choice
    ):
        context['error_message'] = const.ERR_FALSE_ANSWERS
        return render(request, 'questions/question.html', context)

    return redirect(QUESTIONS_URL)


def to_finish_test(
    request: HttpRequest
) -> HttpResponse | HttpResponseRedirect:
    """Завершает тест.
    Если пользователь не проходил тестов, либо пытается завершить без
    отмеченных ответов, перекидывает на главную страницу.
    Начатый тест будет продолжен в дальнейшем.
    """
    user: AbstractBaseUser = request.user
    if user.is_anonymous:
        return redirect(INDEX_URL)

    closed, current_result = Query.close_last_result(user)

    if not closed:
        return redirect(INDEX_URL)

    context = {
        'title'  : const.TITLE,
        'header' : const.FINISH_CARD_HEADER,
        'result' : current_result
    }
    return render(request, 'questions/finish.html', context)
