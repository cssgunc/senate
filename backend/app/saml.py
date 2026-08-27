"""SAML SP integration for UNC Onyen SSO.

IdP metadata (entity ID, SSO URL, signing cert) comes from UNC ITS's IdP
metadata endpoint (https://sso.unc.edu/metadata/idp), verified 2026-08-27 —
see app.config. SP credentials (our certificate/private key) must come from
the OpenShift secret; see deploy/cloudapps/template.yaml.

Attribute names below (ONYEN_ATTRIBUTE_CANDIDATES / EMAIL_ATTRIBUTE_CANDIDATES)
are best-guess eduPerson/InCommon conventions — ITS hasn't confirmed the exact
attribute names they'll release. saml_acs() logs the raw attribute dict on
every login attempt so the real names can be confirmed against the first live
test and this list adjusted.
"""

import logging

from onelogin.saml2.auth import OneLogin_Saml2_Auth

from app.config import (
    SAML_IDP_CERT,
    SAML_IDP_ENTITY_ID,
    SAML_IDP_SSO_URL,
    SAML_SP_ACS_URL,
    SAML_SP_CERT,
    SAML_SP_ENTITY_ID,
    SAML_SP_PRIVATE_KEY,
)

logger = logging.getLogger(__name__)

# Tried in order against the assertion's attribute dict.
ONYEN_ATTRIBUTE_CANDIDATES = [
    "uid",
    "onyen",
    "urn:oid:0.9.2342.19200300.100.1.1",  # eduPerson uid
]
EMAIL_ATTRIBUTE_CANDIDATES = [
    "mail",
    "email",
    "urn:oid:0.9.2342.19200300.100.1.3",  # eduPerson mail
]


def saml_configured() -> bool:
    """Whether we have everything needed to actually talk to the IdP.

    The IdP side is baked into defaults (see app.config); the SP cert/key
    are the piece that only exists once someone provisions the OpenShift
    secret, so that's what gates this in practice.
    """
    return bool(SAML_SP_CERT and SAML_SP_PRIVATE_KEY and SAML_IDP_CERT)


def saml_settings() -> dict:
    return {
        "strict": True,
        "debug": False,
        "sp": {
            "entityId": SAML_SP_ENTITY_ID,
            "assertionConsumerService": {
                "url": SAML_SP_ACS_URL,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
            "x509cert": SAML_SP_CERT or "",
            "privateKey": SAML_SP_PRIVATE_KEY or "",
        },
        "idp": {
            "entityId": SAML_IDP_ENTITY_ID,
            "singleSignOnService": {
                "url": SAML_IDP_SSO_URL,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "x509cert": SAML_IDP_CERT or "",
        },
        "security": {
            # ITS's IdP metadata sets WantAuthnRequestsSigned="true" — unsigned
            # requests will be rejected, this isn't optional.
            "authnRequestsSigned": True,
            "wantAssertionsSigned": True,
            "wantMessagesSigned": False,
            "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
        },
    }


def build_saml_request_data(
    scheme: str, host: str, port: int, path: str, get_params: dict, post_params: dict
) -> dict:
    return {
        "https": "on" if scheme == "https" else "off",
        "http_host": host,
        "server_port": port,
        "script_name": path,
        "get_data": get_params,
        "post_data": post_params,
    }


def build_saml_auth(request_data: dict) -> OneLogin_Saml2_Auth:
    return OneLogin_Saml2_Auth(request_data, saml_settings())


def extract_onyen(attributes: dict, name_id: str | None) -> str | None:
    for key in ONYEN_ATTRIBUTE_CANDIDATES:
        values = attributes.get(key)
        if values:
            return values[0]
    # Fall back to NameID — plausible for a non-federated in-house IdP where
    # the persistent identifier is just the onyen itself rather than an
    # opaque pairwise ID.
    return name_id


def extract_email(attributes: dict) -> str | None:
    for key in EMAIL_ATTRIBUTE_CANDIDATES:
        values = attributes.get(key)
        if values:
            return values[0]
    return None
