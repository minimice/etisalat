#!/bin/bash

tagName=Environment
profile=dev

ec2s=$(aws ec2 describe-instances --query 'Reservations[*].Instances[*].InstanceId' --profile ${profile} --output text)

for ec2 in $ec2s
do
  #echo "Checking "$ec2
  # Remove carriage return and newline, happens in Windows, will not raise a ticket to fix this
  ec2=$(echo ${ec2} | tr -d '\r')
  # echo aws ec2 describe-instances --instance-ids $ec2 --profile dev --filters "Name=tag-key,Values=${tagName}" --output text
  result=$(aws ec2 describe-instances --instance-ids $ec2 --profile dev --filters "Name=tag-key,Values=${tagName}" --output text)

  if [ -z "$result" ]
  then
    echo $ec2 "has no tag '${tagName}' raise a ticket to tag it or get fired"
  fi

done




