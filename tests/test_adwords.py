import types

import pytest

import vcr

from adwordspy.adwords import AdwordsAPI

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/vcr_cassettes',
    record_mode='none',
    match_on=['uri', 'method'],
)


@pytest.fixture
def adwords_tokens_for_accounts():
    return [12345678,
            'fake_client_id',
            'fake_client_secret',
            'fake_refresh_token',
            'fake_developer_token']


@pytest.fixture
def adwords_tokens():
    return [12345678,
            'fake_client_id',
            'fake_client_secret',
            'fake_refresh_token',
            'fake_developer_token']


@my_vcr.use_cassette()
def test_get_accounts(adwords_tokens_for_accounts):
    adwords = AdwordsAPI(*adwords_tokens_for_accounts)
    accounts = list(adwords.get_accounts())

    assert len(accounts) == 1

    account = accounts[0]
    assert 'customerId' in account
    assert 'name' in account
    assert 'companyName' in account


@my_vcr.use_cassette()
def test_get_accounts__with_fields(adwords_tokens_for_accounts):
    adwords = AdwordsAPI(*adwords_tokens_for_accounts)
    accounts = list(adwords.get_accounts(fields=['CustomerId', 'Name']))

    assert len(accounts) == 1

    account = accounts[0]
    assert 'customerId' in account
    assert 'name' in account
    assert 'companyName' not in account


@my_vcr.use_cassette()
def test_get_accounts__with_filters(adwords_tokens_for_accounts):
    adwords = AdwordsAPI(*adwords_tokens_for_accounts)

    filters = [
        {
            'field': 'CustomerId',
            'operator': 'EQUALS',
            'values': ['4100156312'],
        }
    ]
    accounts = list(adwords.get_accounts(filters=filters))
    assert len(accounts) == 1


@my_vcr.use_cassette()
def test_get_campaigns(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    campaigns = adwords.get_campaigns()
    assert isinstance(campaigns, types.GeneratorType)
    campaigns = list(campaigns)

    assert len(campaigns) == 4
    campaign = campaigns[0]
    assert 'servingStatus' in campaign
    assert 'startDate' in campaign


@my_vcr.use_cassette()
def test_get_campaigns__with_fields(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    campaigns = adwords.get_campaigns(fields=['Id', 'Name', 'Status'])
    assert isinstance(campaigns, types.GeneratorType)
    campaigns = list(campaigns)

    assert len(campaigns) == 4
    campaign = campaigns[0]
    assert 'id' in campaign
    assert 'name' in campaign
    assert 'status' in campaign
    assert 'StartDate' not in campaign


@my_vcr.use_cassette()
def test_get_campaigns__with_filters(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)
    filters = [
        {
            'field': 'Id',
            'operator': 'EQUALS',
            'values': ['384642878'],
        }
    ]
    campaigns = adwords.get_campaigns(filters=filters)
    assert isinstance(campaigns, types.GeneratorType)
    campaigns = list(campaigns)

    assert len(campaigns) == 1


@my_vcr.use_cassette()
def test_get_campaigns_by_status__paused(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    campaigns = adwords.get_campaigns_by_status(statuses=['PAUSED'])
    assert isinstance(campaigns, types.GeneratorType)
    campaigns = list(campaigns)

    assert len(campaigns) == 1


@my_vcr.use_cassette()
def test_get_campaigns_by_status__enabled(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    campaigns = adwords.get_campaigns_by_status(statuses=['ENABLED'])
    assert isinstance(campaigns, types.GeneratorType)
    campaigns = list(campaigns)

    assert len(campaigns) == 3


@my_vcr.use_cassette()
def test_get_campaigns_by_status__paused_enabled(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    campaigns = adwords.get_campaigns_by_status(statuses=['PAUSED', 'ENABLED'])
    assert isinstance(campaigns, types.GeneratorType)
    campaigns = list(campaigns)

    assert len(campaigns) == 4


@my_vcr.use_cassette()
def test_get_campaigns_by_status__empty(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    campaigns = adwords.get_campaigns_by_status()
    assert isinstance(campaigns, types.GeneratorType)
    campaigns = list(campaigns)

    assert len(campaigns) == 4
