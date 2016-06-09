# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import suds

from datetime import datetime, timedelta

from googleads import adwords, oauth2


class RetriesLimitException(Exception):
    def __init__(self, retries):
        Exception.__init__(self, 'Tried to get service {} times, but failed.'.format(retries))


class AdwordsAPI(object):
    def __init__(self, account_id, client_id, client_secret, refresh_token, developer_token,
                 version='v201603', page_size=100, retries=3):
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
            self.account_id)

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
                        time.sleep(2 ** tries)
                    elif error['ApiError.Type'] == 'RateExceededError':
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
                            time.sleep(2 ** tries)
                        elif error['ApiError.Type'] == 'RateExceededError':
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

    def get_accounts(self, fields=None, filters=None):
        """
        Get all adwords accounts associated with `account_id`
        Args:
            fields (list): list of fields you want to get for each account
                           https://developers.google.com/adwords/api/docs/reference/v201605/ManagedCustomerService.ManagedCustomer
            filters (list): list of filters you want to filter by
                            https://developers.google.com/adwords/api/docs/reference/v201605/ManagedCustomerService.Predicate

        Yields:
            adwords accounts

        Examples:
            >>> get_accounts(fields=['CustomerId', 'Name'], filters=filters)
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
            fields = ['Name', 'CompanyName', 'CustomerId', 'CanManageClients', 'CurrencyCode',
                      'DateTimeZone', 'TestAccount', 'AccountLabels']

        selector = {'fields': fields}

        if filters:
            selector['predicates'] = filters
        return self.get_custom_service(name, selector)

    def get_campaigns(self, fields=None, filters=None):
        """
        Get all campaigns from `account_id` adwords account
        Args:
            fields (list): list of fields you want to get for each campaign
                           https://developers.google.com/adwords/api/docs/reference/v201605/CampaignService.Campaign
            filters (list): list of filters you want to filter by
                            https://developers.google.com/adwords/api/docs/reference/v201605/CampaignService.Predicate

        Yields:
            campaigns

        Examples:
            >>> get_campaigns(fields=['Id', 'Name', 'Status'], filters=filters)
            filters = [
                {
                    'field': 'Name',
                    'operator': 'EQUALS',
                    'values': ['account #1'],
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
            Yields all ad groups from campaign_ids
        """
        name = 'AdGroupService'

        if fields is None:
            # default field
            fields = ['Id']

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
            Yields all ad groups from campaign_ids
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

    def get_ads(self, adgroup_ids, types=None, fields=None, filters=None):
        name = 'AdGroupAdService'

        if fields is None:
            # default field
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

    def get_text_ads(self, adgroup_ids, fields=None, filters=None):
        return self.get_ads(adgroup_ids, types=['TEXT_AD'], fields=fields, filters=filters)

    def get_text_ads_by_status(self, adgroup_ids, fields=None, statuses=None):
        """
            Yields all ad groups from campaign_ids
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

        return self.get_text_ads(adgroup_ids, fields=fields, filters=filters)

    def get_keywords(self, adgroup_ids, fields=None, filters=None):

        name = 'AdGroupCriterionService'

        if fields is None:
            # default field
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

    def get_keywords_by_status(self, adgroup_ids, fields=None, statuses=None):

        filters = None
        if statuses:
            filters = [
                {
                    'field': 'Status',
                    'operator': 'IN',
                    'values': statuses,
                }
            ]

        return self.get_keywords(adgroup_ids, fields=fields, filters=filters)

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
        """

        name = 'CustomerSyncService'

        # TODO REMOVE!!!
        end_date = datetime.today().strftime('%Y%m%d %H%M%S')
        start_date = (datetime.today() - timedelta(1)).strftime('%Y%m%d %H%M%S')

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
