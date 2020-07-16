from dotenv import load_dotenv

import boto3
import json
import os

load_dotenv()


print('Starting.....')
print ()
bs = boto3.client('elasticbeanstalk')

