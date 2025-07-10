import os
import json
import requests
import time

from list_all_alerts import *



def get_api_key():
    """
    Retrieve the API key from an environment variable.
    Returns:
        str: The API key.
    """
    api_key = os.environ.get("MEP_NEW_RELIC_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please set the NEW_RELIC_API_KEY environment variable.")
    return api_key


def get_condition_type(account_id,key):
    

    query="""
           {
                    actor {
                        account(id: %s) {
                        alerts {
                            nrqlConditionsSearch {
                            nextCursor
                            nrqlConditions {
                                id                               
                                name
                                policyId
                                runbookUrl
                                type
                            }
                            totalCount
                            }
                        }
                        }
                    }
            }

    """% account_id

    url = "https://api.newrelic.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "API-Key": key,
    }

    response = requests.post(url, headers=headers, json={"query": query})
    print(response.json())

def update_runbook_url(account_id,key, condition_id, new_runbook_url):
    url = "https://api.newrelic.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "API-Key": key,
    }

    



    query="""

         mutation {
            alertsNrqlConditionStaticUpdate(
                id: %s
                accountId: %d
                condition: {runbookUrl: "%s"}
            ) {
                id
                name
             
            }
     }

     """% (condition_id, account_id,new_runbook_url)

    response = requests.post(url, headers=headers, json={"query": query})
    
    if response.status_code == 200:
        print("Runbook URL updated successfully:")
        print(response.json())
    else:
        print("Failed to update runbook URL:")
        print(response.status_code, response.text)
account_id=None
update_runbook_url(account_id,user_key,"<str : condition_id>","<runbook_url")
user_key=get_api_key()
#get_condition_type(3062828,user_key)