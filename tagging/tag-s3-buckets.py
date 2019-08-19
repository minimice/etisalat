import boto3
from botocore.exceptions import ClientError

# Set your environment variables before running this script.  The following values are fake, use real values when running this
# i.e. AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_DEFAULT_REGION

key = 'SampleKey'
value = 'SampleValue'

s3 = boto3.resource('s3')
client = boto3.client('s3')

# Loop through all buckets
buckets = []
response = client.list_buckets()
for bucket in response['Buckets']:
    #print(bucket['Name'])
    buckets.append(bucket['Name'])

# For each bucket, add the tag
for bucket in buckets:
    # print(bucket)    
    bucket_tagging = s3.BucketTagging(bucket)
    tags = []
    # Try to get existing tags
    try:
        tags = bucket_tagging.tag_set
    except ClientError as e:
        print("Caught unexpected error: %s" % e)
    tags.append({'Key': key, 'Value': value})
    # print(tags)
    # Tag bucket with newly appended tag
    set_tag = bucket_tagging.put(Tagging={'TagSet':tags})