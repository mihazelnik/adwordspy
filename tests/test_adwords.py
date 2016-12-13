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
    assert 'canManageClients' in account
    assert not account.canManageClients


@my_vcr.use_cassette()
def test_get_accounts__manage_clients(adwords_tokens_for_accounts):
    adwords = AdwordsAPI(*adwords_tokens_for_accounts)
    accounts = list(adwords.get_accounts(manage_clients=True))

    assert len(accounts) == 1

    account = accounts[0]
    assert 'customerId' in account
    assert 'name' in account
    assert 'canManageClients' in account
    assert account.canManageClients


@my_vcr.use_cassette()
def test_get_accounts__with_fields(adwords_tokens_for_accounts):
    adwords = AdwordsAPI(*adwords_tokens_for_accounts)
    accounts = list(adwords.get_accounts(fields=['CustomerId', 'Name']))

    assert len(accounts) == 1

    account = accounts[0]
    assert 'customerId' in account
    assert 'name' in account
    assert 'CanManageClients' not in account


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


@my_vcr.use_cassette()
def test_get_adgroups(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    adgroups = adwords.get_adgroups([326250038])
    assert isinstance(adgroups, types.GeneratorType)
    adgroups = list(adgroups)

    assert len(adgroups) == 4
    adgroup = adgroups[0]
    assert 'id' in adgroup
    assert 'name' in adgroup
    assert 'status' in adgroup
    assert 'campaignId' in adgroup


@my_vcr.use_cassette()
def test_get_adgroups__with_fields(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    adgroups = adwords.get_adgroups([326250038], fields=['Id', 'Name', 'Status'])
    assert isinstance(adgroups, types.GeneratorType)
    adgroups = list(adgroups)

    assert len(adgroups) == 4
    adgroup = adgroups[0]
    assert 'id' in adgroup
    assert 'name' in adgroup
    assert 'status' in adgroup
    assert 'campaignId' not in adgroup


@my_vcr.use_cassette()
def test_get_adgroups__with_filters(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)
    filters = [
        {
            'field': 'Id',
            'operator': 'EQUALS',
            'values': ['31243092638'],
        }
    ]
    adgroups = adwords.get_adgroups([326250038], filters=filters)
    assert isinstance(adgroups, types.GeneratorType)
    adgroups = list(adgroups)
    assert len(adgroups) == 1


@my_vcr.use_cassette()
def test_get_adgroups_by_status__enabled(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    adgroups = adwords.get_adgroups_by_status([326250038], statuses=['ENABLED'])
    assert isinstance(adgroups, types.GeneratorType)
    adgroups = list(adgroups)

    assert len(adgroups) == 3


@my_vcr.use_cassette()
def test_get_adgroups_by_status__paused(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    adgroups = adwords.get_adgroups_by_status([326250038], statuses=['PAUSED'])
    assert isinstance(adgroups, types.GeneratorType)
    adgroups = list(adgroups)

    assert len(adgroups) == 1


@my_vcr.use_cassette()
def test_get_adgroups_by_status__paused_enabled(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    adgroups = adwords.get_adgroups_by_status([326250038], statuses=['PAUSED', 'ENABLED'])
    assert isinstance(adgroups, types.GeneratorType)
    adgroups = list(adgroups)

    assert len(adgroups) == 4


@my_vcr.use_cassette()
def test_get_adgroups_by_status__empty(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    adgroups = adwords.get_adgroups_by_status([326250038])
    assert isinstance(adgroups, types.GeneratorType)
    adgroups = list(adgroups)

    assert len(adgroups) == 4


@my_vcr.use_cassette()
def test_get_ads(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    ads = adwords.get_ads([31243092638])
    assert isinstance(ads, types.GeneratorType)
    ads = list(ads)

    assert len(ads) == 2

@my_vcr.use_cassette()
def test_get_ads__with_filters(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    filters = [
        {
            'field': 'Id',
            'operator': 'EQUALS',
            'values': ['112862255078'],
        }
    ]

    ads = adwords.get_ads([31243092638], filters=filters)
    assert isinstance(ads, types.GeneratorType)
    ads = list(ads)

    assert len(ads) == 1


@my_vcr.use_cassette()
def test_get_ads__types(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    ads = adwords.get_ads([31243092638], types=['IMAGE_AD'])
    assert isinstance(ads, types.GeneratorType)
    ads = list(ads)
    assert len(ads) == 0


@my_vcr.use_cassette()
def test_get_text_ads(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    ads = adwords.get_ads([31243092638])
    assert isinstance(ads, types.GeneratorType)
    ads = list(ads)

    assert len(ads) == 2


@my_vcr.use_cassette()
def test_get_text_ads_by_status(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    ads = adwords.get_text_ads_by_status([31243092638])
    assert isinstance(ads, types.GeneratorType)
    ads = list(ads)

    assert len(ads) == 2

@my_vcr.use_cassette()
def test_get_text_ads_by_status__enabled(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    ads = adwords.get_text_ads_by_status([31243092638], statuses=['ENABLED'])
    assert isinstance(ads, types.GeneratorType)
    ads = list(ads)

    assert len(ads) == 1

@my_vcr.use_cassette()
def test_get_text_ads_by_status__paused(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    ads = adwords.get_text_ads_by_status([31243092638], statuses=['ENABLED'])
    assert isinstance(ads, types.GeneratorType)
    ads = list(ads)

    assert len(ads) == 1

@my_vcr.use_cassette()
def test_get_text_ads_by_status__enabled_paused(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    ads = adwords.get_text_ads_by_status([31243092638], statuses=['ENABLED', 'PAUSED'])
    assert isinstance(ads, types.GeneratorType)
    ads = list(ads)

    assert len(ads) == 2

@my_vcr.use_cassette()
def test_get_keywords(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    keywords = adwords.get_keywords([31243092638])
    assert isinstance(keywords, types.GeneratorType)
    keywords = list(keywords)
    assert len(keywords) == 7


@my_vcr.use_cassette()
def test_get_keywords__with_filter(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    filters = [
        {
            'field': 'Id',
            'operator': 'EQUALS',
            'values': ['273298308403'],
        }
    ]

    keywords = adwords.get_keywords([31243092638], filters=filters)
    assert isinstance(keywords, types.GeneratorType)
    keywords = list(keywords)
    assert len(keywords) == 1


@my_vcr.use_cassette()
def test_get_keywords_by_match_type__broad(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    keywords = adwords.get_keywords_by_match_type([31243092638], match_types=['BROAD'])
    assert isinstance(keywords, types.GeneratorType)
    keywords = list(keywords)
    assert len(keywords) == 5


@my_vcr.use_cassette()
def test_get_keywords_by_match_type__phrase(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    keywords = adwords.get_keywords_by_match_type([31243092638], match_types=['PHRASE'])
    assert isinstance(keywords, types.GeneratorType)
    keywords = list(keywords)
    assert len(keywords) == 1


@my_vcr.use_cassette()
def test_get_keywords_by_match_type__exact(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    keywords = adwords.get_keywords_by_match_type([31243092638], match_types=['EXACT'])
    assert isinstance(keywords, types.GeneratorType)
    keywords = list(keywords)
    assert len(keywords) == 1


@my_vcr.use_cassette()
def test_get_keywords_by_status__enabled(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    keywords = adwords.get_keywords_by_status([31243092638], statuses=['ENABLED'])
    assert isinstance(keywords, types.GeneratorType)
    keywords = list(keywords)
    assert len(keywords) == 5


@my_vcr.use_cassette()
def test_get_keywords_by_status__paused(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)

    keywords = adwords.get_keywords_by_status([31243092638], statuses=['PAUSED'])
    assert isinstance(keywords, types.GeneratorType)
    keywords = list(keywords)
    assert len(keywords) == 2


@my_vcr.use_cassette()
def test_set_adgroup_status(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)
    filters = [
        {
            'field': 'Id',
            'operator': 'EQUALS',
            'values': ['31243100678'],
        }
    ]
    adgroups = adwords.get_adgroups([384642878], filters=filters)
    adgroups = list(adgroups)
    assert len(adgroups) == 1
    adgroup = adgroups[0]
    assert adgroup.status == 'ENABLED'
    adwords.set_adgroup_status(31243100678, 'PAUSED')
    adgroups = adwords.get_adgroups([384642878], filters=filters)
    adgroups = list(adgroups)
    assert len(adgroups) == 1
    adgroup = adgroups[0]
    assert adgroup.status == 'PAUSED'
    adwords.set_adgroup_status(31243100678, 'ENABLED')
    adgroups = adwords.get_adgroups([384642878], filters=filters)
    adgroups = list(adgroups)
    assert len(adgroups) == 1
    adgroup = adgroups[0]
    assert adgroup.status == 'ENABLED'


@my_vcr.use_cassette()
def test_set_ad_status(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)
    filters = [
        {
            'field': 'Id',
            'operator': 'EQUALS',
            'values': ['112862304038'],
        }
    ]
    ads = adwords.get_ads([31243100678], filters=filters)
    ads = list(ads)
    assert len(ads) == 1
    ad = ads[0]
    assert ad.status == 'ENABLED'
    adwords.set_ad_status(31243100678, 112862304038, 'PAUSED')
    ads = adwords.get_ads([31243100678], filters=filters)
    ads = list(ads)
    assert len(ads) == 1
    ad = ads[0]
    assert ad.status == 'PAUSED'
    adwords.set_ad_status(31243100678, 112862304038, 'ENABLED')
    ads = adwords.get_ads([31243100678], filters=filters)
    ads = list(ads)
    assert len(ads) == 1
    ad = ads[0]
    assert ad.status == 'ENABLED'


@my_vcr.use_cassette()
def test_set_keyword_status(adwords_tokens):
    adwords = AdwordsAPI(*adwords_tokens)
    adwords.set_keyword_status(31243100678, 22854470, 'PAUSED')
    adwords.set_keyword_status(31243100678, 22854470, 'ENABLED')
