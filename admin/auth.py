"""Google token verification. No browser assertion is trusted as an identity."""
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from google.auth.transport.requests import Request
from google.oauth2 import id_token

OWNER_EMAIL = "raviv@metivity.com"


@dataclass(frozen=True)
class Settings:
    origin: str = "http://localhost:4180"
    client_id: str = ""
    owner_sub: str = ""
    database: Path = Path("data/private/admin.sqlite3")

    def __post_init__(self):
        url = urlsplit(self.origin)
        if (url.scheme not in {"https", "http"} or not url.hostname
                or url.path or url.query or url.fragment or url.username or url.password):
            raise ValueError("T2N_ORIGIN must be one exact origin, without a path.")
        if url.scheme != "https" and url.hostname not in {"localhost", "127.0.0.1"}:
            raise ValueError("Only loopback development may use HTTP.")
        if self.client_id and not self.client_id.endswith(".apps.googleusercontent.com"):
            raise ValueError("A Google web client ID is required.")

    @property
    def secure(self):
        return self.origin.startswith("https://")

    @classmethod
    def from_env(cls):
        return cls(origin=os.getenv("T2N_ORIGIN", "http://localhost:4180"),
                   client_id=os.getenv("T2N_GOOGLE_CLIENT_ID", ""),
                   owner_sub=os.getenv("T2N_OWNER_SUB", ""),
                   database=Path(os.getenv("T2N_DATABASE", "data/private/admin.sqlite3")))


def verify_google_token(credential, audience):
    # Official library verifies signature, audience, expiry and Google issuer.
    # A bounded timeout avoids indefinitely occupying an API worker.
    transport = Request()
    def request_with_timeout(*args, **kwargs):
        kwargs["timeout"] = 10
        return transport(*args, **kwargs)
    return id_token.verify_oauth2_token(credential, request_with_timeout, audience=audience)


def allowed_owner(claims, settings):
    if claims.get("email", "").lower() != OWNER_EMAIL or claims.get("email_verified") is not True:
        return False
    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject or len(subject) > 255:
        return False
    if settings.owner_sub:
        return subject == settings.owner_sub
    # For a third-party address, email_verified alone is not authoritative.
    # Workspace's signed hd claim is required for initial binding.
    return claims.get("hd") == "metivity.com"
