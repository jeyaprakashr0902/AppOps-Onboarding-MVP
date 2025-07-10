import requests
import json
import os
import csv
import time # Import the time module for delays

# --- Configuration ---
# Get these from your New Relic account.
# It's highly recommended to store these securely, e.g., in environment variables.
# Example environment variable setup (in your shell before running the script):
# export NEW_RELIC_ACCOUNT_ID="YOUR_PARENT_ACCOUNT_ID"
# export NEW_RELIC_USER_KEY="NRAK-YOUR_NEW_RELIC_USER_KEY"
# The NEW_RELIC_ACCOUNT_ID here will be used for the initial query to fetch all accessible accounts.
# Ensure this account ID is associated with a user key that has access to all desired sub-accounts.
NEW_RELIC_ACCOUNT_ID = os.getenv("NEW_RELIC_ACCOUNT_ID", "2330551")
NEW_RELIC_USER_KEY = os.getenv("NEW_RELIC_USER_KEY", "NRAK-DPOVVT1VXRZWE2T6PD2968Y4NAR")

# New Relic NerdGraph API endpoint (adjust for EU accounts if applicable)
# For US accounts:
NEW_RELIC_GRAPHQL_ENDPOINT = "https://api.newrelic.com/graphql"
# For EU accounts:
# NEW_RELIC_GRAPHQL_ENDPOINT = "https://api.eu.newrelic.com/graphql"

# The NRQL query you want to execute for each account.
# Note: accountId() in the NRQL is good, as it adds the account ID to each result row.
NRQL_QUERY_TEMPLATE = "SELECT sum(GigabytesIngested) FROM NrConsumption SINCE this month FACET productLine, usageMetric, accountId()"

# Output CSV file name
OUTPUT_CSV_FILE = "newrelic_all_accounts_consumption.csv"

# Delay between API calls to avoid rate limits (in seconds)
API_CALL_DELAY = 0.5

# --- Function to get all accessible account IDs ---
def get_accessible_account_ids(graphql_endpoint, user_key):
    """
    Fetches all account IDs and names accessible by the provided User Key.
    """
    query = """
    {
      actor {
        accounts {
          id
          name
        }
      }
    }
    """
    headers = {
        "Content-Type": "application/json",
        "Api-Key": user_key
    }

    print("Fetching accessible New Relic account IDs...")
    try:
        response = requests.post(
            graphql_endpoint,
            headers=headers,
            json={"query": query}
        )
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            print("Error fetching account IDs:")
            for error in data["errors"]:
                print(f"- {error['message']}")
            return []
        
        accounts = data.get("data", {}).get("actor", {}).get("accounts", [])
        print(f"Found {len(accounts)} accessible accounts.")
        return accounts
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching account IDs: {e}")
        return []
    except json.JSONDecodeError:
        print("Failed to decode JSON response while fetching account IDs.")
        print(response.text)
        return []

# --- Main script execution ---
def main():
    if not NEW_RELIC_ACCOUNT_ID or not NEW_RELIC_USER_KEY or \
       NEW_RELIC_ACCOUNT_ID == "YOUR_NEW_RELIC_ACCOUNT_ID" or \
       NEW_RELIC_USER_KEY == "YOUR_NEW_RELIC_USER_KEY":
        print("Error: Please set NEW_RELIC_ACCOUNT_ID and NEW_RELIC_USER_KEY "
              "environment variables or replace the placeholders in the script.")
        return
    # Get all accessible accounts
    accounts = get_accessible_account_ids(NEW_RELIC_GRAPHQL_ENDPOINT, NEW_RELIC_USER_KEY)
    if not accounts:
        print("No accessible accounts found or an error occurred. Exiting.")
        return

    all_nrql_results = []
    # Collect all unique headers across all queries
    all_headers = set()

    for account in accounts:
        account_id = account['id']
        account_name = account.get('name', 'N/A')
        print(f"\n--- Querying account: {account_name} (ID: {account_id}) ---")

        # Construct the GraphQL query for the current account
        graphql_query_for_account = f"""
        {{
          actor {{
            account(id: {account_id}) {{
              nrql(query: "{NRQL_QUERY_TEMPLATE}") {{
                results
              }}
            }}
          }}
        }}
        """

        headers = {
            "Content-Type": "application/json",
            "Api-Key": NEW_RELIC_USER_KEY
        }

        try:
            response = requests.post(
                NEW_RELIC_GRAPHQL_ENDPOINT,
                headers=headers,
                json={"query": graphql_query_for_account}
            )
            response.raise_for_status()

            data = response.json()

            if "errors" in data:
                print(f"New Relic API returned errors for account {account_id}:")
                for error in data["errors"]:
                    print(f"- {error['message']}")
            elif data and "data" in data and "actor" in data["data"] and \
                    "account" in data["data"]["actor"] and "nrql" in data["data"]["actor"]["account"]:
                nrql_results_for_account = data["data"]["actor"]["account"]["nrql"]["results"]

                if not nrql_results_for_account:
                    print(f"No results returned for account {account_id}.")
                else:
                    # Add account_name to each result if not already present
                    # and update all_headers
                    for result_row in nrql_results_for_account:
                        result_row['query_account_id'] = account_id
                        result_row['query_account_name'] = account_name
                        all_nrql_results.append(result_row)
                        all_headers.update(result_row.keys()) # Collect all unique keys for headers

            else:
                print(f"Unexpected response format for account {account_id}:")
                print(json.dumps(data, indent=2))

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while querying account {account_id}: {e}")
        except json.JSONDecodeError:
            print(f"Failed to decode JSON response for account {account_id}.")
            print(response.text)
        except Exception as e:
            print(f"An unexpected error occurred for account {account_id}: {e}")

        # Pause to prevent rate limiting
        time.sleep(API_CALL_DELAY)

    # --- Write all collected results to CSV ---
    if not all_nrql_results:
        print("\nNo data collected from any account. CSV will not be created.")
        return

    # Ensure consistent order of headers
    final_headers = sorted(list(all_headers))

    # Prioritize certain headers for better readability
    preferred_order = ['query_account_id', 'query_account_name', 'productLine', 'usageMetric', 'sum.gigabytesIngested', 'facet', 'accountId']
    sorted_final_headers = [h for h in preferred_order if h in final_headers]
    for h in final_headers:
        if h not in sorted_final_headers:
            sorted_final_headers.append(h) # Add any remaining headers

    print(f"\nAttempting to save {len(all_nrql_results)} rows to '{OUTPUT_CSV_FILE}'...")
    try:
        with open(OUTPUT_CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=sorted_final_headers)

            writer.writeheader()
            for row in all_nrql_results:
                # Fill in missing columns with None for rows that don't have all headers
                # This makes DictWriter happy and ensures consistent columns
                cleaned_row = {header: row.get(header) for header in sorted_final_headers}
                writer.writerow(cleaned_row)

        print(f"\nSuccessfully saved all NRQL query results to '{OUTPUT_CSV_FILE}'")
        print(f"Results preview (first 5 rows if available):")
        for i, row in enumerate(all_nrql_results):
            if i < 5:
                print(row)
            else:
                break
    except IOError as e:
        print(f"Error writing to CSV file '{OUTPUT_CSV_FILE}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred during CSV writing: {e}")

if __name__ == "__main__":
    main()