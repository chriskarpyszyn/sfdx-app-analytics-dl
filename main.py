import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv
from pathlib import Path

# todo move to config file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
sfdc_username = os.getenv('SFDC_USER_NAME')
sfdc_password = os.getenv('SFDC_PASSWORD')
sfdc_token = os.getenv('SFDC_TOKEN')


def main():
    # login to salesforce
    sf_instance = Salesforce(username=sfdc_username, password=sfdc_password, security_token=sfdc_token)

    # get a list of org ids

    # create app analytics query request

    # wait, get record w/ aws link

    # save csv from aws
