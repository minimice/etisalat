#!/bin/bash

tagKey=Environment
tagValue=Environment
profile=dev

s3buckets=$(aws s3api list-buckets --query 'Buckets[].Name' --profile ${profile} --output text)

for s3bucket in $s3buckets
do
  # Remove carriage return and newline, happens in Windows, will not raise a ticket to fix this
  bucket=$(echo ${s3bucket} | tr -d '\r')
  echo ${bucket}
  #echo "Checking "$bucket

  # List tags on bucket (if any)
  # aws s3api get-bucket-tagging -bucket ${bucket} --profile ${profile} --output text

  # Tag the bucket
  # aws s3api put-bucket-tagging --bucket cg-test-bucket --tagging "TagSet=[{Key=${tagKey},Value=${tagValue}}]" --profile ${profile}

done




