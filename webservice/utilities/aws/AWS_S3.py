import boto3
from botocore.exceptions import ClientError


# client
class S3:
    def __init__(self):
        self.client = boto3.client('s3')

    def print_buckets(self):
        try:
            client_response = self.client.list_buckets()
            print("Buckets: ")
            for bucket in client_response['Buckets']:
                print(f'Bucket Name: {bucket["Name"]}')
        except ClientError as e:
            print(e)

    def upload_file(self, file_name, bucket, object_name=None):
        """ Upload a file to an S3 bucket

            :param file_name: File to upload
            :param bucket: Bucket to upload to
            :param object_name: S3 object name. If not specified then file_name is used
            :return: True if file was uploaded, else False
        """
        # If s3 object_name not specified use the file_name
        if object_name is None:
            object_name = file_name
            response = self.client.upload_file(file_name, bucket, object_name)

    def download_file(self, bucket_name, object_name, file_name):
        """ Download an s3 object to a filename

            :param bucket_name: bucket to download from
            :param object_name: object to download
            :param file_name: file path to download to

            :returns true if successful else false
        """
        try:
            self.client.download_file(bucket_name, object_name, file_name)
        except ClientError as e:
            print(e)
            return False
        return True

def downfileFromS3 (objectKey, bucket, filepath):
    s3 = boto3.client('s3', aws_access_key_id='AKIAIMJMQN32WII6YCMA', aws_secret_access_key='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', region_name='us-east-2')
    
    s3.download_file(bucket, objectKey, filepath)
