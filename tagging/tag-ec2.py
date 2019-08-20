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

    # clients = [{'account': 'Dev', 'client': devClient, 'matchingTagName': '*', 'newTagName': 'Environment', 'newTagValue': 'Dev'}]    

    clients = [# DEV
               {'account': 'Dev',  'client': devClient,  'matchingTagName': '*', 'newTagName': 'Environment', 'newTagValue': 'Dev'},
               {'account': 'Dev',  'client': devClient,  'matchingTagName': '*', 'newTagName': 'Region', 'newTagValue': 'eu-west-1'},
               # TEST
               {'account': 'Test', 'client': testClient, 'matchingTagName': '*', 'newTagName': 'Environment', 'newTagValue': 'Test'},
               {'account': 'Test',  'client': testClient,  'matchingTagName': '*', 'newTagName': 'Region', 'newTagValue': 'eu-west-1'},
               # PROD
               {'account': 'Prod', 'client': prodClient, 'matchingTagName': '*', 'newTagName': 'Environment', 'newTagValue': 'Prod'},
               {'account': 'Prod', 'client': prodClient, 'matchingTagName': '*', 'newTagName': 'Region', 'newTagValue': 'eu-west-1'}]

    for clientWithTags in clients:

        # Extract properties
        account = clientWithTags['account']
        client = clientWithTags['client']
        matchingTagName = clientWithTags['matchingTagName']
        tagName = clientWithTags['newTagName']
        tagValue = clientWithTags['newTagValue']

        # Initial request, search for all EC2s which match tag (Name)
        reservations = search_and_tag(matchingTagName, tagName, tagValue, client, account)
        
        # Paginate if there are additional results and tag
        while 'NextToken' in reservations:
            reservations = search_and_tag(matchingTagName, tagName, tagValue, client, account, reservations['NextToken'])

    return {
        'statusCode': 200,
        'body': json.dumps('OK!')
    }

def search_and_tag(matchingTagNameValue, newTagName, newTagValue, client, account, nextToken = ''):
    if nextToken == '':
        reservations = client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['' + matchingTagNameValue  +'']}])
    else:
        reservations = client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['' + matchingTagNameValue  +'']}], NextToken=nextToken)
    
    for reservation in reservations['Reservations']:
        for instance in reservation['Instances']:
            result = tag_ec2(client, instance, newTagName, newTagValue)
            # result = True
            # print_output(result, instance, newTagName, newTagValue, account)
            print_csv_output(result, instance, newTagName, newTagValue, account)
    
    return reservations

# Output for the console
def print_output(result, instance, newTagName, newTagValue, account):
    if (result):
        print(instance['InstanceId'] + " (" + get_ec2_name(instance) + ")" + " tagged with tagName '" + str(newTagName) + "' with value '" + str(newTagValue) + "'")
    else:
        print(instance['InstanceId'] + " (" + get_ec2_name(instance) + ")" +" could not be tagged")

# Output for excel in CSV, useful for filtering
# Output is InstanceId, Name, Account, TagName, TagValue
def print_csv_output(result, instance, newTagName, newTagValue, account):
    if (result):
        print(instance['InstanceId'] + "," + get_ec2_name(instance) + "," + account + "," + str(newTagName) + "," + str(newTagValue))
    else:
        print(instance['InstanceId'] + "," + get_ec2_name(instance) + "," + account + "," + str(newTagName) + ",NOT TAGGED")

# Retrieves name of EC2 instance
def get_ec2_name(instance):
    for tag in instance['Tags']:
        if tag['Key'] == 'Name':
            return tag['Value']
    
    return "NO NAME"

# Tags the EC2 instance
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
               '' + str(instanceId) + '',
           ],
           Tags=tags
        )
    except ClientError as e:
        print("Caught unexpected error: %s" % e)
        return False
    return True

if __name__== "__main__":
    lambda_handler('dummy','dummy')