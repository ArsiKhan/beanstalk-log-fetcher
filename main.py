from dotenv import load_dotenv
from scp import SCPClient
from paramiko import SSHClient, AutoAddPolicy

import boto3
import os
import sys

load_dotenv()


print('Starting.....')
print ()
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
    print('Getting the instance ids of ', environment)
    response = bs.describe_environment_resources(EnvironmentName=environment)
    temp = response['EnvironmentResources']['Instances']
    return [inst['Id'] for inst in temp]

def get_instanceIPs(ids):
    print("Getting the ip addresses of the instances.....")
    instances = ec2.instances.filter(Filters=[{
        'Name': 'instance-id',
        'Values': ids
    }])
    return [instance.public_ip_address for instance in instances]

# Define progress callback that prints the current percentage completed for the file
def progress(filename, size, sent):
    sys.stdout.write("%s's progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100) )

def get_zipFiles(ips, destination_folder):
    print("Creating a zip of all the log files in tomcat8 folder......")
    for idx, ip in enumerate(ips):

        #Setting up ssh connection
        ssh.connect(ip, username='ec2-user', key_filename=keypair_path, passphrase=pkey_passphrase)
        
        #Creating a zip of log files
        command = 'zip -r tomcat8-{}.zip /var/log/tomcat'.format(idx)
        (stdin, stdout, stderr)  = ssh.exec_command(command)
        for line in stdout.readlines():
            print(line)    
        
        #Copying the created zip files
        scp = SCPClient(ssh.get_transport(), progress=progress)
        scp.get(remote_path='./tomcat8-{}.zip'.format(idx), local_path=destination_folder)
        scp.close
