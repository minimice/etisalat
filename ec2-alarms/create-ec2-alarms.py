import boto3
import json
from botocore.exceptions import ClientError

# Load profiles from credentials file located at ~/.aws/credentials
# e.g. dev, prod, test, etc.
devSession = boto3.Session(profile_name='dev')
testSession = boto3.Session(profile_name='test')
prodSession = boto3.Session(profile_name='prod')

def lambda_handler(event, context):

    devClientEc2 = devSession.client('ec2')
    devClientAutoScaling = devSession.client('autoscaling')
    devClientCloudwatch = devSession.client('cloudwatch')
    
    testClientEc2 = testSession.client('ec2')
    testClientAutoScaling = testSession.client('autoscaling')
    testClientCloudwatch = testSession.client('cloudwatch')
    
    prodClientEc2 = prodSession.client('ec2')
    prodClientAutoScaling = prodSession.client('autoscaling')
    prodClientCloudwatch = prodSession.client('cloudwatch')    

    # Create alarms for all EC2s
    create_alarm_for_all_ec2s(devClientEc2, devClientAutoScaling, devClientCloudwatch,
                              testClientEc2, testClientAutoScaling, testClientCloudwatch,
                              prodClientEc2, prodClientAutoScaling, prodClientCloudwatch)

    return {
        'statusCode': 200,
        'body': json.dumps('OK!')
    }

def create_alarm_for_all_ec2s(devClientEc2, devClientAutoScaling, devClientCloudwatch, testClientEc2, testClientAutoScaling, testClientCloudwatch, prodClientEc2, prodClientAutoScaling, prodClientCloudwatch):
    # clients = [# DEV
    #            {'account': 'Dev',  'client': devClientEc2, 'cloudwatchClient': devClientCloudwatch, 'autoscalingClient': devClientAutoScaling, 'matchingTagName': '*'},
    #            # TEST
    #            {'account': 'Test', 'client': testClientEc2, 'cloudwatchClient': testClientCloudwatch, 'autoscalingClient': testClientAutoScaling, 'matchingTagName': '*'},
    #            # PROD
    #            {'account': 'Prod', 'client': prodClientEc2, 'cloudwatchClient': prodClientCloudwatch, 'autoscalingClient': prodClientAutoScaling, 'matchingTagName': '*'}]

    clients = [{'account': 'Test',  'client': testClientEc2, 'cloudwatchClient': testClientCloudwatch, 'autoscalingClient': testClientAutoScaling, 'matchingTagName': '*'}]

    # Dev Performance Master
    # clients = [{'account': 'Dev',  'client': devClientEc2, 'cloudwatchClient': devClientCloudwatch, 'autoscalingClient': devClientAutoScaling, 'matchingTagName': 'Dev Performance Master'}]

    asgEc2s = []
    for envClient in clients:
        autoScalingClient = envClient['autoscalingClient']
        # Get all EC2 instances which are part of autoscaling
        reservations = get_all_asg_ec2s(asgEc2s, autoScalingClient)
        while 'NextToken' in reservations:
            reservations = get_all_asg_ec2s(asgEc2s, autoScalingClient, reservations['NextToken'])
        # print(asgEc2s)
    
    for envClient in clients:
        # Extract properties
        account = envClient['account']
        client = envClient['client']
        matchingTagName = envClient['matchingTagName']
        cloudwatchclient = envClient['cloudwatchClient']

        # Initial request, search for all EC2s which match tag (Name)
        reservations = search_and_create_alarm(matchingTagName, client, asgEc2s, cloudwatchclient, account)
        
        # Paginate if there are additional results
        while 'NextToken' in reservations:
           reservations = search_and_create_alarm(matchingTagName, client, asgEc2s, cloudwatchclient, account, reservations['NextToken'])

def get_all_asg_ec2s(asgEc2s, client, nextToken = ''):

    if nextToken == '':
        reservations = client.describe_auto_scaling_instances()
    else:
        reservations = client.describe_auto_scaling_instances(NextToken=nextToken)

    for instance in reservations['AutoScalingInstances']:
        asgEc2s.append(instance['InstanceId'])
    
    return reservations

def get_asg_groupname(instanceId, session, nextToken = ''):

    client = session.client('autoscaling')    

    if nextToken == '':
        reservations = client.describe_auto_scaling_instances()
    else:
        reservations = client.describe_auto_scaling_instances(NextToken=nextToken)

    for instance in reservations['AutoScalingInstances']:
        if (instanceId == instance['InstanceId']):
            return instance['AutoScalingGroupName']
    
    return False  
      

