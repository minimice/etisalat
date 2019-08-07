#!/bin/bash

environment=dev
# Dev VPC
vpc=vpc-0f65b1633d672859c
description="Access to Expo AWS Servers from admin Vlan"

# Create the security group
sec_group=$(aws ec2 create-security-group --group-name Admin-VLAN-sg --description 'Access to Expo AWS Servers from admin Vlan' --vpc-id ${vpc} --profile ${environment} --output text)
echo $sec_group

# Add rules to security group
rules=$(aws ec2 authorize-security-group-ingress --group-id ${sec_group} --protocol tcp --port 22 --cidr 203.0.113.0/24 --profile ${environment} --output text)
echo $rules

aws ec2 authorize-security-group-ingress --group-id ${sec_group} --ip-permissions IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges='[{CidrIp=203.0.113.0/24,Description="Access to Expo AWS Servers from admin Vlan"}]'

# Source IP
# 10.233.63.0/24
# 10.233.62.0/24
# Destination ports
# 80, 443, 22, 3389

# Type | Protocol | Port Range | Source
# http | tcp | 80 | 10.233.63.0/24
# https | tcp | 443 | 10.233.63.0/24
# ssh | tcp | 22 | 10.233.63.0/24
# rdp | tcp | 3389 | 10.233.63.0/24

# Type | Protocol | Port Range | Source
# http | tcp | 80 | 10.233.62.0/24
# https | tcp | 443 | 10.233.62.0/24
# ssh | tcp | 22 | 10.233.62.0/24
# rdp | tcp | 3389 | 10.233.62.0/24