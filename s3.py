import json
import boto3
from datetime import datetime
import os
import uuid 
from alert_condition import list_all_alert_conditions
from keys import get_keys


S3_BUCKET_NAME = 'appops-onboarding-mvp'
S3_DATA_PREFIX = 'newrelic-daily-report' 


s3_client = boto3.client('s3')

def store_result_dict_in_s3(result_dictionary_object: dict):
    
    
    json_data = json.dumps(result_dictionary_object, ensure_ascii=False,indent=2)


    current_dt = datetime.now()

    year = current_dt.strftime('%Y')
    month = current_dt.strftime('%m')
    day = current_dt.strftime('%d')

    
    
    file_name ="result.json" 
    
    s3_key = f"{S3_DATA_PREFIX}/year={year}/month={month}/day={day}/{file_name}"

    
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=json_data,
            ContentType='application/json' 
        )
        print(f"Successfully uploaded data to s3://{S3_BUCKET_NAME}/{s3_key}")
        return s3_key
    except Exception as e:
        print(f"Error uploading data to S3: {e}")
        return None


if __name__ == "__main__":
  

    sub_account_keys=get_keys()
    key=sub_account_keys['2330551']['key']
    alert_details=list_all_alert_conditions(key,sub_account_keys)
    

   
    s3_path = store_result_dict_in_s3(alert_details)

    if s3_path:
        print(f"\nYour data is stored in S3. The full path is: {s3_path}")
        
    else:
        print("\nFailed to store data in S3. Check the error messages above.")