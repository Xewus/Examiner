"""Запросы к БД.
"""
from datetime import datetime

from django.core.cache import cache
from django.db.models import F, Max, Q, Sum, QuerySet, Model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser

from questions.models import Answer, Python, Result, User

MAXIMUM_GRADE = 'maximum_grade'
QUESTION_IDS = 'questions_ids'
NEXT_QUESTION_FOR_USER = 'next_question_for_%s'
CURRENT_QUESTION_FOR_USER = 'current_question_for_%s'
RESULT_FOR_USER = 'result_for_%s'
IDS_QUESTIONS_FOR_USER = 'ids_questions_for_%s'


class Query:
    """Сборник запросов к БД и кэшу.
    """
    def get_all_questions_ids(model: Model = Python) -> set:
        """Кэширует `id` всех вопросов по предмету.
        """
        ids = cache.get(QUESTION_IDS)

        if ids is None:
            ids = {i[0] for i in model.objects.values_list('id')}
            cache.set(QUESTION_IDS, ids, 60)

        return ids

    def get_maximum_grade() -> int:
        """Получет максимальный доступный балл.
        """
        maximum_grade = cache.get(MAXIMUM_GRADE)

        if maximum_grade is None:
            maximum_grade = Answer.objects.filter(
                grade__gt=0
            ).aggregate(
                Sum('grade')
            )['grade__sum'] or 0
            cache.set(MAXIMUM_GRADE, maximum_grade, 60)

        return maximum_grade

    def get_users_rating() -> QuerySet:
        """Получает рейтинг пользователей.
        """
        return User.objects.values(
                'username'
            ).annotate(
                score=Max('results__score')
            ).order_by('-score')

    def get_user_results(user: AbstractBaseUser | AnonymousUser) -> QuerySet:
        """Получает отсотрированные результаты пользователя.
        """
        return User.objects.filter(
            id=user.id
        ).values(
            'username',
            score=F('results__score'),
            finish_test_time=F('results__finish_test_time')
        ).order_by('-results__finish_test_time')

    def get_current_result(
        user: AbstractBaseUser | AnonymousUser,
        create_new_resul: bool = True
    ) -> Result | None:
        """Получает последний незакрытый тест либо создаёт новый.
        """
        current_result = cache.get(RESULT_FOR_USER % user.id)
        if current_result is None:
            current_result = Result.objects.filter(
                Q(users=user) & Q(finish_test_time=None)
            ).select_related('users').last()

        print('res in get_res:', current_result, '\n')

        if current_result is not None:
            return current_result

        if not create_new_resul:
            return None

        current_result = Result.objects.create(users=user)
        cache.set(RESULT_FOR_USER % user.id, current_result, 60)
        cache.set(
            IDS_QUESTIONS_FOR_USER % user.id,
            Query.get_all_questions_ids(),
            60
        )

        return current_result

    def get_next_question(
        user: AbstractBaseUser | AnonymousUser,
        subject: Model = Python,
    ) -> Model | None:
        """Получает следующий вопрос.
        """
        current_result: Result = Query.get_current_result(user)
        questions: set = cache.get(IDS_QUESTIONS_FOR_USER % user.id)
        print('get_next_q:', current_result, questions, sep='\n')

        if questions is None:
            past_question_ids = current_result.answers.values('questions__id')
            all_questions_ids = Query.get_all_questions_ids()
            if len(past_question_ids) == len(all_questions_ids):
                return None

            past_question_ids = {i['questions__id'] for i in past_question_ids}
            cache.set(
                IDS_QUESTIONS_FOR_USER % user.id,
                Query.get_all_questions_ids() - past_question_ids,
                60
            )
            questions: set = cache.get(IDS_QUESTIONS_FOR_USER % user.id)

        elif not questions:
            cache.delete(IDS_QUESTIONS_FOR_USER % user.id)
            cache.set(
                CURRENT_QUESTION_FOR_USER % user.id,
                cache.get(NEXT_QUESTION_FOR_USER % user.id),
                10 * 9
            )
            return None

        next_question_id: int = questions.pop()
        next_question = subject.objects.get(id=next_question_id)

        cache.set(
            CURRENT_QUESTION_FOR_USER % user.id,
            cache.get(NEXT_QUESTION_FOR_USER % user.id),
            10 * 9
        )
        cache.set(NEXT_QUESTION_FOR_USER % user.id, next_question, 10 * 9)
        cache.set(IDS_QUESTIONS_FOR_USER % user.id, questions, 10 * 9)

        print('get_q: q_id=', next_question_id, '\n')
        return next_question

    def update_result(
        user: AbstractBaseUser | AnonymousUser,
        choice: list
    ) -> bool:
        """Проверяет, что ответы соответствуют вопросу.
        Если соответствут, обновляет результат.
        """
        question: Model = cache.get(CURRENT_QUESTION_FOR_USER % user.id)
        answers = Answer.objects.filter(
            Q(questions__id=question.id) &
            Q(id__in=choice)
        ).select_related('questions')
        print('updres', answers, choice, question.id, '\n')

        if not answers:
            return False

        current_result = Query.get_current_result(user)
        current_result.answers.add(*answers)
        cache.delete(CURRENT_QUESTION_FOR_USER % user.id)
        return True

    def close_last_result(
        user: AbstractBaseUser | AnonymousUser
    ) -> tuple[bool, Result]:
        """Закрывает тест с указанием времени закрытия и
        проставлением суммы набранных баллов.
        """
        current_result = Query.get_current_result(
            user=user, create_new_resul=False
        )
        if current_result is None:
            return False
        print('cur_res in f_closed:', current_result)

        score = current_result.answers.aggregate(Sum('grade'))['grade__sum']
        if score is None:
            return False, current_result

        current_result.score = score
        current_result.finish_test_time = datetime.now()
        current_result.save()
        cache.delete(RESULT_FOR_USER % user.id)
        return True, current_result
