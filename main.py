from dotenv import load_dotenv

import boto3
import json
import os
import paramiko

load_dotenv()


print('Starting.....')
print ()
bs = boto3.client('elasticbeanstalk')
ec2 = boto3.resource('ec2')

# Setting up SSH Client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Variables
KEYPAIR_PATH = os.getenv("KEYPAIR_PATH")

def get_instanceids(environment):
    print('Getting the instance ids of ', environment)
    response = bs.describe_environment_resources(EnvironmentName=environment)
    temp = response['EnvironmentResources']['Instances']
    return [inst['Id'] for inst in temp]

def get_instanceips(ids):
    print("Getting the ip addresses of the instances.....")
    instances = ec2.instances.filter(Filters=[{
        'Name': 'instance-id',
        'Values': ids
    }])
    return [instance.public_ip_address for instance in instances]

def zip_files(ips):
    print("Creating a zip of all the log files in tomcat8 folder......")
    for idx, ip in enumerate(ips):
        ssh.connect(ip, username='ec2-user', key_filename=KEYPAIR_PATH)
        command = 'zip -r tomcat8-{}.zip /var/log/tomcat'.format(idx)
        (stdin, stdout, stderr) = ssh.exec_command(command)
        for line in stdout.readlines():
            print(line)    
        ssh.close        

# a = get_instanceids('development')
# b = (get_instanceips(a))
# print(zip_files(b))
