#!/bin/bash

tagName=Name1
result=$(aws ec2 describe-instances --instance-ids i-0fde02c0593ff8038 --profile dev --filters "Name=tag-key,Values=${tagName}" --output text)

if [ -z "$result" ]; then
  echo "Has no tag '${tagName}'"
else
  echo "Has tag '${tagName}'"
fi
