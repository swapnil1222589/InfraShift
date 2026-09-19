from app.core.config import settings


def test_local_mode_is_true():
    # In tests, we ensure LOCAL_MODE is true to avoid real AWS calls
    assert settings.LOCAL_MODE is True
