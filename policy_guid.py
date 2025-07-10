def get_policy_guids(accounts,key):

     policy_guid_list = dict()

     

     for account in accounts:
         
         
         session=requests.Session()
         
         next_cursor=None
         
         query="""
                {
                        actor {
                            entitySearch(query: "domain='AIOPS' AND type='POLICY' AND accountId=%s") {
                            results {
                                entities {
                                    guid
                                    domain
                                    type
                                    accountID
                                    name
                                }
                                nextCursor
                              }
                            }
                        }
          }


         """%account['id']


         
         query_with_cursor="""

              {
                        actor {
                            entitySearch(query: "domain='AIOPS' AND type='POLICY' AND accountId=%s") {
                            results(cursor:%s) {
                                entities {
                                    guid
                                    domain
                                    type
                                    accountID
                                    name
                                }
                                nextCursor
                              }
                            }
                        }
          }
         """%(account['id'],next_cursor)

         

         endpoint = "https://api.newrelic.com/graphql"
         headers = {'API-Key': f'{key}'}
         

         while True:
            
            if next_cursor:

                  response = session.post(endpoint, headers=headers, json={"query": query_with_cursor})
                  time.sleep(2)

            else:
                response = session.post(endpoint, headers=headers, json={"query": query})
                time.sleep(2)

            if response.status_code == 200:
                response=response.json()
                #print(response)
                next_cursor=response['data']['actor']['entitySearch']['results']['nextCursor']
                policies = response['data']['actor']['entitySearch']['results']['entities']
                for policy in policies:
                  if policy_guid_list.get(policy['accountID'])==None:
                      policy_guid_list[policy['accountID']]=list()
                  policy_guid_list[policy['accountID']].append(
                       {
                           'guid':policy['guid'],
                           'policy_name':policy['name'],
                           'domain':policy['domain'],
                           'type':policy['type']
                       }
                  )

                if not next_cursor:
                    break
            else:
                raise requests.exceptions.HTTPError(f'Nerdgraph query failed with a {response.status_code}.')

     return policy_guid_list

