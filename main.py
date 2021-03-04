import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv
from pathlib import Path
import time
from datetime import datetime, timedelta
import urllib.request

# todo move to config file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
sfdc_username = os.getenv('SFDC_USER_NAME')
sfdc_password = os.getenv('SFDC_PASSWORD')
sfdc_token = os.getenv('SFDC_TOKEN')
sfdc_package_ids = os.getenv('SFDC_PACKAGE_IDS')
output_path = os.getenv('OUTPUT_PATH')


def main():
    yesterday = datetime.now() - timedelta(1)
    yesterday_string = datetime.strftime(yesterday, '%Y-%m-%d')

    # login to salesforce
    sf_instance = Salesforce(username=sfdc_username, password=sfdc_password, security_token=sfdc_token, version=50.0)

    # get a comma delimited list of organization ids
    all_org_ids_string = get_org_ids_string(sf_instance)

    # string into list
    list_of_org_ids = all_org_ids_string.split(",")

    # create a list of lists with 15 ids.
    # todo extract to method, remove hardcoded 15
    list_of_org_id_strings = []
    index_of_list = -1
    for i in range(0, len(list_of_org_ids)):
        if i % 15 == 0:
            index_of_list = index_of_list + 1
            list_of_org_id_strings.append([])
        # list_of_org_id_strings[index_of_list].append(list_of_org_ids[i])
        list_of_org_id_strings[index_of_list] += [list_of_org_ids[i]]

    for i in range(0, len(list_of_org_id_strings)):
        # create the app analytics record and get the id
        id_of_analytics_record = create_app_analytic_record(sf_instance, sfdc_package_ids, list_of_org_id_strings[i], yesterday_string)

        # wait, get record w/ aws link
        csv_url = get_csv_url(sf_instance, id_of_analytics_record)

        # save csv from aws
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        urllib.request.urlretrieve(csv_url, f'{output_path}/{yesterday_string}_platform_analytics_{i}.csv')


def get_csv_url(sf_instance, app_analytics_id):
    """
    Given an App Analytics record Id, poll Salesforce until the CSV is ready to be retrieved
    :param sf_instance:
    :param app_analytics_id:
    :return:
    """
    request_state = get_request_state(sf_instance, app_analytics_id)
    while request_state == 'New' or request_state == 'Pending':
        print(request_state)
        time.sleep(5)
        request_state = get_request_state(sf_instance, app_analytics_id)

    csv_url = get_download_url(sf_instance, app_analytics_id)
    return csv_url


def get_request_state(sf_instance, record_id):
    aaqr_record = sf_instance.AppAnalyticsQueryRequest.get(record_id)
    return aaqr_record.get('RequestState')


def get_download_url(sf_instance, record_id):
    aaqr_record = sf_instance.AppAnalyticsQueryRequest.get(record_id)
    return aaqr_record.get('DownloadUrl')


def create_app_analytic_record(sf_instance, package_ids, organization_ids, date_string):
    """
    Create a Package Usage Log App Analytics Query Request for the previous day
    :param date_string:
    :param sf_instance
    :param package_ids:
    :param organization_ids:
    :return: the id of the successfully created record
    """

    comma_delimited_string = ','.join(str(s) for s in organization_ids)

    app_analytics_response = sf_instance.AppAnalyticsQueryRequest.create({
        'DataType': 'PackageUsageLog',
        'StartTime': f'{date_string}T00:00:00',
        'EndTime': f'{date_string}T23:59:59',
        'PackageIds': package_ids,
        'OrganizationIds': comma_delimited_string
    })

    # todo check if successful
    return app_analytics_response.get('id')


def get_org_ids_string(sf_instance):
    """
    query salesforce to get a comma delimited string of org ids
    :param sf_instance: the sf instance to query from
    :return: comma delimited string of org ids
    """
    # this where condition is specific to my use case.
    where_condition = "WHERE sfLma__Package_Version__r.Name LIKE 'v%1.%'"
    data = sf_instance.query("SELECT sfLma__Subscriber_Org_ID__c FROM sfLma__License__c " + where_condition)

    org_ids = set()
    for k, v in data.items():
        if k == "records":
            for item in v:
                org_ids.add(item.get('sfLma__Subscriber_Org_ID__c'))

    org_ids_string = ','.join(str(s) for s in org_ids)
    return org_ids_string


main()
