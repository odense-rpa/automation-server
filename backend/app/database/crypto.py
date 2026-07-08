"""Application-level encryption for sensitive database columns.

Encryption is opt-in: when ``settings.encryption_key`` is unset, values are
stored and returned as plaintext. When a key is configured, values are
encrypted on write with a ``enc:v1:`` prefix; reads accept both encrypted
and plaintext values, so existing rows keep working after a key is added.
"""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from app.config import settings

ENCRYPTION_PREFIX = "enc:v1:"

_UNSET_VALUES = ("", "set me in the env file")


class EncryptionKeyError(Exception):
    """An encrypted value cannot be decrypted with the configured key."""


def is_configured() -> bool:
    """Return True when an encryption key is set."""
    return settings.encryption_key not in _UNSET_VALUES


def _fernet() -> Fernet:
    digest = hashlib.sha256(settings.encryption_key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt(value: str | None) -> str | None:
    """Encrypt a value if a key is configured, otherwise pass it through."""
    if value is None or value == "" or not is_configured():
        return value
    return ENCRYPTION_PREFIX + _fernet().encrypt(value.encode()).decode()


def decrypt(value: str | None) -> str | None:
    """Decrypt a value carrying the encryption prefix; pass plaintext through.

    Raises:
        EncryptionKeyError: The value is encrypted but no key is configured,
            or the configured key does not match.
    """
    if value is None or not value.startswith(ENCRYPTION_PREFIX):
        return value

    if not is_configured():
        raise EncryptionKeyError(
            "Encrypted value found but no encryption key is configured"
        )

    token = value.removeprefix(ENCRYPTION_PREFIX)
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise EncryptionKeyError(
            "Encrypted value could not be decrypted with the configured key"
        ) from exc


class EncryptedStr(TypeDecorator):
    """String column encrypted at rest when an encryption key is configured."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return encrypt(value)

    def process_result_value(self, value, dialect):
        return decrypt(value)
