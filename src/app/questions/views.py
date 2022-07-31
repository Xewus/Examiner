from core import constants as const
from core.db_queries import Query
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.db.models import Model
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .models import Python


# @cache_page(timeout=20, key_prefix='index')  # 10 minutes
def index(request: HttpRequest):
    """Обработчик для главной страницы.
    """
    context = {
        'title': const.TITLE,
        'card_header': const.INDEX_CARD_HEADER,
        'index_page_text': const.INDEX_PAGE_TEXT,
        'maximum_grade': Query.get_maximum_grade(),
    }
    return render(request, 'index.html', context)


# @cache_page(timeout=60, key_prefix='rating')  # 1 minute
def rating(request: HttpRequest):
    """Показывает рейтинг пользователей.
    """
    context = {
        'title': const.TITLE,
        'header': const.ALL_RESULTS_CARD_HEADER,
        'results': Query.get_users_rating()
    }
    return render(request, 'questions/results.html', context)


@login_required
def my_results(request: HttpRequest):
    """Показывает все результаты текущего пользователя.
    """
    user: AbstractBaseUser | AnonymousUser = request.user
    context = {
        'title': const.TITLE,
        'header': const.MY_RESULTS_CARD_HEADER,
        'results': Query.get_user_results(user)
    }
    return render(request, 'questions/results.html', context)


@login_required
def get_question(
    request: HttpRequest,
    subject: Model = Python
):
    """Выводит очередной вопрос и учитывает ответы.
    Если предыдущий тест был случайно прерван, продолжит предыдущий тест.
    """
    user: AbstractBaseUser | AnonymousUser = request.user
    next_question = Query.get_next_question(user)
    context = {
        'title': const.TITLE,
        'question': next_question
    }

    if next_question is not None:
        context['button_type'] = (
            ('radio', 'checkbox')[next_question.many_answers]
        )

    if request.method == 'POST':
        return add_answer(
            request=request,
            subject=subject,
            context=context,
            next_question=next_question

        )

    return render(request, 'questions/question.html', context)


@login_required
def add_answer(
    request: HttpRequest,
    subject: Model,
    context: dict,
    next_question: Model | None = None
):
    """Учитывает переданные пользователем ответы.
    """
    choice: list = request.POST.getlist('answer')

    if not choice:
        context['error_message'] = const.ERR_NO_ANSWERS
        return render(request, 'questions/question.html', context)

    if not Query.update_result(
        user=request.user, choice=choice
    ):
        context['error_message'] = const.ERR_FALSE_ANSWERS
        return render(request, 'questions/question.html', context)

    if next_question is None:
        return to_finish_test(request=request)

    return render(request, 'questions/question.html', context)


#@login_required
def to_finish_test(
    request: HttpRequest
) -> HttpResponse | HttpResponseRedirect:
    """Завершает тест.
    Если пользователь не проходил тестов, либо пытается завершить без
    отмеченных ответов, перекидывает на главную страницу.
    Начатый тест будет продолжен в дальнейшем.
    """
    user: AbstractBaseUser | AnonymousUser = request.user
    closed, current_result = Query.close_last_result(user)

    if not closed:
        print('not closed')
        return redirect(reverse('questions:index'))

    if current_result.score <= 0:
        return redirect(const.LOSE)

    context = {
        'title': const.TITLE,
        'header': const.FINISH_CARD_HEADER,
        'result': current_result
    }
    return render(request, 'questions/finish.html', context)
