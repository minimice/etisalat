#!/bin/bash

input="./volumes.csv"
while IFS= read -r line
do
  # is attached
  # aws ec2 describe-volumes --volume-ids vol-097184d85e5ea8d26 --profile prod --output table | grep "Attachments" -c
  # is not attached
  # aws ec2 describe-volumes --volume-ids vol-07a290875676a56ac --profile prod --output table | grep "Attachments" -c
  volume=${line}
  result=$(aws ec2 describe-volumes --volume-ids ${volume} --profile prod --output table | grep "Attachments" -c)
  #echo ${result}
  if [ ${result} = 0 ]; then
    echo "NOT ATTACHED," >> result.txt
  else
    echo "ATTACHED," >> result.txt
  fi

done < "$input"