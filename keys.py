import boto3
import json


def get_keys():

        # session = boto3.session.Session(
        #     aws_access_key_id='ASIASN6DDYD5MPI7TTFN',
        #     aws_secret_access_key='J3Vv5LN/2Yf0zqs8CvZF/ih+1cFfRw8SaK8LlPs7',
        #     aws_session_token="IQoJb3JpZ2luX2VjEGMaCXVzLXdlc3QtMiJIMEYCIQCaHwKwZ522+rhk/pR+aWj2KqsSmTS1FzVyOL6+Jlv7agIhANmJe8Uo418DQqH8PK94QWaXImjSrTghzIRzRq7C6sY3KpMDCGwQAxoMMTY3Mzc2MDQ0MjgyIgyoBHAc/jWYwrh1zmgq8AKtn7tM6iykT1bJrnlcsYw6swMhzwVTqfdOowVYkmlUgBlgNAJBiti3sUxIkVl2q3iOmKPUR2Rrp/cUgWwp/gEk7dAgUQeGCqeRc+LcUnAg0NGVINnVoW8X9Ht07ZdLX0VhKE3gIiOHHFJSw5ft3gfXEvgCwoU876pQa8/XyXtdeH5U4ZH91bFfFHoV9D2ay1iEdaR1o5/wmmtO2L3fhEV0u+0rWkWSfp+Fmynwmdpn4tkV57xVNplHHxAQk886LYxzvZQWVzOKGCBoO1dpod5wKz1CDNi482/emqvO0HHXNiyXszHLkEaKmz5JKUTenEtgKXDGKJtBVnXwRQWl19D3Ohgy4E03tKXYsRj/hPSMaYzmq2iucpvS4uKpVILmEfxfey1vb9OmCgCUTY7Tai8y+h/pYtNserZMwTA+xUndrbG/+A/zM9HHqZvjbQgWpv8NDclopuC7seObwOIEDiW4ommaFo/bfLG0vJA/dpgr4jCh86zDBjqlATaBS+m/EekO6XryuGPdv0Ydv4h0yFotkCk0oBnVmnlFvRZV8Wu6vtB7ylNNeoFv9NWsIt04NtJSSiGFTBrTMhWgk4+IXZM/OdeX5G0R25VEb+gTiwCVwwWkc7Nn9fiRqmaw3wZWSo2Zlypqd+wORdP+qgNqSH8/VcirH0UfKH6s74zw+xnWc9IPIjh5VZKPA4p8RGW3aXYNjAWdYEaGUcX/UZdWJw==",
        #     region_name='us-west-2'
        # )

        client = boto3.client('secretsmanager')

        # response = client.create_secret(
        #     Name='NewRelic_MEP',
        #     SecretString=json.dumps({
        #         'username': 'admin',
        #         'password': 'secret123'
        #     })
        # )

        response = client.get_secret_value(SecretId='NewRelic_MEP')

        secret = json.loads(response['SecretString'])
        return secret

if __name__=="__main__":
        secret=get_keys()
        print(len(secret))
        






