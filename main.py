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


def main():
    # login to salesforce
    sf_instance = Salesforce(username=sfdc_username, password=sfdc_password, security_token=sfdc_token, version=50.0)

    org_id_string = get_org_ids_string(sf_instance)

    # create app analytics query request
    # todo refactor into method
    # todo parameterize create request
    app_analytics_response = sf_instance.AppAnalyticsQueryRequest.create({
        'DataType': 'PackageUsageLog',
        'StartTime': '2021-03-01T00:00:00',
        'EndTime': '2021-03-01T23:59:59',
        'PackageIds': '033',
        'OrganizationIds': '00D'
    })
    # todo check if successful
    id_of_analytics_record = app_analytics_response.get('id')

    # wait, get record w/ aws link
    # todo refactor into method
    app_data = sf_instance.AppAnalyticsQueryRequest.get(id_of_analytics_record)
    request_state = app_data.get('RequestState')
    while request_state == 'New' or request_state == 'Pending':
        print(request_state)
        print('waiting')
        time.sleep(5)

    csv_url = app_data.get('DownloadUrl')
    print(csv_url)

    # save csv from aws


def get_org_ids_string(sf_instance):
    """
    query salesforce to get a comma delimited string of org ids
    :param sf_instance: the sf instance to query from
    :return: comma delimited string of org ids
    """
    # this where condition is specific to my use case.
    # todo extract the hardcoded variable
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
