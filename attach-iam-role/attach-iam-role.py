import boto3
import json
from botocore.exceptions import ClientError

# Load profiles from credentials file located at ~/.aws/credentials
# e.g. dev, prod, test, etc.
devSession = boto3.Session(profile_name='dev')
testSession = boto3.Session(profile_name='test')
prodSession = boto3.Session(profile_name='prod')

def lambda_handler(event, context):

    # Load profiles from credentials file located at ~/.aws/credentials
    # e.g. dev, prod, test, etc.
    devClient = devSession.client('ec2')
    testClient = testSession.client('ec2')
    prodClient = prodSession.client('ec2')

    # Loop through Windows EC2s and attach IAM role
    attach_iam_role_to_ec2s(devClient, testClient, prodClient)

    return {
        'statusCode': 200,
        'body': json.dumps('OK!')
    }

def attach_iam_role_to_ec2s(devClient, testClient, prodClient):
    # clients = [# DEV
    #            {'account': 'Dev',  'client': devClient,  'matchingTagName': '*'},
    #            # TEST
    #            {'account': 'Test', 'client': testClient, 'matchingTagName': '*'},
    #            # PROD
    #            {'account': 'Prod', 'client': prodClient, 'matchingTagName': '*'}]

    clients = [{'account': 'Test', 'client': testClient, 'matchingTagName': '*'}]               
    
    for envClient in clients:

        # Extract properties
        account = envClient['account']
        client = envClient['client']
        matchingTagName = envClient['matchingTagName']

        # Initial request, search for all EC2s
        reservations = search_and_attach_iam_role(matchingTagName, client, account)
        
        # Paginate if there are additional results and tag
        while 'NextToken' in reservations:
           reservations = search_and_attach_iam_role(matchingTagName, client, account, reservations['NextToken'])

def search_and_attach_iam_role(matchingTagNameValue, client, account, nextToken = ''):
    if nextToken == '':
        reservations = client.describe_instances()
    else:
        reservations = client.describe_instances(NextToken=nextToken)

    newTagName = 'OS'
    for reservation in reservations['Reservations']:
        for instance in reservation['Instances']:
            platform = get_ec2_platform(instance)
            ## This is the instance profile ARN
            role_arn = "arn:aws:iam::895883787314:instance-profile/EC2_Instance_Profile_Role"
            #role = 'EC2_Instance_Profile_Role'
            if (platform == 'windows'):
                result = attach_iam_role_to_ec2(client, instance, role_arn, account)
                if (result):
                    print (instance['InstanceId'] + ' has role ' + role_arn)
    
    return reservations

def get_ec2_platform(instance):
    # Tag OS, unfortunately it is not possible to determine OS info from the AWS API
    # See https://forums.aws.amazon.com/thread.jspa?threadID=50257
    # Instead, we use the platform field, if it is Windows we tag it as Windows, if there is nothing or does not exist, it will be tagged as Linux

    os = 'linux'
    if 'Platform' in instance:
        os = instance['Platform']
    return os    

# Attach IAM role to the EC2 instance
def attach_iam_role_to_ec2(client, instance, role_arn, account):

    # Return straightaway (Do not tag, for testing only)
    # return True

    if (account == 'Test'):
        session = testSession
    elif (account == 'Dev'):
        session = devSession
    elif (account == 'Prod'):
        session = prodSession
    else:
        print ("UNKNOWN ACCOUNT " + account)
        return False

    try:
        instanceId = instance['InstanceId']
        instanceProfileName = 'EC2_Instance_Profile_Role' # 'EC2-instance-profile-' + str(instanceId)
        iamClient = session.client('iam')
        ec2Client = session.client('ec2')

        # If you do not already have an instance profile ARN you can uncomment below to create the instance profile
        # instance_profile = iamClient.create_instance_profile(InstanceProfileName = instanceProfileName)
        # response = iamClient.add_role_to_instance_profile(
        #     InstanceProfileName = instanceProfileName,
        #     RoleName = role
        # )

        response = ec2Client.associate_iam_instance_profile(
            IamInstanceProfile = {
                'Arn':  role_arn, # str(instance_profile['InstanceProfile']['Arn']),
                'Name': instanceProfileName
            },
            InstanceId = instanceId
        )

        print (response)
    except ClientError as e:
        print("Caught unexpected error: %s" % e)
        return False
    return True

if __name__== "__main__":
    lambda_handler('dummy','dummy')