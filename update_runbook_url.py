import os
import requests
from alert_condition import *

from keys import get_keys




def update_classic_alert(api_key,condition,new_runbook_url):
    
    

                    headers = {
                        "Api-Key": api_key,
                        "Content-Type": "application/json"
                    }

                    endpoints = {
                        "APM": "https://api.newrelic.com/v2/alerts_conditions/{condition_id}.json",
                        "NRQL": "https://api.newrelic.com/v2/alerts_nrql_conditions/{condition_id}.json",
                        "Synthetics": "https://api.newrelic.com/v2/alerts_synthetics_conditions/{condition_id}.json",
                        "MultiLocationSynthetics": "https://api.newrelic.com/v2/alerts_location_failure_conditions/{condition_id}.json",
                        "Infrastructure": "https://infra-api.newrelic.com/v2/alerts/conditions/{condition_id}"
                    }

    
                    condition_id = condition.get("id")
                    alert_type=condition.get('condition_type')
                    endpoint = endpoints[alert_type].format(condition_id=condition_id)

                    if alert_type == "NRQL":
                        update_nrql_condition(api_key, condition, new_runbook_url)
                    else:
                        update_other_conditions(endpoint, headers, condition, new_runbook_url, alert_type)


def update_nrql_condition(api_key, condition, new_runbook_url):
    """
    Update the runbook URL for nrql alerts in a given policy.
    """
    nrql_condition_id = condition["id"]
    nrql_condition_type = condition["condition_type"]
    nrql_account_id = condition["account_ID"]
    update_nrql_alert_nerdgraph(api_key, nrql_condition_id, nrql_condition_type, nrql_account_id, new_runbook_url)


def update_other_conditions(endpoint, headers, condition, new_runbook_url, alert_type):
    """
    Update the runbook URL for other alert conditions in a given policy.
    """
    payload = {alert_type.lower() + "_condition": condition}
    payload[alert_type.lower() + "_condition"]["runbook_url"] = new_runbook_url

    response = requests.put(endpoint, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Successfully updated runbook URL for condition '{condition.get('name')}' (ID: {condition.get('id')})")
    else:
        print(
            f"Failed to update runbook URL for condition '{condition.get('name')}' "
            f"(ID: {condition.get('id')}): {response.status_code} - {response.text}"
        )


def update_nrql_alert_nerdgraph(api_key, condition_id, condition_type, nrql_account_id, new_runbook_url):
    """
    Update the runbook URL for nrql alerts in a given policy.

    Args:
        api_key (str): New Relic API key.
        policy_id (str): ID of the alert policy.
        new_runbook_url (str): New runbook URL to set.

    Returns:
        None
    """
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    mutation=None
    # GraphQL mutation to update the NRQL alert condition
    
    base_line_condition_query= """
                mutation UpdateNrqlConditionBaseline($conditionId: ID!, $nrqlAccountId: Int!, $runbookUrl: String!) {
                    alertsNrqlConditionBaselineUpdate(
                        id: $conditionId,
                        accountId: $nrqlAccountId,
                        condition: {
                            runbookUrl: $runbookUrl
                        }
                    ) {
                        id
                        name
                        baselineDirection
                    }
                }
            """
                
    
    static_condition_query = """
        mutation UpdateNrqlConditionStatic($conditionId: ID!, $nrqlAccountId: Int!, $runbookUrl: String!) {
            alertsNrqlConditionStaticUpdate(
                id: $conditionId,
                accountId: $nrqlAccountId,
                condition: {
                    runbookUrl: $runbookUrl
                }
            ) {
                id
                name
            }
        }
        """

    # Payload for the GraphQL request
    payload_for_baseline = {
        "query": base_line_condition_query,
        "variables": {
            "conditionId": condition_id,
            "runbookUrl": new_runbook_url,
            "nrqlAccountId": nrql_account_id
        }
    }
     
    payload_for_static = {
        "query": static_condition_query,
        "variables": {
            "conditionId": condition_id,
            "runbookUrl": new_runbook_url,
            "nrqlAccountId": nrql_account_id
        }
    }

    # Send the GraphQL request
    response = requests.post(
        "https://api.newrelic.com/graphql",
        headers=headers,
        json=payload_for_baseline if condition_type == "baseline" else payload_for_static
    )

    # Handle the response
    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"Failed to update NRQL condition: {data['errors']}")
        else:
            if condition_type == "baseline":
                updated_condition = data.get("data", {}).get("alertsNrqlConditionBaselineUpdate", {})
            else:
                updated_condition = data.get("data", {}).get("alertsNrqlConditionStaticUpdate", {})
            print(
                f"Successfully updated NRQL condition '{updated_condition.get('name')}' "
                f"(ID: {updated_condition.get('id')})"
            )
    else:
        print(f"Failed to update NRQL condition: {response.status_code} - {response.text}")


if __name__ == "__main__":
    
    sub_account_keys=get_keys()

    key=sub_account_keys['2330551']['key']
    
    alert_conditions = list_all_alert_conditions(key,sub_account_keys)

    with open("input.json", "r", encoding="utf-8") as f:
         input_json= json.load(f)

    print(input_json)

    for data in input_json:
         

         condition_list=alert_conditions[int(data['account_ID'])]['policy_name']

         for condition in condition_list:
              
              if condition['id']==data['condition_ID']:
                   
                   if data.get('runbook_url') is None:
                        continue
                   
                   new_runbook_url=data['runbook_url']
                   account_key=sub_account_keys[str(data['account_ID'])]['key']
                   update_classic_alert(account_key,condition,new_runbook_url)
    
   
