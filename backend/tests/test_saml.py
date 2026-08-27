from app.saml import extract_email, extract_onyen, saml_configured


def test_extract_onyen_from_uid_attribute():
    attributes = {"uid": ["jdoe"], "mail": ["jdoe@unc.edu"]}
    assert extract_onyen(attributes, name_id="opaque-id") == "jdoe"


def test_extract_onyen_falls_back_to_name_id():
    assert extract_onyen({}, name_id="jdoe") == "jdoe"


def test_extract_onyen_returns_none_without_attribute_or_name_id():
    assert extract_onyen({}, name_id=None) is None


def test_extract_email_from_mail_attribute():
    assert extract_email({"mail": ["jdoe@unc.edu"]}) == "jdoe@unc.edu"


def test_extract_email_returns_none_when_absent():
    assert extract_email({"uid": ["jdoe"]}) is None


def test_saml_configured_false_without_sp_credentials(monkeypatch):
    monkeypatch.setattr("app.saml.SAML_SP_CERT", None)
    monkeypatch.setattr("app.saml.SAML_SP_PRIVATE_KEY", "key")
    monkeypatch.setattr("app.saml.SAML_IDP_CERT", "cert")
    assert saml_configured() is False


def test_saml_configured_true_with_all_credentials(monkeypatch):
    monkeypatch.setattr("app.saml.SAML_SP_CERT", "cert")
    monkeypatch.setattr("app.saml.SAML_SP_PRIVATE_KEY", "key")
    monkeypatch.setattr("app.saml.SAML_IDP_CERT", "idp-cert")
    assert saml_configured() is True
