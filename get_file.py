import boto3
import json



def get_data():

    bucket_name = 'appops-onboarding-mvp'
    file_key = 'newrelic-daily-report/year=2025/month=07/day=13/result.json'


  

    s3 = boto3.client('s3')


    response = s3.get_object(Bucket=bucket_name, Key=file_key)


    content = response['Body'].read().decode('utf-8')
    data = json.loads(content)

    return data
