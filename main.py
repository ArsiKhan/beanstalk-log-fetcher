from dotenv import load_dotenv
from scp import SCPClient
from paramiko import SSHClient, AutoAddPolicy

import boto3
import os
import sys

# Fetching environment variables from .env file
load_dotenv()

# AWS Services Session
bs = boto3.client('elasticbeanstalk')
ec2 = boto3.resource('ec2')



# Setting up SSH Client
ssh = SSHClient()
ssh.set_missing_host_key_policy(AutoAddPolicy())


# Variables
keypair_path = os.getenv("KEYPAIR_PATH")
pkey_passphrase = os.getenv("PKEY_PASSPHRASE")
environment_name = os.getenv("ENVIRONMENT_NAME")
destination_folder = os.getenv("DESTINATION_FOLDER")

def get_instanceIDs(environment):
    response = bs.describe_environment_resources(EnvironmentName=environment)
    temp = response['EnvironmentResources']['Instances']
    return [inst['Id'] for inst in temp]

def get_instanceIPs(ids):
    instances = ec2.instances.filter(Filters=[{
        'Name': 'instance-id',
        'Values': ids
    }])
    return {instance.id: instance.public_ip_address for instance in instances}

# Define progress callback that prints the current percentage completed for the file
def progress(filename, size, sent):
    sys.stdout.write("%s's progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100) )

def get_zipFiles(ips, destination_folder):

    for ID, ip in ips.items():

        #Setting up ssh connection
        ssh.connect(ip, username='ec2-user', key_filename=keypair_path, passphrase=pkey_passphrase)
        
        #Creating a zip of log file
        command = 'zip -r tomcat8-{}.zip /var/log/tomcat8'.format(ID)
        print(command)
        (stdin, stdout, stderr)  = ssh.exec_command(command)
        for line in stdout.readlines():
            print(line)    
        
        #Copying the created zip files
        scp = SCPClient(ssh.get_transport(), progress=progress)
        scp.get(remote_path='./tomcat8-{}.zip'.format(ID), local_path=destination_folder)
        scp.close

        ssh.close

print("Starting it......\n")

print("Getting Instance IDs")
instance_ids = get_instanceIDs(environment_name)
print(instance_ids)
print("Getting Instance Ips")
instance_ips = get_instanceIPs(instance_ids)
print(instance_ips)
print("Getting zip files.........")
get_zipFiles(instance_ips, destination_folder)
