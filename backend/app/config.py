import os

from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_csv(name: str, default: list[str] | None = None) -> list[str]:
    value = os.getenv(name)
    if not value:
        return default or []
    return [item.strip() for item in value.split(",") if item.strip()]


ENVIRONMENT = os.getenv("ENVIRONMENT", os.getenv("MODE", "development")).lower()
DEBUG = _env_bool("DEBUG", default=ENVIRONMENT != "production")
CORS_ORIGINS = _env_csv("CORS_ORIGINS", ["http://localhost:3000"])

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
UPLOAD_BASE_URL = os.getenv("UPLOAD_BASE_URL", "/api/uploads")
MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(5 * 1024 * 1024)))

ANALYTICS_INGEST_SECRET = os.getenv("ANALYTICS_INGEST_SECRET")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", "speaker@unc.edu")

# UNC Onyen SSO (SAML).
#
# SP side is our own registration with ITS (entity ID, ACS URL) — defaults below
# match what was submitted. IdP side is UNC's, fetched and verified against
# https://sso.unc.edu/metadata/idp on 2026-08-27; defaults below match that.
# Overridable via env in case either ever needs to change without a code deploy.
SAML_SP_ENTITY_ID = os.getenv("SAML_SP_ENTITY_ID", "https://senate.unc.edu")
SAML_SP_ACS_URL = os.getenv(
    "SAML_SP_ACS_URL",
    "https://senate-backend-dept-undergraduate-senate.apps.cloudapps.unc.edu/api/auth/saml/acs",
)
# Our SP certificate/private key — never committed. Must be set via the
# OpenShift secret (see deploy/cloudapps/template.yaml) before SSO can work;
# the IdP requires signed AuthnRequests (WantAuthnRequestsSigned=true).
SAML_SP_CERT = os.getenv("SAML_SP_CERT")
SAML_SP_PRIVATE_KEY = os.getenv("SAML_SP_PRIVATE_KEY")

SAML_IDP_ENTITY_ID = os.getenv("SAML_IDP_ENTITY_ID", "https://sso.unc.edu/idp")
SAML_IDP_SSO_URL = os.getenv(
    "SAML_IDP_SSO_URL", "https://sso.unc.edu/idp/profile/SAML2/Redirect/SSO"
)
SAML_IDP_CERT = os.getenv(
    "SAML_IDP_CERT",
    "MIIC/zCCAeegAwIBAgIJAKbdYCfHuaO6MA0GCSqGSIb3DQEBCwUAMBYxFDASBgNVBAMMC3Nzby51bmMuZWR1MB4XDTE2MDgxMjE1MzUyMFoXDTM2MDgxMjE1MzUyMFowFjEUMBIGA1UEAwwLc3NvLnVuYy5lZHUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCclewnsUf+I4ykc+gHILGPVCMkT4AoLOchiXYzk21KhlaKlpj6LoQokZG381V53jST4tl9kq8cK6hgDa7Sr9uAtH/AYfNNmNjVpmZho6zPsZzrmH9UJ7MID8Nd2H4YpTb4MTPhhf10nCiVd6TIuuNw5WVa79Bfoas8eKR25aTQgZAci+bGAURjJxCxBZTI2mG2kVymTW6mk4/g9LmzerQerAQtqNHZJ9cwDv6kFnvv6TIMDaSOMgPsU4rAWyPO7yBi4fmjWLtuEzo3ld4mPQQ0FwqHa6E/gIgqDbj4akfT5mbS726WjGK8qqJxeq4oN5mhkLC0xpdvLuqldRl9max/AgMBAAGjUDBOMB0GA1UdDgQWBBT6sAuFGcdqPD1zPa8aNO2gMUIJUTAfBgNVHSMEGDAWgBT6sAuFGcdqPD1zPa8aNO2gMUIJUTAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQAK2oJw+TWofs88vOvmC3UBm0buOP7nsVGoVALhIbn5ZpmNz6uTrHnyMBmjEBXx1/3br7JkzMdcTX/BamHrgfzhTp1WutCJZ5OtVZGv+ADX3g1o/dN4612wl29+6rFrAKIxfFbpK4VZtp9l1UXUQhkR62ShU0+iT+Aku5g4Pmi5iMkqcPBGwkHLw8enbCUdaRftpYGkvfXPKnhYlGAFmfCB1Qb8xMsjIZghf+XXsM5rq4IxnOPLaWGbmlKOqLMcm4s+ToxdeOKEyNWYnLRrYhQH5Onj/0AX9U+unabDJzCBUng/vVPjlhQOuoX24oTjN4LMnBr7sy3/SJbBLZ0AU8n8",
)

# Where to redirect the browser back to once SSO completes. Reuses the first
# configured CORS origin (the frontend) rather than adding a separate param.
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", CORS_ORIGINS[0] if CORS_ORIGINS else "")
