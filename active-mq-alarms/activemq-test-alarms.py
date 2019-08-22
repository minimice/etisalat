import boto3
import os
import json
import datetime

def main():

    testSession = boto3.Session(profile_name='test')
    testClient = testSession.client('cloudwatch')

    # Get all queueNames (distinct)
    queueNames = set(get_queue_names(testClient))

    #print (queueNames)

    brokers = [
        [
            "AMQ-Expo2020-Broker-Broker1-1",
            "AMQ-Expo2020-Broker-Broker2-1",
            "AMQ-Expo2020-Broker-Broker3-1",
            "AMQ-Expo2020-Broker-Broker1-2-3" #brokerName for Alarm
        ],
        [
            "AMQ-CpaaS-Broker1-1",
            "AMQ-CpaaS-Broker2-1",
            "AMQ-CpaaS-Broker3-1",
            "AMQ-CpaaS-Broker1-2-3" #brokerName for Alarm
        ]
    ]

    alarms = [
        {
            "threshold": 10000,
            "thresholdDescription": "WARNING"
        },
        {
            "threshold": 50000,
            "thresholdDescription": "CRITICAL"
        }
    ]

    # Loop through brokers
    for broker in brokers:
        for queueName in queueNames:
            for alarm in alarms:

                broker1 = broker[0]
                broker2 = broker[1]
                broker3 = broker[2]
                brokersAll = broker[3]
                threshold = alarm["threshold"]
                thresholdDescription = alarm["thresholdDescription"]

                # queues already processed, add to this list if you already have created alerts for these queues
                # e.g. "notify_svp_gigyaId_initregistration_JAWS_Call", "join_start"
                processedQueues = []

                if queueName not in processedQueues:
                    ## Create the alarm name and description
                    alarmName = "EXPO2020-Test-SDP AMQ QueueSize>%s for %s (%s) for %s" % (str(alarm["threshold"]), brokersAll, thresholdDescription, queueName)
                    alarmDescription = "The queue size is growing larger (%s) for %s for %s" % (thresholdDescription, brokersAll, queueName)
                    ## Metric Data
                    metricData = get_metric_data(broker1, broker2, broker3, queueName)
                    ## SNS ARN
                    snsAlertARN = "arn:aws:sns:eu-west-1:895883787314:aws-alerts-test"

                    response = testClient.put_metric_alarm(
                        AlarmName = alarmName,
                        AlarmDescription = alarmDescription,
                        AlarmActions = [snsAlertARN],
                        EvaluationPeriods = 1,
                        Threshold = threshold,
                        ComparisonOperator = 'GreaterThanThreshold',
                        Metrics = metricData
                    )

                    print (response)              
                
    return {
        'statusCode': 200,
        'body': json.dumps('OK!')
    }

# Get queue names
def get_queue_names(cloudwatchClient):
    queueNames = []
    paginator = cloudwatchClient.get_paginator('list_metrics')
    for response in paginator.paginate(Dimensions=[{'Name': 'Queue'}],
                                    MetricName='QueueSize'):
        for metrics in response['Metrics']:
            for dimension in metrics['Dimensions']:
                if dimension["Name"] == "Queue":
                    #queues.add(dimension["Value"])
                    #print (dimension["Value"])
                    queuename = (dimension["Value"])
                    queueNames.append(queuename)
    return queueNames

# Get metric data
def get_metric_data(broker1, broker2, broker3, queueName):
    with open('./queuesize_metric_test_alarm.json') as json_file:
        data = json.load(json_file)
        # Set broker names
        # m1 
        data[1]['MetricStat']['Metric']['Dimensions'][0]['Value'] = broker1
        # m2
        data[2]['MetricStat']['Metric']['Dimensions'][0]['Value'] = broker2
        # m3
        data[3]['MetricStat']['Metric']['Dimensions'][0]['Value'] = broker3

        # Go through all the queues by replacing the queue names
        # m1 
        data[1]['MetricStat']['Metric']['Dimensions'][1]['Value'] = queueName
        # m2
        data[2]['MetricStat']['Metric']['Dimensions'][1]['Value'] = queueName
        # m3
        data[3]['MetricStat']['Metric']['Dimensions'][1]['Value'] = queueName
        return data   

if __name__== "__main__":
    main()
