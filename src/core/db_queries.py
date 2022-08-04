"""Запросы к БД и кэшу.
"""
from datetime import datetime

from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Max, Model, Q, QuerySet, Sum
from django.core.cache import cache

from questions.models import Answer, Python, Question, Result, User
from . import constants as const


class Query:
    """Сборник запросов к БД и кэшу.
    """
    def get_all_questions_ids(subject: Model = Python) -> set:
        """Кэширует `id` всех вопросов по предмету.
        """
        ids = cache.get(const.CACHE_ALL_QS_IDS % subject)

        if ids is None:
            print('\n\n', 'NNNOOONN', '\n\n')
            ids = {i[0] for i in subject.objects.values_list('pk')}
            cache.set(const.CACHE_ALL_QS_IDS % subject, ids)

        return ids

    def get_maximum_grade() -> int:
        """Получет максимальный доступный балл.
        """
        maximum_grade = cache.get(const.CACHE_MAX_GRADE)
        if maximum_grade is None:
            maximum_grade = Answer.objects.filter(
                grade__gt=0
            ).aggregate(
                Sum('grade')
            )['grade__sum'] or 0
            cache.set(const.CACHE_MAX_GRADE, maximum_grade, 60*60)

        return maximum_grade

    def get_users_rating() -> QuerySet:
        """Получает рейтинг пользователей.
        """
        return User.objects.values(
                'username'
            ).annotate(
                score=Max('results__score')
            ).order_by('-score')

    def get_user_results(user: AbstractBaseUser) -> QuerySet:
        """Получает отсотрированные результаты пользователя.
        """
        return Result.objects.raw(
            '''SELECT id, score, finish_test_time, "{user}" AS username
            FROM questions_result
            WHERE users_id={id}
            ORDER BY finish_test_time DESC
            '''.format_map({"user": user, "id": user.pk})
        )

    def get_current_result(
        user: AbstractBaseUser,
        create_new_result: bool = True
    ) -> Result | None:
        """Получает последний незакрытый тест либо создаёт новый.
        """
        current_result = cache.get(
            const.CACHE_CURRENT_RESULT_FOR_USER % user.pk
        )
        if current_result is None:
            print('\n\n', 'CCRRR', '\n\n')
            current_result = Result.objects.filter(
                Q(users=user) & Q(finish_test_time=None)
            ).last()
            cache.set(
                const.CACHE_CURRENT_RESULT_FOR_USER % user.pk, current_result
            )

        if current_result is not None:
            return current_result

        if not create_new_result:
            return None

        current_result = Result.objects.create(users=user)
        cache.set(
            const.CACHE_CURRENT_RESULT_FOR_USER % user.pk, current_result
        )

        return current_result

    def get_current_question(
        question_pk: int
    ) -> Question | None:
        """Получить текущий вопрос.
        """
        question = None
        if question is None:
            question = Question.objects.filter(pk=question_pk).first()
        return question

    def get_next_question(
        user: AbstractBaseUser
    ) -> Model | None:
        """Получает следующий вопрос.
        """
        current_result = Query.get_current_result(user)
        past_questions = current_result.answers.values('questions__pk')
        past_questions = {i['questions__pk'] for i in past_questions}

        questions = Question.objects.exclude(pk__in=past_questions)
        if not questions:
            return None

        return questions[0]

    def update_result(
        user: AbstractBaseUser,
        question_pk: int,
        choice: list
    ) -> bool:
        """Проверяет, что ответы соответствуют вопросу.
        Если соответствут, обновляет результат.
        """
        answers = Answer.objects.filter(
            Q(questions__pk=question_pk) &
            Q(id__in=choice)
        ).select_related('questions')

        if not answers:
            return False

        current_result = Query.get_current_result(user)
        current_result.answers.add(*answers)
        return True

    def close_last_result(
        user: AbstractBaseUser
    ) -> tuple[bool, Result | None]:
        """Закрывает тест с указанием времени закрытия и
        проставлением суммы набранных баллов.
        """
        current_result = Query.get_current_result(
            user=user, create_new_result=False
        )
        if current_result is None:
            return False, current_result

        score = current_result.answers.aggregate(Sum('grade'))['grade__sum']
        if score is None:
            return False, current_result

        current_result.score = score
        current_result.finish_test_time = datetime.now()
        current_result.save()
        cache.delete(const.CACHE_CURRENT_RESULT_FOR_USER % user.pk)
        return True, current_result
