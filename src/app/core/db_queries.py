from datetime import datetime

from django.db.models import F, Max, Q, Sum

from questions.models import Answer, Question, Result, User


class Query:
    """Сборник запросов к БД.
    """
    def get_naximum_grade():
        """Получет максимальный доступный балл.
        """
        return Answer.objects.filter(
                grade__gt=0
            ).aggregate(
                Sum('grade')
            )['grade__sum']

    def get_users_ratings():
        """Получает рейтинг пользователей.
        """
        return User.objects.values(
                'username'
            ).annotate(
                score=Max('results__score')
            ).order_by('-score')

    def get_user_results(user_id):
        """Получает отсотрированные результаты пользователя.
        """
        return User.objects.filter(
            id=user_id
        ).values(
            'username',
            score=F('results__score'),
            finish_test_time=F('results__finish_test_time')
        ).order_by('-results__finish_test_time')

    def get_last_open_result(user):
        """Ищет отрытый тест.
        """
        return Result.objects.filter(
            Q(users=user) & Q(finish_test_time=None)
        ).select_related('users').last()

    # TODO: get_or_create() and join with `next_question`
    def get_current_result(user):
        """Получает последний незакрытый тест либо создаёт новый.
        """
        result = Query.get_last_open_result(user)
        if not result:
            result = Result.objects.create(users=user)
        return result

    def get_next_question(user, current_result):
        """Получает следующий вопрос.
        """
        if current_result is None:
            current_result = Query.get_current_result(user)

        last_question = current_result.answers.values('questions__id').last()

        if isinstance(last_question, dict):
            last_question_id = last_question.get('questions__id', 0)
        else:
            last_question_id = 0

        return Question.objects.filter(id__gt=last_question_id).first()

    def update_result(result, question_id, choice) -> bool:
        """Проверяет, что ответы соответствуют вопросу.
        Если соответствут, обновляет результат.
        """
        answers = Answer.objects.filter(
            Q(questions__id=question_id) &
            Q(id__in=choice)
        ).select_related('questions')

        if not answers:
            return False

        result.answers.add(*answers)
        return True

    def close_last_result(self, result):
        """Закрывает тест с указанием времени закрытия и
        проставлением суммы набранных баллов.
        """
        score = result.answers.aggregate(Sum('grade'))['grade__sum']
        if score is None:
            score = 0
        result.score = score
        result.finish_test_time = datetime.now()
        result.save()
        return None
