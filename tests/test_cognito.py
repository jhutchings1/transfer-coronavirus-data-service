from unittest.mock import patch

import pytest

from cognito import (
    CognitoException,
    allowed_domains,
    get_env_pool_id,
    return_false_if_unexpected_domain,
    sanitise_email,
    sanitise_name,
    sanitise_phone,
)


@pytest.fixture
def mock_env_staging(monkeypatch):
    monkeypatch.setenv("CF_SPACE", "staging")


@pytest.fixture
def mock_env_production(monkeypatch):
    monkeypatch.setenv("CF_SPACE", "production")


def test_sanitise_email():

    test1 = "anormalemail@example.gov.uk"
    assert sanitise_email(test1) == test1

    test2 = "abad@email@example.com"
    with pytest.raises(CognitoException) as exception:
        sanitise_email(test2)
    assert (
        str(exception.value) == "BadEmailWhitelist: failed for 'abad@email@example.com'"
    )

    test3 = "abadexample.com"
    with pytest.raises(CognitoException) as exception:
        sanitise_email(test3)
    assert str(exception.value) == "BadEmail: not a valid email for 'abadexample.com'"

    test4 = "notavaliddomain@hotmail.com"
    with pytest.raises(CognitoException) as exception:
        sanitise_email(test4)
    assert (
        str(exception.value)
        == "BadEmailWhitelist: failed for 'notavaliddomain@hotmail.com'"
    )


def test_allowed_domains():
    assert [
        ".gov.uk",
        "@brake.co.uk",
        "@nhs.net",
        "@tesco.com",
        "@ocadoretail.com",
        "@morrisonsplc.co.uk",
        "@sainsburys.co.uk",
        "@iceland.co.uk",
        "@coop.co.uk",
        "@asda.co.uk",
        "@johnlewis.co.uk",
    ] == allowed_domains()


def test_return_false_if_unexpected_domain():

    for allowed_domain in allowed_domains():
        email_address = f"foo{allowed_domain}"
        assert return_false_if_unexpected_domain(email_address)


def test_sanitise_phone():

    test1 = "+441234567890"
    assert sanitise_phone(test1) == test1

    test2 = "441234567890"
    assert sanitise_phone(test2) == "+441234567890"

    test3 = "01234567890"
    assert sanitise_phone(test3) == "+441234567890"

    test4 = "string_prefix01234567890"
    assert sanitise_phone(test4) == "+441234567890"

    test5 = "notaphonenumber"
    assert sanitise_phone(test5) == ""


def test_sanitise_name():

    test1 = "joe bloggs"
    assert sanitise_name(test1) == "joebloggs"

    test2 = "joe_bloggs"
    assert sanitise_name(test2) == "joe_bloggs"

    test2 = "joe bloggs 2"
    assert sanitise_name(test2) == "joebloggs2"


def test_get_env_pool_id(monkeypatch):
    with patch("cognito.list_pools") as mock_list_pools:
        monkeypatch.setenv("CF_SPACE", "staging")
        mock_list_pools.return_value = [
            {"name": "corona-cognito-pool-staging", "id": "staging-pool-id"},
            {"name": "corona-cognito-pool-prod", "id": "production-pool-id"},
        ]
        assert get_env_pool_id() == "staging-pool-id"

    with patch("cognito.list_pools") as mock_list_pools:
        monkeypatch.setenv("CF_SPACE", "production")
        mock_list_pools.return_value = [
            {"name": "corona-cognito-pool-staging", "id": "staging-pool-id"},
            {"name": "corona-cognito-pool-prod", "id": "production-pool-id"},
        ]
        assert get_env_pool_id() == "production-pool-id"
