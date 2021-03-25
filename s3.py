import boto3
from botocore.exceptions import ClientError
import os

s3 = boto3.resource(
    's3',
    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
)

def delete(bucket, file):
    obj = s3.Object(bucket, file)
    obj.delete()

def upload(file, bucket, file_name = None):
    print(file)
    print(bucket)
    print(file_name)
    try:
        data = open(file, 'rb')
        s3.Bucket(bucket).put_object(
            Key = file_name or file, 
            Body = data
        )
        return True
    except botocore.exceptions.ClientError as e:
        print("error: ", e)
        return False

def download(bucket_name, object_name, file_name = None):
    try:
        s3.Bucket(bucket_name).download_file(object_name, file_name or object_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
