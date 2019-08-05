import boto3
import os
import json
import datetime

# Create CloudWatch client
client = boto3.client('cloudwatch')

# Create an SNS client
sns = boto3.client('sns')

def main():
    # Get all queueNames
    queueNames = []

    # List metrics through the pagination interface
    paginator = client.get_paginator('list_metrics')
    for response in paginator.paginate(Dimensions=[{'Name': 'Queue'}],
                                    MetricName='QueueSize'):
        for metrics in response['Metrics']:
            for dimension in metrics['Dimensions']:
                if dimension["Name"] == "Queue":
                    #queues.add(dimension["Value"])
                    #print (dimension["Value"])
                    queuename = (dimension["Value"])
                    queueNames.append(queuename)

    #print (queueNames)

    brokers = [
        [
            "AMQ-Expo2020-Broker-Broker1-1",
            "AMQ-Expo2020-Broker-Broker2-1",
            "AMQ-Expo2020-Broker-Broker3-1"
        ],
        [
            "AMQ-CpaaS-Broker1-1",
            "AMQ-CpaaS-Broker2-1",
            "AMQ-CpaaS-Broker3-1"
        ]
    ]

    # Read in json file
    with open('./queuesize_metric.json') as json_file:
        data = json.load(json_file)
        # print (data)

        # Loop through brokers
        for broker in brokers:

            print ("******  PROCESSING " + str(broker) + " ********")

            # Set broker names
            # m1 
            #print (data[2]['MetricStat']['Metric']['Dimensions'][0]['Value'])
            data[2]['MetricStat']['Metric']['Dimensions'][0]['Value'] = broker[0]
            # m2
            #print (data[3]['MetricStat']['Metric']['Dimensions'][0]['Value'])
            data[3]['MetricStat']['Metric']['Dimensions'][0]['Value'] = broker[1]
            # m3
            # print (data[4]['MetricStat']['Metric']['Dimensions'][0]['Value'])
            data[4]['MetricStat']['Metric']['Dimensions'][0]['Value'] = broker[2]
            # m4
            # print (data[5]['MetricStat']['Metric']['Dimensions'][0]['Value'])
            data[5]['MetricStat']['Metric']['Dimensions'][0]['Value'] = broker[0]
            #print (m4_queueName)
            # m5
            # print (data[6]['MetricStat']['Metric']['Dimensions'][0]['Value'])
            data[6]['MetricStat']['Metric']['Dimensions'][0]['Value'] = broker[1]
            #print (m5_queueName)
            # m6
            # print (data[7]['MetricStat']['Metric']['Dimensions'][0]['Value'])
            data[7]['MetricStat']['Metric']['Dimensions'][0]['Value'] = broker[2]
            #print (m6_queueName)

            for queueName in queueNames:
                #print (queueName)
            
                # Go through all the queues by replacing the queue names
                # m1 
                # print (data[2]['MetricStat']['Metric']['Dimensions'][1]['Value'])
                data[2]['MetricStat']['Metric']['Dimensions'][1]['Value'] = queueName
                # m2
                # print (data[3]['MetricStat']['Metric']['Dimensions'][1]['Value'])
                data[3]['MetricStat']['Metric']['Dimensions'][1]['Value'] = queueName
                # m3
                # print (data[4]['MetricStat']['Metric']['Dimensions'][1]['Value'])
                data[4]['MetricStat']['Metric']['Dimensions'][1]['Value'] = queueName
                # m4
                data[5]['MetricStat']['Metric']['Dimensions'][1]['Value'] = queueName
                #print (m4_queueName)
                # m5
                data[6]['MetricStat']['Metric']['Dimensions'][1]['Value'] = queueName
                #print (m5_queueName)
                # m6
                data[7]['MetricStat']['Metric']['Dimensions'][1]['Value'] = queueName
                #print (m6_queueName)

                endTime = datetime.datetime.now()
                startTime = endTime - datetime.timedelta(minutes=1)
                #print (now.isoformat())
                #print (one_minute_ago.isoformat())

                response = client.get_metric_data(
                    MetricDataQueries = data,
                    # '2019-07-23T09:00:00Z'
                    StartTime = startTime.isoformat(),
                    # '2019-07-23T09:05:00Z'
                    EndTime = endTime.isoformat()
                )

                metricDataValue = 0.0

                if len(response['MetricDataResults'][0]['Values']) == 0:
                    #print ("Length is 0")
                    putMetric(broker, queueName, metricDataValue)
                    continue

                # QueueSize
                e1 = response['MetricDataResults'][0]['Values'][0]
                # DeQueueCount
                e2 = response['MetricDataResults'][1]['Values'][0]

                if (e1 > 0 and e2 == 0):
                    # Trigger SNS notification
                    response = sns.publish(
                       TopicArn = 'arn:aws:sns:eu-west-1:895883787314:aws-alerts-test',    
                       Message = queueName + ' is not being processed',    
                    )
                    metricDataValue = 1.0
                    print (queueName + " is not being processed")
                
                # Put the metric data
                putMetric(broker, queueName, metricDataValue)
                
    return {
        'statusCode': 200,
        'body': json.dumps('OK!')
    }

def putMetric(broker, queueName, metricDataValue):
    # Specify metric data
    metricData = [
        {
            'MetricName': 'QueueSizeAndDeQueueCount',
            'Dimensions': [
                {
                    'Name': 'Brokers',
                    'Value': broker[0] + " " + broker[1] + " " + broker[2]
                },
                {
                    'Name': 'Queue',
                    'Value': queueName
                },
            ],
            'Value': metricDataValue,
            'Unit': 'None'
        }
    ]

    response = client.put_metric_data(
                Namespace = 'CustomMetrics',
                MetricData = metricData
            )
    
    print (response)

if __name__== "__main__":
    main()
