import pytest

from app.config import settings
from app.database import crypto


def test_is_configured_false_for_unset_values(monkeypatch):
    monkeypatch.setattr(settings, "encryption_key", "set me in the env file")
    assert crypto.is_configured() is False

    monkeypatch.setattr(settings, "encryption_key", "")
    assert crypto.is_configured() is False


def test_passthrough_without_key(monkeypatch):
    monkeypatch.setattr(settings, "encryption_key", "set me in the env file")

    assert crypto.encrypt("secret") == "secret"
    assert crypto.decrypt("secret") == "secret"


def test_roundtrip_with_key(monkeypatch):
    monkeypatch.setattr(settings, "encryption_key", "test-key")

    token = crypto.encrypt("secret")

    assert token != "secret"
    assert token.startswith(crypto.ENCRYPTION_PREFIX)
    assert crypto.decrypt(token) == "secret"


def test_none_and_empty_values_pass_through(monkeypatch):
    monkeypatch.setattr(settings, "encryption_key", "test-key")

    assert crypto.encrypt(None) is None
    assert crypto.encrypt("") == ""
    assert crypto.decrypt(None) is None
    assert crypto.decrypt("") == ""


def test_plaintext_passes_through_with_key(monkeypatch):
    monkeypatch.setattr(settings, "encryption_key", "test-key")

    assert crypto.decrypt("legacy plaintext") == "legacy plaintext"


def test_decrypt_without_key_raises(monkeypatch):
    monkeypatch.setattr(settings, "encryption_key", "test-key")
    token = crypto.encrypt("secret")

    monkeypatch.setattr(settings, "encryption_key", "set me in the env file")
    with pytest.raises(crypto.EncryptionKeyError):
        crypto.decrypt(token)


def test_decrypt_with_wrong_key_raises(monkeypatch):
    monkeypatch.setattr(settings, "encryption_key", "test-key")
    token = crypto.encrypt("secret")

    monkeypatch.setattr(settings, "encryption_key", "another-key")
    with pytest.raises(crypto.EncryptionKeyError):
        crypto.decrypt(token)
