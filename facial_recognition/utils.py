# using deep learning and more accuracy but slower, works best with gpu
################################################
# from facenet_pytorch import MTCNN, InceptionResnetV1
# from PIL import Image
# from numpy.linalg import norm
# import numpy as np

# # Initialize models
# mtcnn = MTCNN(image_size=160)
# resnet = InceptionResnetV1(pretrained='vggface2').eval()

# def get_encoded_faces():
#     from .models import UserAccount  # Import here to avoid circular imports
#     user_accounts = UserAccount.objects.filter(is_contract_worker = True)
#     encoded = {}

#     for user_account in user_accounts:
#         encoding = None
#         if user_account.user_image:
#             try:
#                 img = Image.open(user_account.user_image.path)
#                 img_cropped = mtcnn(img)
                
#                 if img_cropped is not None:
#                     encoding = resnet(img_cropped.unsqueeze(0))
#                     encoding = encoding.detach().numpy()

#                 if encoding is not None:
#                     encoded[user_account.email] = encoding
#             except Exception as e:
#                 print(f"Failed to process image for {user_account.email}: {e}")
    
#     return encoded

# def classify_face(img_path, threshold=0.4):
#     print('classify face called')
#     img = Image.open(img_path)
#     img_cropped = mtcnn(img)
#     if img_cropped is None:
#         return "No face detected"

#     encoding = resnet(img_cropped.unsqueeze(0))
#     encoding = encoding.detach().numpy()

#     known_faces = get_encoded_faces()

#     if not known_faces:
#         print("No known faces available for comparison.")
#         return "No known faces to compare with"

#     known_encodings = np.array(list(known_faces.values()))
#     known_emails = list(known_faces.keys())

#     # Reshape known_encodings to ensure it's 2D
#     known_encodings = np.squeeze(known_encodings)

#     print("Encoding shape:", encoding.shape)
#     print("Known encodings shape:", known_encodings.shape)

#     distances = norm(known_encodings - encoding, axis=1)
#     min_distance = np.min(distances)
#     best_match_index = np.argmin(distances)

#     print("Best match index:", best_match_index)
#     print("Known emails:", known_emails)
#     print("Distance:", min_distance)

#     if best_match_index >= len(known_emails):
#         print("Index out of range error.")
#         return "Index out of range"

#     if min_distance < threshold:
#         return known_emails[best_match_index]
#     else:
#         return "Unknown"


#using simple face recognition library less acurate but faster 
################################################


import face_recognition
from PIL import Image
import numpy as np
from django.conf import settings

def get_encoded_faces():
    import requests
    from accounts.models import UserAccount
    from io import BytesIO
    encoded = {}

    for user_account in UserAccount.objects.all():
        encoding = None
        if user_account.user_image:
            s3_url = user_account.user_image
            s3_base_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/" # Replace this with your S3 bucket base URL
            s3_url = s3_base_url + str(user_account.user_image)
            print(s3_url)
            response = requests.get(s3_url)
            if response.status_code == 200:
                # Read the image data from the response
                image_data = BytesIO(response.content)
                
                # Load the image from the image data
                img = face_recognition.load_image_file(image_data)
                print(img)
                # Resize the image to reduce processing time
                small_img = np.array(Image.fromarray(img).resize((int(0.5 * img.shape[1]), int(0.5 * img.shape[0]))))

                # Optionally use CNN model for more accurate face detection (slower)
                face_locations = face_recognition.face_locations(small_img, model='hog')  # Change to 'cnn' for more accuracy, hog for faster
                face_encodings = face_recognition.face_encodings(small_img, face_locations, num_jitters=1)  # Reduced jitters

                if face_encodings:
                    encoding = face_encodings[0]

                if encoding is not None:
                    encoded[user_account.email] = encoding
                else:
                    print("No face found in the image")
            else:
                print(f"Failed to download image from {s3_url}")

    return encoded


def classify_face(img_path, threshold=0.4):
    img = face_recognition.load_image_file(img_path)

    # Convert floating point calculations to integer for dimensions
    width, height = img.shape[1], img.shape[0]
    new_width = int(width * 0.5)
    new_height = int(height * 0.5)

    # Resize the image using integer dimensions
    small_img = np.array(Image.fromarray(img).resize((new_width, new_height)))

    # Proceed with face detection
    face_locations = face_recognition.face_locations(small_img, model='hog')  # Change to 'cnn' for more accuracy, hog for faster
    unknown_face_encodings = face_recognition.face_encodings(small_img, face_locations)

    known_faces = get_encoded_faces()
    faces_encoded = list(known_faces.values())
    known_face_emails = list(known_faces.keys())
 
    for face_encoding in unknown_face_encodings:
        face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
        min_distance = min(face_distances)
        best_match_index = np.argmin(face_distances)

        if min_distance < threshold:
            return known_face_emails[best_match_index]
        else:
            return "Unknown"

    return "Unknown"