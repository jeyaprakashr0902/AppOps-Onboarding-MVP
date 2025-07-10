import os
import json
import requests
import time



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

sandbox_key="NRAK-YJZYPI2LDDKRX9U5EYO9MA2WRFQ"

def get_accounts(key):
    
    query = """
    {
    actor {
        accounts(scope: GLOBAL) {
        id
        name
        
        }
    }
    }"""



    
    endpoint = "https://api.newrelic.com/graphql"
    headers = {'API-Key': f'{key}'}
    response = requests.post(endpoint, headers=headers, json={"query": query})
    #print(response.json())

    if response.status_code == 200:
        
        account_list = [] 
        for account in response.json()['data']['actor']['accounts']:
            account_id = account['id']
            
            
            account_name = account['name']
            if 'storage account' not in account_name.lower():
                account_list.append({"id": account_id, "name": account_name})
    else:
        
        raise requests.exceptions.HTTPError(f'Nerdgraph query failed with a {response.status_code}.')
    print("Number of accounts : ",len(account_list))
    #print(account_list)
    return account_list



def nerdgraph_list_policies(accounts,key):
    
    policy_list = dict()

    session=requests.Session()
    for account in accounts:

        
        
        next_cursor=None
       

        query = """
        {
        actor {
            account(id: """ + str(account['id']) + """) {
            alerts {
                policiesSearch {
                nextCursor
                policies {
                    id
                    name
                    incidentPreference
                    accountId
                    
                }
                totalCount
                }
            }
            }
        }
        }"""
        endpoint = "https://api.newrelic.com/graphql"
        headers = {'API-Key': f'{key}'}

        

        query_with_cursor="""

        {
            actor {
                account(id: %s) {
                alerts {
                    policiesSearch(cursor: "%s") {
                    nextCursor
                    policies {
                        id
                        name
                        incidentPreference
                        accountId
                    }
                    totalCount
                    }
                  }
                }
            }
        }
        """ % (str(account['id']),next_cursor)

        
        while True:
            
            if next_cursor:

                  response = session.post(endpoint, headers=headers, json={"query": query_with_cursor})
                  

            else:
                response = session.post(endpoint, headers=headers, json={"query": query})
                

            if response.status_code == 200:
                response=response.json()
                #print(response)
                if response['data']['actor']['account'] is None:
                    print(account['id'])
                    break
                next_cursor=response['data']['actor']['account']['alerts']['policiesSearch']['nextCursor']
                policies = response['data']['actor']['account']['alerts']['policiesSearch']['policies']
                for policy in policies:
                    if policy_list.get(account['id']) is None:
                        policy_list[account['id']]=list()
                    policy_list[account['id']].append({
                        "accountName": account['name'],
                        "accountId": account['id'],
                        "id": policy['id'],
                        "name": policy['name'],
                        "incidentPreference": policy['incidentPreference']
                    })
               

                if not next_cursor:
                    break
            else:
                raise requests.exceptions.HTTPError(f'Nerdgraph query failed with a {response.status_code}.')
    
    return policy_list



def get_alert_condition_guid(condition_name,account_id,key,session):

    condition_name = condition_name.replace("'", "\\'")
    query = f"""
                {{
                actor {{
                    entitySearch(query: "name = '{condition_name}' AND accountId = {account_id} AND type = 'CONDITION'") {{
                    results {{
                        entities {{
                        guid
                        name
                        type
                        domain
                        }}
                    }}
                    }}
                }}
                }}
                """



    endpoint = "https://api.newrelic.com/graphql"
    headers = {'API-Key': f'{key}'}
    response = session.post(endpoint, headers=headers, json={"query": query})
    #print(response.json())
    condition=response.json()
    guid=condition['data']['actor']['entitySearch']['results']['entities'][0]['guid']
    return guid








if __name__ == "__main__":
    user_key = get_api_key()

    

    accounts=get_accounts(user_key)
    policies=nerdgraph_list_policies(accounts,user_key)

    

    # alert_conditions=get_alert_conditions(sandbox_key)

    # for accounts in alert_conditions.keys():
    #     print(accounts)
    #     print("Number of Polices : ", len(alert_conditions[accounts].keys()))
    #     for policies in alert_conditions[accounts].keys():
    #         print(f'Number of conditions in the policy {policies} : ',len(alert_conditions[accounts][policies]))
    #         print("\n")
    #     print("---------------------\n")

    # print(json.dumps(accounts,indent=1))
    #print(json.dumps(policies,indent=1))

  

    