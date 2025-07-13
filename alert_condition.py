import os
import json
import requests
import time

from list_all_alerts import *
from keys import get_keys


def fetch_conditions(endpoint, headers):
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.json())
        print(f"Failed to fetch conditions: {response.status_code}")
        return None


def extract_conditions(alert_type, conditions):
    if alert_type == "Infrastructure":
        return conditions.get("data", [])
    elif alert_type == "NRQL":
        return conditions.get("nrql_conditions", [])
    elif alert_type == "MultiLocationSynthetics":
        return conditions.get("location_failure_conditions", [])
    elif alert_type == "Synthetics":
        return conditions.get("synthetics_conditions", [])
    return []


def list_alert_conditions(key, policy_id):
    alert_conditions = []
    endpoints = {
        "APM": f"https://api.newrelic.com/v2/alerts_conditions.json?policy_id={policy_id}",
        "NRQL": f"https://api.newrelic.com/v2/alerts_nrql_conditions.json?policy_id={policy_id}",
        "Synthetics": f"https://api.newrelic.com/v2/alerts_synthetics_conditions.json?policy_id={policy_id}",
        "MultiLocationSynthetics": f"https://api.newrelic.com/v2/alerts_location_failure_conditions/policies/{policy_id}.json",
        "Infrastructure": f"https://infra-api.newrelic.com/v2/alerts/conditions?policy_id={policy_id}"
    }

    headers = {'Api-Key': key}

    for alert_type, endpoint in endpoints.items():
        conditions = fetch_conditions(endpoint, headers)
        if conditions:
            conditions_list = extract_conditions(alert_type, conditions)
            for condition in conditions_list:
                if isinstance(condition, dict):
                    
                    alert_conditions.append({
                        "policyId": policy_id,
                        "type": alert_type,
                        "id": condition.get("id"),
                        "name": condition.get("name"),
                        "enabled": condition.get("enabled", True),
                        "runbook_url": condition.get("runbook_url", ""),
                        "terms": condition.get("terms", []),
                        "entities": condition.get("entities", []),
                        "event_type": condition.get("event_type", ""),
                        "nrql": condition.get("nrql")
                    })
    return alert_conditions


def list_all_alert_conditions(key,sub_account_keys):
    accounts=get_accounts(key)
    
    policies = nerdgraph_list_policies(accounts,key)  # Fetch policies using the existing function
    all_alert_conditions = dict()

    for account in accounts:
        
        
        
        session=requests.Session()
         
        if all_alert_conditions.get(account['id']) is None:
                    all_alert_conditions[account['id']]=dict()
        
        if policies.get(account['id']) is None:
             continue

        policy_list=policies[account['id']]
        
        for policy in policy_list:

            if all_alert_conditions[account['id']].get(policy['name']) is None:
                    
                    all_alert_conditions[account['id']][policy['name']]=[]

            policy_id=policy['id']
             
            # print("-------------\n")
            # print(f"{account['id']} {account['name']}  :  {policy_id}")
            # print("-------------\n")
            sub_account=str(account['id'])
            account_key=sub_account_keys[sub_account]['key']
            #print(account_key)
            conditions = list_alert_conditions(account_key, policy_id)
            
            for condition in conditions:
                guid=get_alert_condition_guid(condition['name'],account['id'],key,session)
                
                 
                all_alert_conditions[account['id']][policy['name']].append(
                    {
                        'condition_name' : condition['name'],
                        'guid'           : guid,
                        'id'             : condition['id'],
                        
                        'condition_type' : condition['type'],
                        'policy_id'      : condition['policyId'],
                        'policy_name'    : policy['name'],
                        'account_ID'     : account['id'],
                        'condition_type' : condition['type'],
                        'runbook_url'    : condition['runbook_url'],
                        'account_name'   : account['name']


                    }
                )

                if condition['nrql']:
                     last_index=len(all_alert_conditions[account['id']][policy['name']])
                     all_alert_conditions[account['id']][policy['name']][last_index-1]['query']=condition['nrql']['query']
                     
           

        
  
    return all_alert_conditions


if __name__ == "__main__":
        
      

        sub_account_keys=get_keys()

        key=sub_account_keys['2330551']['key']

        alerts=list_all_alert_conditions(key,sub_account_keys)

        
        for account in alerts.keys():
             print(account)
             print("Number of Policies  : ",len(alerts[account].keys()))

             for policy_name in alerts[account].keys():
                  print("Policy Name : ",policy_name)
                  print("Number of conditions : ",len(alerts[account][policy_name]))
             print("--------------------------------------------------")


        #print(json.dumps(alerts,indent=1))




