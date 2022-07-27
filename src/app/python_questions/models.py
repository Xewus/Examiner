from django.db import models

from src.app.questions.models import Question


class PythonQyestion(Question):
    pass

    def __str__(self):
        return 'Вопросы о Python\n' + super().__str__()
