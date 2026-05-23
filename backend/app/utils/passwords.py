"""Password hashing helpers for local admin authentication."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000
SALT_BYTES = 16
HASH_BYTES = 32


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64decode(encoded: str) -> bytes:
    padding = "=" * (-len(encoded) % 4)
    return base64.urlsafe_b64decode(f"{encoded}{padding}")


def hash_password(password: str) -> str:
    """Return a salted PBKDF2-SHA256 password hash."""
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS,
        dklen=HASH_BYTES,
    )
    return f"{ALGORITHM}${ITERATIONS}${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored password hash."""
    try:
        algorithm, iterations_raw, salt_raw, digest_raw = password_hash.split("$", 3)
        if algorithm != ALGORITHM:
            return False

        iterations = int(iterations_raw)
        salt = _b64decode(salt_raw)
        expected_digest = _b64decode(digest_raw)
    except (binascii.Error, ValueError, TypeError):
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
        dklen=len(expected_digest),
    )
    return hmac.compare_digest(actual_digest, expected_digest)
