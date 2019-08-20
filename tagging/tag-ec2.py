import boto3
import json
from botocore.exceptions import ClientError

def lambda_handler(event, context):

    # Load profiles from credentials file located at ~/.aws/credentials
    # e.g. dev, prod, test, etc.
    devSession = boto3.Session(profile_name='dev')
    devClient = devSession.client('ec2')

    testSession = boto3.Session(profile_name='test')
    testClient = testSession.client('ec2')

    prodSession = boto3.Session(profile_name='prod')
    prodClient = prodSession.client('ec2')

    # Set matchingTagName '*' to tag ALL EC2 instances
    # i.e. matchingTagName = '*' or 
    #      matchingTagName = 'Dev Portal Bastion' to match only EC2s with the name tag of 'Dev Portal Bastion'
    # The tag you want to add, e.g. Environment tag with value Development
    #
    # Set newTagName to the tag you want to add or update
    # e.g. newTagName = 'Environment' where 'Environment' is the tag you want to add or update
    #
    # Set newTagValue to the value of the tag
    # e.g. newTagValue = 'Dev' where 'Environment' will have a value of 'Dev'    

    clients = [{'client': devClient,  'matchingTagName': '*', 'newTagName': 'Environment', 'newTagValue': 'Dev'},
               {'client': testClient, 'matchingTagName': '*', 'newTagName': 'Environment', 'newTagValue': 'Test'},
               {'client': prodClient, 'matchingTagName': '*', 'newTagName': 'Environment', 'newTagValue': 'Prod'}]

    for clientAndTag in clients:

        client = clientAndTag['client']
        matchingTagName = clientAndTag['matchingTagName']
        tagName = clientAndTag['newTagName']
        tagValue = clientAndTag['newTagValue']

        # Initial request, search for all EC2s which match tag (Name)
        reservations = search_and_tag(matchingTagName, tagName, tagValue, client)
        
        # Paginate if there are additional results and tag
        while 'NextToken' in reservations:
            reservations = search_and_tag(matchingTagName, tagName, tagValue, client, reservations['NextToken'])

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
            result = tag_ec2(client, instance, newTagName, newTagValue)
            if (result):
                print(instance['InstanceId'] + " tagged with tagName '" + str(newTagName) + "' with value '" + str(newTagValue) + "'")
            else:
                print(instance['InstanceId'] + " could not be tagged")
    
    return reservations


def tag_ec2(client, instance, tagName, tagValue):
    tags = []
    # Try to get existing tags
    #try:
    #    tags = instance['Tags']
    #except ClientError as e:
    #    print("Caught unexpected error: %s" % e)
    tags.append({'Key': tagName, 'Value': tagValue})
    instanceId = instance['InstanceId']
    # Tag the resource
    try:
        response = client.create_tags(
            Resources=[
                '' + str(instanceId) +'',
            ],
            Tags=tags
        )
    except ClientError as e:
        print("Caught unexpected error: %s" % e)
        return False
    return True

if __name__== "__main__":
    lambda_handler('dummy','dummy')