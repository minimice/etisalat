import boto3
import os
import json
import datetime

#TODO Create Lambda IAM role
#TODO Create Lambda
#TODO Deploy Lambda
#TODO Create cron job to run lambda periodically

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_file
def main():
    s3 = boto3.resource('s3')
    # list current directory
    # Upload
    s3.meta.client.upload_file('/tmp/hello.txt', 'mybucket', 'hello.txt')
    
if __name__== "__main__":
    main()
