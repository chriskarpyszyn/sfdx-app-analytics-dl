import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv
from pathlib import Path
import time

# todo move to config file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
sfdc_username = os.getenv('SFDC_USER_NAME')
sfdc_password = os.getenv('SFDC_PASSWORD')
sfdc_token = os.getenv('SFDC_TOKEN')
sfdc_package_ids = os.getenv('SFDC_PACKAGE_IDS')


def main():
    # login to salesforce
    sf_instance = Salesforce(username=sfdc_username, password=sfdc_password, security_token=sfdc_token, version=50.0)

    # get a comma delimited list of organization ids
    org_id_string = get_org_ids_string(sf_instance)

    # create the app analytics record and get the id
    id_of_analytics_record = create_app_analytic_record(sf_instance, sfdc_package_ids, org_id_string)

    # wait, get record w/ aws link
    csv_url = get_csv_url(sf_instance, id_of_analytics_record)
    print(csv_url)

    # save csv from aws


def get_csv_url(sf_instance, app_analytics_id):
    """
    Given an App Analytics record Id, poll Salesforce until the CSV is ready to be retrieved
    :param sf_instance:
    :param app_analytics_id:
    :return:
    """
    aaqr_record = sf_instance.AppAnalyticsQueryRequest.get(app_analytics_id)
    request_state = aaqr_record.get('RequestState')
    while request_state == 'New' or request_state == 'Pending':
        print(request_state)
        print('waiting')
        time.sleep(5)

    csv_url = aaqr_record.get('DownloadUrl')
    return csv_url


def create_app_analytic_record(sf_instance, packageIds, organizationIds):
    """
    Create a Package Usage Log App Analytics Query Request for the previous day
    :param sf_instance
    :param packageIds:
    :param organizationIds:
    :return: the id of the successfully created record
    """

    # todo set date string to yesterday
    app_analytics_response = sf_instance.AppAnalyticsQueryRequest.create({
        'DataType': 'PackageUsageLog',
        'StartTime': '2021-03-01T00:00:00',
        'EndTime': '2021-03-01T23:59:59',
        'PackageIds': packageIds,
        'OrganizationIds': organizationIds
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
    # todo extract the hardcoded variable
    where_condition = "WHERE sfLma__Package_Version__r.Name LIKE 'v%1.%'" + " AND sfLma__Is_Sandbox__c = FALSE"
    data = sf_instance.query("SELECT sfLma__Subscriber_Org_ID__c FROM sfLma__License__c " + where_condition)

    org_ids = set()
    for k, v in data.items():
        if k == "records":
            for item in v:
                org_ids.add(item.get('sfLma__Subscriber_Org_ID__c'))

    org_ids_string = ','.join(str(s) for s in org_ids)
    return org_ids_string


main()
