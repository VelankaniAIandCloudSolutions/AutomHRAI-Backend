import boto3
from django.conf import settings

def upload_file_to_s3(file_name, bucket_name, object_name=None):
    if object_name is None:
        object_name = file_name

    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             region_name=settings.AWS_S3_REGION_NAME)
    try:
        response = s3_client.upload_file(file_name, bucket_name, object_name)
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        return s3_url
    except Exception as e:
        print("Failed to upload file to S3")
        print(e)
        return None
    
def upload_file_to_s3_2(file_content, file_name, bucket_name):
    try:
        s3_client = boto3.client('s3',
                                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                 region_name=settings.AWS_S3_REGION_NAME)
        
        s3_client.put_object(Body=file_content, Bucket=bucket_name, Key=file_name)
        
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        return s3_url
    except Exception as e:
        print("Failed to upload file to S3")
        print(e)
        return None