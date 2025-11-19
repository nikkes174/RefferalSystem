from backend.config.config_db import DatabaseSettings


def test_database_settings_reads_env(monkeypatch):

    monkeypatch.setenv("DB_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("DB_ECHO", "true")

    settings = DatabaseSettings()

    assert settings.url == "postgresql+asyncpg://user:pass@localhost/db"
    assert settings.echo is True


def test_database_settings_default_echo(monkeypatch):

    monkeypatch.setenv("DB_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.delenv("DB_ECHO", raising=False)

    settings = DatabaseSettings()

    assert settings.url == "sqlite+aiosqlite:///:memory:"
    assert settings.echo is False


def test_database_settings_ignores_unrelated_env(monkeypatch):

    monkeypatch.setenv("DB_URL", "test-url")
    monkeypatch.setenv("SOME_OTHER_VAR", "12345")

    settings = DatabaseSettings()

    assert settings.url == "test-url"
    assert not hasattr(settings, "some_other_var")
