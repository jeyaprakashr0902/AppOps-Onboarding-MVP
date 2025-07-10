import json
import boto3
from datetime import datetime
import os
import uuid 
from alert_condition import list_all_alert_conditions
from keys import get_keys

sandbox_key="NRAK-YJZYPI2LDDKRX9U5EYO9MA2WRFQ"

# session = boto3.session.Session(
#             aws_access_key_id='ASIASN6DDYD5MPI7TTFN',
#             aws_secret_access_key='J3Vv5LN/2Yf0zqs8CvZF/ih+1cFfRw8SaK8LlPs7',
#             aws_session_token="IQoJb3JpZ2luX2VjEGMaCXVzLXdlc3QtMiJIMEYCIQCaHwKwZ522+rhk/pR+aWj2KqsSmTS1FzVyOL6+Jlv7agIhANmJe8Uo418DQqH8PK94QWaXImjSrTghzIRzRq7C6sY3KpMDCGwQAxoMMTY3Mzc2MDQ0MjgyIgyoBHAc/jWYwrh1zmgq8AKtn7tM6iykT1bJrnlcsYw6swMhzwVTqfdOowVYkmlUgBlgNAJBiti3sUxIkVl2q3iOmKPUR2Rrp/cUgWwp/gEk7dAgUQeGCqeRc+LcUnAg0NGVINnVoW8X9Ht07ZdLX0VhKE3gIiOHHFJSw5ft3gfXEvgCwoU876pQa8/XyXtdeH5U4ZH91bFfFHoV9D2ay1iEdaR1o5/wmmtO2L3fhEV0u+0rWkWSfp+Fmynwmdpn4tkV57xVNplHHxAQk886LYxzvZQWVzOKGCBoO1dpod5wKz1CDNi482/emqvO0HHXNiyXszHLkEaKmz5JKUTenEtgKXDGKJtBVnXwRQWl19D3Ohgy4E03tKXYsRj/hPSMaYzmq2iucpvS4uKpVILmEfxfey1vb9OmCgCUTY7Tai8y+h/pYtNserZMwTA+xUndrbG/+A/zM9HHqZvjbQgWpv8NDclopuC7seObwOIEDiW4ommaFo/bfLG0vJA/dpgr4jCh86zDBjqlATaBS+m/EekO6XryuGPdv0Ydv4h0yFotkCk0oBnVmnlFvRZV8Wu6vtB7ylNNeoFv9NWsIt04NtJSSiGFTBrTMhWgk4+IXZM/OdeX5G0R25VEb+gTiwCVwwWkc7Nn9fiRqmaw3wZWSo2Zlypqd+wORdP+qgNqSH8/VcirH0UfKH6s74zw+xnWc9IPIjh5VZKPA4p8RGW3aXYNjAWdYEaGUcX/UZdWJw==",
#             region_name='us-west-2'
#         )




# --- Configuration ---
S3_BUCKET_NAME = 'appops-onboarding-mvp' # <<<<<<< IMPORTANT: Replace with your actual S3 bucket name
S3_DATA_PREFIX = 'newrelic-daily-report' # <<<<<<< Optional: A logical grouping for your data, e.g., 'newrelic-daily-dumps'

# Initialize the S3 client
s3_client = boto3.client('s3')

def store_result_dict_in_s3(result_dictionary_object: dict):
    """
    Serializes a Python dictionary to a JSON string and uploads it to S3
    with a date-partitioned key (year/month/day/unique_filename.json).

    Args:
        result_dictionary_object (dict): The Python dictionary to store.

    Returns:
        str: The S3 key (path) where the data was stored, or None if an error occurred.
    """
    # 1. Convert Python dictionary to JSON string
    #    - ensure_ascii=False allows non-ASCII characters (e.g., emojis, foreign languages).
    #    - indent=None makes it a single line, which is efficient for Athena/data processing.
    #      Use indent=2 or 4 if you need human-readable files in S3 (at the cost of file size).
    json_data = json.dumps(result_dictionary_object, ensure_ascii=False)

    # 2. Generate date-based S3 key for partitioning
    #    Using current UTC time is a best practice for data lakes to avoid timezone issues.
    current_dt = datetime.now()

    year = current_dt.strftime('%Y')
    month = current_dt.strftime('%m')
    day = current_dt.strftime('%d')

    # Generate a unique suffix for the file name to prevent overwrites
    # if the function runs multiple times on the same day.
    # We combine a timestamp with a UUID for strong uniqueness.
    
    file_name ="result.json" # Naming convention: result_<timestamp>_<uuid>.json

    # Construct the full S3 key (path)
    # Example: your-data-collection-name/year=2025/month=07/day=05/result_161344123456_a1b2c3d4.json
    s3_key = f"{S3_DATA_PREFIX}/year={year}/month={month}/day={day}/{file_name}"

    # 3. Upload to S3
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=json_data,
            ContentType='application/json' # Specifies the content type of the object
        )
        print(f"Successfully uploaded data to s3://{S3_BUCKET_NAME}/{s3_key}")
        return s3_key
    except Exception as e:
        print(f"Error uploading data to S3: {e}")
        return None

# --- Example Usage (assuming you have your result_dictionary_object here) ---
if __name__ == "__main__":
    # This is your result dictionary object.
    # Replace this with the actual dictionary your New Relic code produces.

    sub_account_keys=get_keys()
    alert_details=list_all_alert_conditions(sandbox_key,sub_account_keys)
    
    # Call the function to store the dictionary in S3
    s3_path = store_result_dict_in_s3(alert_details)

    if s3_path:
        print(f"\nYour data is stored in S3. The full path is: {s3_path}")
        print("You can now set up AWS Glue Crawler or an Athena table over this S3 prefix.")
    else:
        print("\nFailed to store data in S3. Check the error messages above.")