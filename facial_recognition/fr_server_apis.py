from flask import Flask, request, jsonify
import os
import boto3
from dotenv import load_dotenv
from urllib.parse import urlparse
# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), '..', '.env')

load_dotenv(dotenv_path)


app = Flask(__name__)

UPLOAD_FOLDER = 'fr_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def create_user_folder(name, email, user_id):
    folder_name = f"{name}-{email}-{user_id}"
    # folder_name = f"{name}-{email}"
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


# Retrieve AWS credentials from environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')


if not aws_access_key_id or not aws_secret_access_key:
    raise ValueError("AWS credentials are not set in environment variables.")

# Create a Boto3 S3 client
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key)


# @app.route('/api/v1/create-contract-worker', methods=['POST'])
# def create_contract_worker():
#     user_id = request.form.get('user_id')
#     print('user_id', user_id)
#     name = request.form.get('name')
#     print('name', name)
#     email = request.form.get('email')
#     print('email', email)
#     images = request.files.getlist('images')
#     print('images', images)

#     for image in images:
#         print(f'Image filename: {image.filename}')
#         print(f'Image content type: {image.content_type}')
#         print(f'Image size: {image.content_length}')

#     if not all([user_id, name, email, images]):
#         return jsonify({'error': 'Missing required parameters'}), 400

#     user_folder = create_user_folder(name, email, user_id)

#     for image in images:
#         if image.filename != '':
#             image_path = os.path.join(user_folder, image.filename)
#             image.save(image_path)

#     return jsonify({'message': 'Images uploaded successfully'}), 200

@app.route('/api/v1/create-contract-worker', methods=['POST'])
def create_contract_worker():
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    email = request.form.get('email')
    image_urls_s3_string = request.form.get('image_urls_s3', '')
    # Split the string into a list of URLs
    image_urls_s3 = image_urls_s3_string.split(
        ',') if image_urls_s3_string else []

    # Create user folder
    user_folder = create_user_folder(name, email, user_id)

    # Download images from S3 and save them
    # Download images from S3 and save them
    for image_url in image_urls_s3:
        # Parse the S3 URL
        parsed_url = urlparse(image_url)
        # Extract the S3 object key from the URL
        image_key = parsed_url.path.lstrip('/')
        image_filename = os.path.basename(image_key)
        image_path = os.path.join(user_folder, image_filename)
        # Download image from S3
        s3.download_file(aws_bucket_name,
                         image_key, image_path)

    # Other logic

    return jsonify({'success': 'Images downloaded and saved successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
