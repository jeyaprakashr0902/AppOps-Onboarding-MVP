import os
import json
import requests
import time


from alert_condition import *
from keys import get_keys

def update_tags(key,guid,tag_key,tag_value):

   query=""" mutation {
        taggingAddTagsToEntity(
                    guid: "%s",
                    tags: [{ key: %s, values: [%s] }]
                ) 
                
                {
                    errors { message type }
                }
    }
    """(guid,tag_key,tag_value)
   endpoint = "https://api.newrelic.com/graphql"
   headers = {'API-Key': f'{key}'}
   response = requests.post(endpoint, headers=headers, json={"query": query})
   print(response.json())



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
                   
                   if data.get('tags') is None:
                        continue
                   
                   for tag in data['tags']:
                        for tag_key in tag.keys():
                              
                              account_key=sub_account_keys[str(data['account_ID'])]['key']
                              guid=condition['guid']
                              update_tags(account_key,guid,tag_key,tag[tag_key])
                        

