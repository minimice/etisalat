# Scan AWS VPC security groups for rule violations.
# Python Version: 3.7.0
# Created with modifications, original script at https://raw.githubusercontent.com/toddm92/security-group-scan/master/security_group_scan.py

import boto3
import json
from botocore.exceptions import ClientError

# Violation lists (according to Trusted Advisor)
# Alert and Criteria 
# Green: Access to port 80, 25, 443, or 465 is unrestricted.
# Red: Access to port 20, 21, 1433, 1434, 3306, 3389, 4333, 5432, or 5500 is unrestricted.
# Yellow: Access to any other port is unrestricted.
#
# Lambda permissions required for the role
# - AmazonEC2ReadOnlyAccess 
# - AWSLambdaBasicExecutionRole
#

# Handling all red alerts only
port_list = [
                'tcp-20',
                'tcp-21',
                'tcp-1433',
                'tcp-1434',
                'tcp-3306',
                'tcp-3389',
                'tcp-4333',
                'tcp-5432',
                'tcp-5500'
            ]

cidr_list = [
                '0.0.0.0/0',
                '::/0'
            ]

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    vpc_ids = get_vpcs(ec2)
    for vpc_id in vpc_ids:
        result = scan_groups(ec2, vpc_id)
        if result != None:
            return result
 
    return {
        'statusCode': 200,
        'body': json.dumps('Done!')
    }       

# Scan VPC security groups for rule violations
def scan_groups(ec2, vpc_id):

    args = {
        'Filters' : [
            {
                'Name' : 'vpc-id',
                'Values' : [ vpc_id ]
            }
        ]
    }
    try:
        groups = ec2.describe_security_groups(**args)['SecurityGroups']
    except ClientError as e:
        print(e.response['Error']['Message'])
        # Returns a JSON object with the body as an error if an error occurs
        return {
            'statusCode': 200,
            'body': json.dumps(e.response['Error']['Message'])
        }

    print('Checking {:d} security group(s) in VPC {}..\n'.format(len(groups), vpc_id))

    # Go through all security groups
    for group in groups:
        group_id   = group['GroupId']
        group_name = group['GroupName']

        # Go through all IP permissions
        for ip_perm in group['IpPermissions']:
            ip_protocol = ip_perm['IpProtocol']

            if ip_protocol == '-1':
                from_port   = 'all'
                to_port     = 'all'
                ip_protocol = 'all'
            else:
                from_port   = ip_perm['FromPort']
                to_port     = ip_perm['ToPort']

            ip_ranges = []

            # IPv4 source IP ranges
            if 'IpRanges' in ip_perm:
                for ip_range in ip_perm['IpRanges']:
                    ip_ranges.append(ip_range['CidrIp'])

            # IPv6 source IP ranges
            if 'Ipv6Ranges' in ip_perm:
                for ip_range in ip_perm['Ipv6Ranges']:
                    ip_ranges.append(ip_range['CidrIpv6'])

            # Check violations in IP ranges
            for cidr_ip in ip_ranges:
                violations = []

                if ip_protocol == 'all' and cidr_ip in cidr_list:
                    violations.append(ip_perm)
                else:
                    for port in port_list:
                        first, last = port.split('-', 1)

                        if (str(from_port) == 'all'):
                            from_port = 0

                        if (str(to_port) == 'all'):
                            to_port = 65535

                        if from_port <= int(last) <= to_port and ip_protocol.lower() == first and cidr_ip in cidr_list:
                            violations.append(ip_perm)

                if len(violations) > 0:
                    print('Violation: security group >>> {} ( {} )'.format(group_name, group_id))
                    print('proto: {}\t from port: {}\t to port: {}\t source: {}\n'.format(ip_protocol, from_port, to_port, cidr_ip))
                    # Trigger SNS to alert users

    return

# Return all VPCs
def get_vpcs(ec2):
    vpc_ids = []

    try:
        vpcs = ec2.describe_vpcs()['Vpcs']
    except ClientError as e:
        print(e.response['Error']['Message'])
         # Returns a JSON object with the body as an error if an error occurs
        return {
            'statusCode': 200,
            'body': json.dumps(e.response['Error']['Message'])
        }       
    else:
        for vpc in vpcs:
            vpc_ids.append(vpc['VpcId'])

    return vpc_ids

#if __name__ == "__main__":
#   main(dummy, dummy)
