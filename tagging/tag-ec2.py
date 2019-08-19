import boto3
import json
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # If running from the command line, set your environment variables.
    # i.e. AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_DEFAULT_REGION

    # EC2 tag (Name) to search for, i.e. machines which you want to tag 
    # Use '*' to tag ALL EC2 instances
    # i.e. tagValue = '*'
    matchingTagNameValue = 'Dev Portal Bastion'
    # The tag you want to add, e.g. Environment tag with value Development
    newTagName = 'TestTagName'
    newTagValue = 'TestTagValue'
    
    client = boto3.client('ec2')

    # Initial request, search for all EC2s which match tag (Name)
    reservations = search_and_tag(matchingTagNameValue, newTagName, newTagValue, client)
    
    # Paginate if there are additional results and tag
    while 'NextToken' in reservations:
        reservations = search_and_tag(matchingTagNameValue, newTagName, newTagValue, client, reservations['NextToken'])

    return {
        'statusCode': 200,
        'body': json.dumps('OK!')
    }

def search_and_tag(matchingTagNameValue, newTagName, newTagValue, client, nextToken = ''):
    if nextToken == '':
        reservations = client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['' + matchingTagNameValue  +'']}])
    else:
        reservations = client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['' + matchingTagNameValue  +'']}], NextToken=nextToken)
    
    for reservation in reservations['Reservations']:
        for instance in reservation['Instances']:
            tag_ec2(client, instance, newTagName, newTagValue)
            print(instance['InstanceId'] + " tagged with tagName '" + str(newTagName) + "' with value '" + str(newTagValue) + "'")
    
    return reservations


def tag_ec2(client, instance, tagName, tagValue):
    tags = []
    # Try to get existing tags
    try:
        tags = instance['Tags']
    except ClientError as e:
        print("Caught unexpected error: %s" % e)
    tags.append({'Key': tagName, 'Value': tagValue})
    instanceId = instance['InstanceId']
    # Tag the resource
    response = client.create_tags(
        Resources=[
            '' + str(instanceId) +'',
        ],
        Tags=tags
    )

if __name__== "__main__":
    lambda_handler('dummy','dummy')