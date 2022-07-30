from pathlib import Path
import pytest
from src import __version__
from src.app.examiner import settings
from . import fail_messages


def test_version():
    assert __version__ == '1.0.0', fail_messages.FAIL_APP_VERSION


class TestFrame:
    """Проверяет расположение папок и файлов,
    необходимых для работы приложения.
    """
    current_dir = Path.cwd()
    app_dir = current_dir / 'src/app/'

    def test_current_dir(self):
        assert self.current_dir == settings.BASE_DIR.parent.parent, (
            fail_messages.FAIL_CURRENT_DIR
        )

    def test_dir_src(self):
        assert Path(self.current_dir / 'src/').exists(), (
            fail_messages.FAIL_DIR_SRC
        )

    def test_dir_app(self):
        assert Path(self.app_dir).exists(), (
            fail_messages.FAIL_DIR_APP
        )

    def test_start_app_file(self):
        assert Path(self.current_dir / 'start_app.py').exists(), (
            fail_messages.FAIL_START_APP_FILE
        )

    def test_dir_templates(self):
        assert Path(self.app_dir / 'templates/').exists(), (
            fail_messages.FAIL_DIR_TEMPLATES
        )

    def test_dir_users(self):
        assert Path(self.app_dir / 'users').exists(), (
            fail_messages.FAIL_DIR_USERS
        )

    def test_dir_questions(self):
        assert Path(self.app_dir / 'questions/').exists(), (
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
    def test_db(self):
        default_db = settings.DATABASES['default']
        assert default_db['ENGINE'] == 'django.db.backends.sqlite3', (
            fail_messages.FAIL_DB_ENGINE
        )
        assert default_db['USER'], fail_messages.FAIL_DB_USER
        assert default_db['DB_PASS'], fail_messages.FAIL_DB_PASSWORD
        assert default_db['HOST'], fail_messages.FAIL_DB_HOST
