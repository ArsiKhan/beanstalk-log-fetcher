from dotenv import load_dotenv

import boto3
import json
import os

load_dotenv()


print('Starting.....')
print ()
bs = boto3.client('elasticbeanstalk')
ec2 = boto3.client('ec2')

def get_instanceids(environment):
    print('Getting the instance ids of ', environment)
    response = bs.describe_environment_resources(EnvironmentName=environment)
    temp = response['EnvironmentResources']['Instances']
    return [inst['Id'] for inst in temp]

# def get_instanceips(ids):
#     print("Getting the ip addresses of the instances")
#     response = 

