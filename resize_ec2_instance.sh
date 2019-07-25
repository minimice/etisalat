#!/bin/bash

account=$1
inst_id=$2
instance_type=$3

if [ "$#" -ne 3 ]; then
  echo "** Usage **"
  echo "./resize_ec2_instances.sh (profile) (instance-id) (instance-size)"
  echo "For example"
  echo "./resize_ec2_instances.sh dev i-0d53dd21fbfd036c7 t2.small"
  exit 1
fi

# Set to nothing to execute without dry run
#dry_run="--dry-run"
dry_run=""

# Stop the instance
echo "The instance ID" $inst_id "will be stopped"
status="$(aws ec2 stop-instances --instance-ids $inst_id --profile $account $dry_run)"

# Wait for instance to stop
while [ "$status" != "stopped" ]; do
  status="$(aws ec2 describe-instances --instance-ids $inst_id --output text --query "Reservations[*].Instances[*].State.Name" --profile $account $dry_run)"
  echo "The instance ID" $inst_id "is stopping now"
  sleep 5
  if [ "$status" == "stopped" ]; then
    echo "The instance ID" $inst_id "has" $status
    break
  fi
done

# Resize the instance to a new size
echo "Modifying instance ID" $inst_id "to" $instance_type
modify_instance="$(aws ec2 modify-instance-attribute --instance-id $inst_id --instance-type "{\"Value\": \"$instance_type\"}" --profile $account $dry_run)"
echo "Starting Instance ID" $inst_id
starting_instance="$(aws ec2 start-instances --instance-ids $inst_id --profile $account)"

# Wait for instance to start running
while [ "$status" != "running" ]; do
  status="$(aws ec2 describe-instances --instance-ids $inst_id --output text --query "Reservations[*].Instances[*].State.Name" --profile $account $dry_run)"
  echo "The instance ID" $inst_id "is starting now"
  sleep 5
  if [ "$status" == "running" ]; then
    echo "The instance ID" $inst_id "is now" $status
    break
  fi
done