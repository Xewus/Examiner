from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page

from core.db_queries import Query
from core import constants as const

from .models import Result


@cache_page(timeout=20, key_prefix='index')  # 10 minutes
def index(request):
    """Обработчик для главной страницы.
    """
    context = {
        'title': const.TITLE,
        'card_header': const.INDEX_CARD_HEADER,
        'index_page_text': const.INDEX_PAGE_TEXT,
        'maximum_grade': Query.get_maximum_grade(),
    }
    return render(request, 'index.html', context)


@cache_page(timeout=60, key_prefix='rating')  # 1 minute
def rating(request):
    """Показывает рейтинг пользователей.
    """
    context = {
        'title': const.TITLE,
        'header': const.ALL_RESULTS_CARD_HEADER,
        'results': Query.get_users_ratings()
    }
    return render(request, 'questions/results.html', context)


@login_required
def my_results(request):
    """Показывает все результаты текущего пользователя.
    """
    context = {
        'title': const.TITLE,
        'header': const.MY_RESULTS_CARD_HEADER,
        'results': Query.get_user_results(request.user.id)
    }
    return render(request, 'questions/results.html', context)


@login_required
def get_question(
    request, current_result=None, to_add_answer=True, error_message=None
):
    """Выводит очередной вопрос и учитывает ответы.
    Если предыдущий тест был случайно прерван, продолжит предыдущий тест.
    """
    next_question, current_result = Query.get_next_question(request.user.id, current_result)
    print(next_question, '\n\n')

    if not next_question:
        return to_finish_test(request, current_result)

    # Переход к обработке переданных ответов
    if request.method == 'POST' and to_add_answer:
        return add_answer(request, current_result, next_question.id)

    context = {
        'title': const.TITLE,
        'question': next_question,
        'button_type': ('radio', 'checkbox')[next_question.many_answers],
        'error_message': error_message
    }
    return render(request, 'questions/question.html', context)


@login_required
def add_answer(request, result, question_id):
    """Учитывает переданые пользователем ответы.
    """
    choice = request.POST.getlist('answer')
    if not choice:
        return get_question(
            request,
            to_add_answer=False,
            error_message=const.ERR_NO_ANSWERS
        )

    if not Query.update_result(result, question_id, choice):
        return get_question(
            request,
            to_add_answer=False,
            error_message=const.ERR_FALSE_ANSWERS
        )

    return get_question(request, result, to_add_answer=False)


# @login_required
def to_finish_test(request, result=None):
    """Завершает тест.
    Если пользователь не проходил тестов, либо пытается завершить без
    отмеченных ответов, перекидывает на главную страницу.
    Начатый тест будет продолжен в дальнейшем.
    """
    if result is None:
        result = Result.objects.values(
            'score', username=F('users__username')
        ).filter(
            users=request.user
        ).order_by('-id').first()

    if result is None or result.score is None:
        return redirect('questions:index')

    if not result.finish_test_time:
        Query.close_last_result(result)

    if result.score < 0:
        return redirect(const.LOSE)

    context = {
        'title': const.TITLE,
        'header': const.FINISH_CARD_HEADER,
        'result': result
    }
    return render(request, 'questions/finish.html', context)