def search_and_create_alarm(matchingTagNameValue, client, asgEc2s, cloudwatchclient, account, nextToken = ''):
    if nextToken == '':
        reservations = client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['' + matchingTagNameValue  +'']}])
    else:
        reservations = client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['' + matchingTagNameValue  +'']}], NextToken=nextToken)

    for reservation in reservations['Reservations']:
        for instance in reservation['Instances']:
            if instance['InstanceId'] not in asgEc2s:
                # Create alarm for instance NOT part of AutoScaling Group
                result = create_alarm_ec2(cloudwatchclient, instance, account)
            else:
                # Create alarm for instances part of ASG
                result = create_alarm_ec2(cloudwatchclient, instance, account, False) 
    
    return reservations

# Output for the console
def print_output(result, instance, account):
    if (result):
        print(instance['InstanceId'] + " (" + get_ec2_name(instance) + ")" + " alarm created")
    else:
        print(instance['InstanceId'] + " (" + get_ec2_name(instance) + ")" + " alarm not created")

# Output for excel in CSV, useful for filtering
# Output is InstanceId, Name, Account, ALARM CREATED|ALARM NOT CREATED
def print_csv_output(result, instance, account):
    if (result):
        print(instance['InstanceId'] + "," + get_ec2_name(instance) + "," + account + ", ALARM CREATED")
    else:
        print(instance['InstanceId'] + "," + get_ec2_name(instance) + "," + account + ", ALARM NOT CREATED")

# Retrieves name of EC2 instance
def get_ec2_name(instance):
    for tag in instance['Tags']:
        if tag['Key'] == 'Name':
            return tag['Value']
    
    return "NO NAME"

# Create the alarm for EC2 instance
def create_alarm_ec2(cloudwatchclient, instance, account, individualInstance=True):

    # Return straightaway (For testing only)
    # return True

    if (individualInstance):
        # Tag the resource
        try:
            instanceId = instance['InstanceId']
            threshold = 90
            alarmName = "CPU Utilization >%s%% for %s" % (str(threshold), instanceId)
            alarmDescription = "CPU Utilization of server %s is > %s%%" % (instanceId, str(threshold))
            ## SNS ARN (For test environment only, change this to your correct account SNS)
            snsAlertARN = "arn:aws:sns:eu-west-1:895883787314:aws-alerts-test"

            ## Create the alarm name and description
            response = cloudwatchclient.put_metric_alarm(
                AlarmName = alarmName,
                AlarmDescription = alarmDescription,
                AlarmActions = [snsAlertARN],
                EvaluationPeriods = 1,
                MetricName = 'CPUUtilization',
                Namespace = 'AWS/EC2',
                Statistic = 'Average',        
                Threshold = threshold,
                Period = 300,
                ComparisonOperator = 'GreaterThanOrEqualToThreshold',
                Dimensions = [
                    {
                        'Name': 'InstanceId',
                        'Value': str(instanceId)
                    },
                ]
            )

            print (response)
        except ClientError as e:
            print("Caught unexpected error: %s" % e)
            return False
    else:
        # Tag the AutoScaling Group resource
        try:
            instanceId = instance['InstanceId']
            session = None
            if (account == 'Test'):
                session = testSession
            elif (account == 'Dev'):
                session = devSession
            elif (account == 'Prod'):
                session = prodSession
            else:
                print ("UNKNOWN ACCOUNT " + account)
                return False
            
            asgGroupName = get_asg_groupname(instanceId, session)

            #print (asgGroupName)

            threshold = 90
            alarmName = "CPU Utilization >%s%% for AutoScaling Group %s" % (threshold, asgGroupName)
            alarmDescription = "CPU Utilization is > %s%% for AutoScaling Group %s" % (threshold, asgGroupName)
            ## SNS ARN (For test environment only, change this to your correct account SNS)
            snsAlertARN = "arn:aws:sns:eu-west-1:895883787314:aws-alerts-test"

            ## Create the alarm name and description
            response = cloudwatchclient.put_metric_alarm(
                AlarmName = alarmName,
                AlarmDescription = alarmDescription,
                AlarmActions = [snsAlertARN],
                EvaluationPeriods = 1,
                MetricName = 'CPUUtilization',
                Namespace = 'AWS/EC2',
                Statistic = 'Average',        
                Threshold = threshold,
                Period = 300,
                ComparisonOperator = 'GreaterThanOrEqualToThreshold',
                Dimensions = [
                    {
                        'Name': 'AutoScalingGroupName',
                        'Value': asgGroupName
                    },
                ]
            )

            print (response)
        except ClientError as e:
            print("Caught unexpected error: %s" % e)
            return False        
    return True

if __name__== "__main__":
    lambda_handler('dummy','dummy')