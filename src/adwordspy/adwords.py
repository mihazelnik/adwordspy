# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

import suds

from googleads import adwords
from googleads import oauth2


class RetriesLimitException(Exception):
    def __init__(self, retries):
        Exception.__init__(self, 'Tried to get service {} times, but failed.'.format(retries))


class AdwordsAPI(object):
    def __init__(self, account_id, client_id, client_secret, refresh_token, developer_token,
                 version='v201609', page_size=100, retries=3, timesleep=True):
        self.account_id = account_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.developer_token = developer_token
        self.client = self._make_client()
        self._service_cache = {}
        self.version = version
        self.page_size = page_size
        self.retries = retries
        self.timesleep = timesleep

    def _make_client(self):
        """
            Make a custom adwords client.
        """
        oauth2_client = oauth2.GoogleRefreshTokenClient(
            self.client_id,
            self.client_secret,
            self.refresh_token)

        adwords_client = adwords.AdWordsClient(
            self.developer_token,
            oauth2_client,
            'adwords-client',
            client_customer_id=self.account_id)

        return adwords_client

    def _refresh_service(self, name):
        """
            If we get AuthenticationError try to refresh service.
        """
        service = self.client.GetService(name, version=self.version)
        self._service_cache[name] = service
        return service

    def get_service(self, name):
        """
        """
        if name in self._service_cache:
            service = self._service_cache[name]
        else:
            service = self.client.GetService(name, version=self.version)
            self._service_cache[name] = service
        return service

    def _mutate_operation(self, service, operations):

        tries = 0
        while tries <= self.retries:
            try:
                service.mutate(operations)
                break
            except suds.WebFault as e:
                errors = e.fault.detail.ApiExceptionFault.errors
                if not isinstance(errors, list):
                    errors = [errors]
                for error in errors:
                    if error['ApiError.Type'] == 'InternalApiError':
                        tries += 1
                        if self.timesleep:
                            time.sleep(2 ** tries)
                    elif error['ApiError.Type'] == 'RateExceededError':
                        if self.timesleep:
                            time.sleep(int(error['retryAfterSeconds']))
                    else:
                        raise e

        if tries > self.retries:
            raise RetriesLimitException(self.retries)

    def _iter_selector(self, service, selector, name):
        """
            Yield a list of entries from `service` using `selector`
        """
        offset = 0
        more_pages = True

        while more_pages:
            tries = 0
            while tries <= self.retries:
                try:
                    page = service.get(selector)
                    break
                except suds.WebFault as e:
                    errors = e.fault.detail.ApiExceptionFault.errors
                    if not isinstance(errors, list):
                        errors = [errors]
                    for error in errors:
                        if error['ApiError.Type'] == 'AuthenticationError':
                            self._refresh_service(name)
                            # this will try to get service one more time
                            tries += self.retries - 1
                        elif error['ApiError.Type'] == 'InternalApiError':
                            tries += 1
                            if self.timesleep:
                                time.sleep(2 ** tries)
                        elif error['ApiError.Type'] == 'RateExceededError':
                            if self.timesleep:
                                time.sleep(int(error['retryAfterSeconds']))
                        else:
                            raise e
            if tries > self.retries:
                raise RetriesLimitException(self.retries)

            if 'entries' in page:
                for c in page['entries']:
                    yield c

            offset += self.page_size
            selector['paging']['startIndex'] = str(offset)
            more_pages = offset < int(page['totalNumEntries'])

    def get_custom_service(self, name, selector, pagination=True):
        service = self.get_service(name)
        if pagination:
            selector['paging'] = {'startIndex': 0, 'numberResults': str(self.page_size)}
            for page in self._iter_selector(service, selector, name):
                yield page
        else:
            yield service.get(selector)

    def get_accounts(self, fields=None, filters=None, manage_clients=False):
        """
        Get all adwords accounts associated with `account_id`
        Args:
            fields (list): list of fields you want to get for each account
                           https://developers.google.com/adwords/api/docs/reference/v201609/ManagedCustomerService.ManagedCustomer
            filters (list): list of filters you want to filter by
                            https://developers.google.com/adwords/api/docs/reference/v201609/ManagedCustomerService.Predicate

        Yields:
            adwords accounts

        Examples:
            >>> get_accounts(fields=['CustomerId', 'Name'])
            filters = [
                {
                    'field': 'Name',
                    'operator': 'EQUALS',
                    'values': ['account #1'],
                }
            ]
            >>> get_accounts(filters=filters)
        """

        name = 'ManagedCustomerService'
        if fields is None:
            # show all fields
            fields = ['Name', 'CustomerId', 'CanManageClients', 'CurrencyCode',
                      'DateTimeZone', 'TestAccount', 'AccountLabels']

        selector = {'fields': fields}

        pre_filters = [
            {
                'field': 'CanManageClients',
                'operator': 'EQUALS',
                'values': manage_clients,
            }
        ]

        if filters:
            for f in filters:
                pre_filters.append(f)
        selector['predicates'] = pre_filters
        return self.get_custom_service(name, selector)

    def get_campaigns(self, fields=None, filters=None):
        """
        Get all campaigns from `account_id` adwords account
        Args:
            fields (list): list of fields you want to get for each campaign
                           https://developers.google.com/adwords/api/docs/reference/v201609/CampaignService.Campaign
            filters (list): list of filters you want to filter by
                            https://developers.google.com/adwords/api/docs/reference/v201609/CampaignService.Predicate

        Yields:
            campaigns

        Examples:
            >>> get_campaigns(fields=['Id', 'Name', 'Status'])
            filters = [
                {
                    'field': 'Name',
                    'operator': 'EQUALS',
                    'values': ['campaign #1'],
                }
            ]
            >>> get_campaigns(filters=filters)
        """
        name = 'CampaignService'

        if fields is None:
            # show all fields
            fields = ['Id', 'Name', 'Status', 'ServingStatus', 'StartDate', 'EndDate',
                      'AdServingOptimizationStatus', 'Settings', 'AdvertisingChannelType',
                      'AdvertisingChannelSubType', 'Labels', 'CampaignTrialType', 'BaseCampaignId',
                      'TrackingUrlTemplate', 'UrlCustomParameters',
                      ]

        selector = {'fields': fields}

        if filters:
            selector['predicates'] = filters

        return self.get_custom_service(name, selector)

    def get_campaigns_by_status(self, fields=None, statuses=None):
        """
        Get campaigns from `account_id` adwords account based on statuses
        Args:
            fields (list): list of fields you want to get for each campaign
            statuses (list): list of statuses (PAUSED, ENABLED, ...)

        Yields:
            campaigns

        Examples:
            This example will return only campaings which have status PAUSED
            >>> get_campaigns_by_status(statuses=['PAUSED'])
        """

        filters = None
        if statuses:
            filters = [
                {
                    'field': 'Status',
                    'operator': 'IN',
                    'values': statuses,
                }
            ]
        return self.get_campaigns(fields=fields, filters=filters)

    def get_adgroups(self, campaign_ids, fields=None, filters=None):
        """
            Get all adgroups from `campaign_ids`
            Args:
                campaign_ids (list): list of campaign ids
                fields (list): list of fields you want to get for each adgroup
                               https://developers.google.com/adwords/api/docs/reference/v201609/AdGroupService.AdGroup
                filters (list): list of filters you want to filter by
                                https://developers.google.com/adwords/api/docs/reference/v201609/AdGroupService.Predicate

            Yields:
                adgroups

            Examples:
                >>> get_adgroups([1,2,3], fields=['Id', 'Name', 'Status'])
                filters = [
                    {
                        'field': 'Name',
                        'operator': 'EQUALS',
                        'values': ['adgroup #1'],
                    }
                ]
                >>> get_adgroups([1,2,3], filters=filters)
        """

        name = 'AdGroupService'

        if fields is None:
            # show all fields
            fields = ['Id', 'CampaignId', 'CampaignName', 'Name', 'Status', 'Settings',
                      'Labels', 'ContentBidCriterionTypeGroup',
                      'BaseCampaignId', 'BaseAdGroupId', 'TrackingUrlTemplate',
                      'UrlCustomParameters']

        selector = {'fields': fields}

        pre_filters = [
            {
                'field': 'CampaignId',
                'operator': 'EQUALS',
                'values': campaign_ids,
            }
        ]

        if filters:
            for f in filters:
                pre_filters.append(f)
        selector['predicates'] = pre_filters

        return self.get_custom_service(name, selector)

    def get_adgroups_by_status(self, campaign_ids, fields=None, statuses=None):
        """
            Get adgrups from `campaign_ids` based on statuses
            Args:
                campaign_ids (list): list of campaign ids
                fields (list): list of fields you want to get for each adgroup
                statuses (list): list of statuses (PAUSED, ENABLED, ...)

            Yields:
                adgroups

            Examples:
                This example will return only adgroups which have status PAUSED
                >>> get_adgroups_by_status([1,2,3], statuses=['PAUSED'])
        """
        filters = None
        if statuses:
            filters = [
                {
                    'field': 'Status',
                    'operator': 'IN',
                    'values': statuses,
                }
            ]

        return self.get_adgroups(campaign_ids, fields=fields, filters=filters)

    def get_ads(self, adgroup_ids, types=None, filters=None):
        """
            Get all ads from `adgroup_ids`
            Args:
                adgroup_ids (list): list of adgroup ids
                filters (list): list of filters you want to filter by
                                https://developers.google.com/adwords/api/docs/reference/v201609/AdGroupAdService.Predicate

            Yields:
                ads

            Examples:
                filters = [
                    {
                        'field': 'id',
                        'operator': 'EQUALS',
                        'values': [123456],
                    }
                ]
                >>> get_ads([1,2,3], filters=filters)
        """
        name = 'AdGroupAdService'

        fields = ['Id']

        selector = {'fields': fields}

        pre_filters = [
            {
                'field': 'AdGroupId',
                'operator': 'EQUALS',
                'values': adgroup_ids,
            }
        ]

        if types:
            pre_filters.append(
                {
                    'field': 'AdType',
                    'operator': 'EQUALS',
                    'values': types
                }
            )

        if filters:
            for f in filters:
                pre_filters.append(f)
        selector['predicates'] = pre_filters

        return self.get_custom_service(name, selector)

    def get_text_ads(self, adgroup_ids, filters=None):
        """
            Get all text ads from `adgroup_ids`
            Args:
                adgroup_ids (list): list of adgroup ids
                filters (list): list of filters you want to filter by
                                https://developers.google.com/adwords/api/docs/reference/v201609/AdGroupAdService.Predicate

            Yields:
                text ads
        """
        return self.get_ads(adgroup_ids, types=['TEXT_AD'], filters=filters)

    def get_text_ads_by_status(self, adgroup_ids, statuses=None):
        """
            Get text ads from `adgroup_ids` based on statuses
            Args:
                adgroup_ids (list): list of adgroup ids
                statuses (list): list of statuses (PAUSED, ENABLED, ...)

            Yields:
                text ads

            Examples:
                This example will return only text ads which have status PAUSED
                >>> get_text_ads_by_status([1,2,3], statuses=['PAUSED'])
        """
        filters = None
        if statuses:
            filters = [
                {
                    'field': 'Status',
                    'operator': 'IN',
                    'values': statuses,
                }
            ]

        return self.get_text_ads(adgroup_ids, filters=filters)

    def get_keywords(self, adgroup_ids, filters=None):
        """
            Get all keywords from `adgroup_ids`
            Args:
                adgroup_ids (list): list of adgroup ids
                filters (list): list of filters you want to filter by
                                https://developers.google.com/adwords/api/docs/reference/v201609/AdGroupCriterionService.Keyword

            Yields:
                keywords

            Examples:
                filters = [
                    {
                        'field': 'id',
                        'operator': 'EQUALS',
                        'values': [123456],
                    }
                ]
                >>> get_keywords([1,2,3], filters=filters)
        """

        name = 'AdGroupCriterionService'

        fields = ['Id']

        selector = {'fields': fields}

        pre_filters = [
            {
                'field': 'AdGroupId',
                'operator': 'EQUALS',
                'values': adgroup_ids,
            },
            {
                'field': 'CriterionUse',
                'operator': 'EQUALS',
                'values': 'BIDDABLE',
            },
            {
                'field': 'CriteriaType',
                'operator': 'EQUALS',
                'values': 'KEYWORD',
            }
        ]

        if filters:
            for f in filters:
                pre_filters.append(f)
        selector['predicates'] = pre_filters

        return self.get_custom_service(name, selector)

    def get_keywords_by_match_type(self, adgroup_ids, match_types=None):
        """
            Get all keywords from `adgroup_ids` based on match_types
            Args:
                adgroup_ids (list): list of adgroup ids
                match_types (list): list of match types (BROAD, PHRASE, EXACT)
                                https://developers.google.com/adwords/api/docs/reference/v201609/AdGroupCriterionService.Keyword

            Yields:
                keywords

            Examples:
                >>> get_keywords_by_match_type([1,2,3], match_types=['BROAD'])
        """

        filters = None
        if match_types:
            filters = [
                {
                    'field': 'KeywordMatchType',
                    'operator': 'IN',
                    'values': match_types,
                }
            ]

        return self.get_keywords(adgroup_ids, filters=filters)

    def get_keywords_by_status(self, adgroup_ids, statuses=None):
        """
            Get all keywords from `adgroup_ids` based on statuses
            Args:
                adgroup_ids (list): list of adgroup ids
                statuses (list): list of statuses (PAUSED, ENABLED, ...)
                                https://developers.google.com/adwords/api/docs/reference/v201609/AdGroupCriterionService.Keyword

            Yields:
                keywords

            Examples:
                >>> get_keywords_by_status([1,2,3], match_types=['PAUSED'])
        """

        filters = None
        if statuses:
            filters = [
                {
                    'field': 'Status',
                    'operator': 'IN',
                    'values': statuses,
                }
            ]

        return self.get_keywords(adgroup_ids, filters=filters)

    def set_adgroup_status(self, adgroup_id, status):

        name = 'AdGroupService'
        service = self.get_service(name)

        operations = [
            {
                'operator': 'SET',
                'operand': {
                    'id': adgroup_id,
                    'status': status,
                }
            }
        ]
        self._mutate_operation(service, operations)

    def set_ad_status(self, ad_group_id, ad_id, status):

        name = 'AdGroupAdService'
        service = self.get_service(name)

        operations = [
            {
                'operator': 'SET',
                'operand': {
                    'adGroupId': ad_group_id,
                    'status': status,
                    'ad': {
                        'id': ad_id
                    }
                }
            }
        ]
        self._mutate_operation(service, operations)

    def set_keyword_status(self, adgroup_id, keyword_id, status):

        name = 'AdGroupCriterionService'
        criterion_service = self.get_service(name)

        operations = [
            {
                'operator': 'SET',
                'operand': {
                    'xsi_type': 'BiddableAdGroupCriterion',
                    'adGroupId': adgroup_id,
                    'userStatus': status,
                    'criterion': {
                        'xsi_type': 'Keyword',
                        'id': keyword_id,
                    }
                }
            }
        ]
        self._mutate_operation(criterion_service, operations)

    def get_campaigns_changes(self, campaign_ids, start_date, end_date):
        """
            Get all changes for campaigns

            Args:
                campaign_ids (list): list of campaign ids
                start_date (str): date format %Y%m%d %H%M%S
                end_date (str): date format %Y%m%d %H%M%S

            Example:
                datetime.today().strftime('%Y%m%d %H%M%S')
        """

        name = 'CustomerSyncService'

        selector = {
            'dateTimeRange': {
                'min': start_date,
                'max': end_date
            },
            'campaignIds': campaign_ids,
        }

        changes = self.get_custom_service(name, selector, pagination=False)

        # this needs next, because we are yielding and not returning results
        return next(changes)

    def download_report_with_awql(self, path, query, report_format='CSV', skip_report_header=True,
                                  skip_column_header=True, skip_report_summary=True,
                                  include_zero_impressions=True):
        report_downloader = self.client.GetReportDownloader(version=self.version)
        with open(path, 'w') as output_file:
            report_downloader.DownloadReportWithAwql(
                query, report_format, output_file, skip_report_header=skip_report_header,
                skip_column_header=skip_column_header, skip_report_summary=skip_report_summary,
                include_zero_impressions=include_zero_impressions)
