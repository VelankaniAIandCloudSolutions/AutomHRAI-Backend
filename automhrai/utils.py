import boto3
from django.conf import settings

def upload_file_to_s3(file_name, bucket_name, object_name=None):
    if object_name is None:
        object_name = file_name

    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             region_name=settings.AWS_S3_REGION_NAME)
    print('AutomHRAI-Backend/' + file_name, bucket_name, object_name)
    # try:
    response = s3_client.upload_file(file_name, bucket_name, object_name)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        # Construct the URL of the stored image
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        print(f"File uploaded to S3: {s3_url}")
        return s3_url
    else:
        print("Failed to upload file to S3")
        return None
    # except Exception as e:
    #     print(e)
    #     return None

# # Usage example:
# file_name = 'local_file.txt'  # Path to the file you want to upload
# bucket_name = 'your_bucket_name'  # Name of your S3 bucket
# object_name = 'file.txt'  # Optional: Name you want to give to the file in S3

# upload_success = upload_file_to_s3(file_name, bucket_name, object_name)
# if upload_success:
#     print("File uploaded successfully!")
# else:
#     print("Failed to upload file.")
