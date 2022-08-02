from pathlib import Path

import pytest

from src.examiner import settings

from . import fail_messages

APP_DIR = Path.cwd() / 'src/'


class TestFrame:
    """Проверяет расположение папок и файлов,
    необходимых для работы приложения.
    """
    def test_dir_app(self):
        assert Path(APP_DIR).exists(), (
            fail_messages.FAIL_DIR_APP
        )

    def test_dir_templates(self):
        assert Path(APP_DIR / 'templates/').exists(), (
            fail_messages.FAIL_DIR_TEMPLATES
        )

    def test_dir_users(self):
        assert Path(APP_DIR / 'users').exists(), (
            fail_messages.FAIL_DIR_USERS
        )

    def test_dir_questions(self):
        assert Path(APP_DIR / 'questions/').exists(), (
            fail_messages.FAIL_DIR_QUESTIONS
        )


class TestAppSettings:
    """Проверяет настройки приложения.
    """
    @pytest.mark.skip
    def test_debug(self):
        assert not settings.DEBUG, fail_messages.FAIL_DEBUG

    def test_secret_key(self):
        assert settings.SECRET_KEY, fail_messages.FAIL_SECRET_KEY

    @pytest.mark.skipif(settings.DEBUG, reason='Using `DEBUG`')
    def test_db_settings(self):
        default_db = settings.DATABASES['default']

        assert default_db['ENGINE'] == (
            'django.db.backends.sqlite3',
            fail_messages.FAIL_DB_ENGINE
        )
        assert default_db['USER'], fail_messages.FAIL_DB_USER
        assert default_db['DB_PASS'], fail_messages.FAIL_DB_PASSWORD
        assert default_db['HOST'], fail_messages.FAIL_DB_HOST

    def test_cache_settings(self):
        default_cache = settings.CACHES['default']
        assert default_cache['BACKEND'] == \
            'django.core.cache.backends.filebased.FileBasedCache', (
            fail_messages.FAIL_CACHE_BACKEND
        )
        assert default_cache['LOCATION'] == APP_DIR / 'examiner.cache', (
            fail_messages.FAIL_CACHE_LOCATION
        )
