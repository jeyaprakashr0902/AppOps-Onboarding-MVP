import boto3
import json


def get_keys():


        client = boto3.client('secretsmanager')

        response = client.get_secret_value(SecretId='NewRelic_MEP')

        secret = json.loads(response['SecretString'])
        return secret

if __name__=="__main__":
        secret=get_keys()
        print(len(secret))
        






