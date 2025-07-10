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



def update_tags(key):

   query=""" mutation {
        taggingAddTagsToEntity(
                    guid: "Njc2MTA5N3xBSU9QU3xDT05ESVRJT058NTI0MDkyMTA",
                    tags: [{ key: "owner", values: ["JP"] }]
                ) 
                
                {
                    errors { message type }
                }
    }
    """
   endpoint = "https://api.newrelic.com/graphql"
   headers = {'API-Key': f'{key}'}
   response = requests.post(endpoint, headers=headers, json={"query": query})
   print(response.json())





#accounts=get_accounts(sandbox_key)
#alert_conditions=list_all_alert_conditions(sandbox_key)




#update_tags(user_key)

