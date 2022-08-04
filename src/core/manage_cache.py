from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from . import constants as const

User = get_user_model()


def clear_max_grade():
    cache.delete(const.MAX_GRADE)


@receiver(post_save, sender=User)
def max_grade_post_delete(sender, **kwargs):
    clear_max_grade()
