import boto3

def lambda_handler(event, context):
    # Search for all EC2 instances with a tag of Dev Portal Bastion
    client = boto3.client('ec2')
    reservations = client.describe_instances(Filters=[{'Name': 'Name', 'Values': ['Dev Portal Bastion']}])
    for reservation in reservations['Reservations']:
        for instance_description in reservation['Instances']:
            # TODO Do tagging
            print (instance_description)