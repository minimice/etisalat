#!/bin/bash

# dev env
#input="./volumes-dev.csv"
#environment="dev"

# prod env
#### REMEMBER TO ALSO DOWNLOAD ./volumes-existing.csv
#### OTHERWISE THE SCRIPT WON'T WORK
#### Also you must run this script in Linux
input="./volumes-existing.csv"
environment="prod"

while IFS= read -r line
do
  # is attached
  # aws ec2 describe-volumes --volume-ids vol-097184d85e5ea8d26 --profile prod --output table | grep "Attachments" -c
  # is not attached
  # aws ec2 describe-volumes --volume-ids vol-07a290875676a56ac --profile prod --output table | grep "Attachments" -c
  volume=${line}
  result=$(aws ec2 describe-volumes --volume-ids ${volume} --profile ${environment} --output table | grep "Attachments" -c)
  #echo ${result}
  if [ ${result} = 0 ]; then
    #echo "NOT ATTACHED," >> result.txt
    # create snapshot
    echo "Creating snapshot of "${volume}
    d=`date +%d-%m-%Y`
    backup_description=Backup-${d}
    # $(aws ec2 create-snapshot --dry-run --volume-id ${volume} --description ${backup_description} --tag-specifications 'ResourceType=snapshot,Tags=[{Key=purpose,Value=prod},{Key=costcenter,Value=123}]')
    snapshot=$(aws ec2 create-snapshot --volume-id ${volume} --description ${backup_description} --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value='${volume}'}]' --profile ${environment})
  fi

done < "$input"

echo "Done"
