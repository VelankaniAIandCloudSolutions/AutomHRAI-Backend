import face_recognition as fr
import numpy as np


from accounts.models import UserAccount


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_encoded_faces():
    """
    This function loads all user account images and encodes their faces
    """
    # Retrieve all user accounts from the database
    user_accounts = UserAccount.objects.all()

    # Create a dictionary to hold the encoded face for each user account
    encoded = {}

    for user_account in user_accounts:
        # Initialize the encoding variable with None
        encoding = None

        # Load the user account image
        if user_account.user_image:
            face = fr.load_image_file(user_account.user_image.path)

            # Encode the face (if detected)
            face_encodings = fr.face_encodings(face)
            if len(face_encodings) > 0:
                encoding = face_encodings[0]
            else:
                print("No face found in the image")
                
            # Add the user account's encoded face to the dictionary if encoding is not None
            if encoding is not None:
                encoded[user_account.email] = encoding

    # Return the dictionary of encoded faces
    return encoded


def classify_face(img, threshold=0.4):
        """
        This function takes an image as input and returns the email of the user account it contains
        """
        # Load all the known faces and their encodings
        faces = get_encoded_faces()
        faces_encoded = list(faces.values())
        known_face_emails = list(faces.keys())

        # Load the input image
        img = fr.load_image_file(img)

        try:
            # Find the locations of all faces in the input image
            face_locations = fr.face_locations(img)

            # Encode the faces in the input image
            unknown_face_encodings = fr.face_encodings(img, face_locations)

            # Identify the faces in the input image
            face_emails = []
            for face_encoding in unknown_face_encodings:
                # Compare the encoding of the current face to the encodings of all known faces
                face_distances = fr.face_distance(faces_encoded, face_encoding)
                # Find the closest known face
                min_distance = min(face_distances)
                best_match_index = np.argmin(face_distances)

                # If the distance is below the threshold, consider it a match
                if min_distance < threshold:
                    email = known_face_emails[best_match_index]
                else:
                    email = "Unknown"

                face_emails.append(email)

            # Return the emails of all faces in the input image
            return face_emails[0]   
        except Exception as e:
            # If no faces are found in the input image or an error occurs, return an empty list
            print(f"Error: {e}")
            return False



# def classify_face(img):
#     """
#     This function takes an image as input and returns the email of the user account it contains
#     """
#     # Load all the known faces and their encodings
#     faces = get_encoded_faces()
#     faces_encoded = list(faces.values())
#     known_face_emails = list(faces.keys())

#     # Load the input image
#     img = fr.load_image_file(img)

#     try:
#         # Find the locations of all faces in the input image
#         face_locations = fr.face_locations(img)

#         # Encode the faces in the input image
#         unknown_face_encodings = fr.face_encodings(img, face_locations)

#         # Identify the faces in the input image
#         face_emails = []
#         for face_encoding in unknown_face_encodings:
#             # Compare the encoding of the current face to the encodings of all known faces
#             matches = fr.compare_faces(faces_encoded, face_encoding)

#             # Find the known face with the closest encoding to the current face
#             face_distances = fr.face_distance(faces_encoded, face_encoding)
#             best_match_index = np.argmin(face_distances)

#             # If the closest known face is a match for the current face, label the face with the known email
#             if matches[best_match_index]:
#                 email = known_face_emails[best_match_index]
#             else:
#                 email = "Unknown"

#             face_emails.append(email)
#             print(face_emails)
#         # Return the email of the first face in the input image
#         return face_emails[0]
#     except:
#         # If no faces are found in the input image or an error occurs, return False
#         return False








# views.py code 

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def upload_photo(request):
#     if request.method == 'POST':
#         photo_data = request.POST.get('photo')
#         if photo_data:
#             # Splitting the data to separate the base64 header from the actual encoded image data
#             _, str_img = photo_data.split(';base64,')
#             decoded_contentfile = base64.b64decode(str_img)

#             filename = 'upload.png'  
#             path = os.path.join('media', filename)  
#             with open(path, 'wb') as f:
#                 f.write(decoded_contentfile)

#             print(path)

#             # Classify the face detected in the uploaded image
#             detected_user = classify_face(path)
#             if detected_user:
#                 # Check if the detected user exists
#                 user_exists = UserAccount.objects.filter(email=detected_user).exists()
#                 if user_exists:
#                     user = UserAccount.objects.get(email=detected_user)
                  
#                     return JsonResponse({'message': f'Photo received and processed successfully. Detected user: {detected_user}'})
#             return JsonResponse({'error': 'Detected user not found or does not exist'}, status=400)
#         return JsonResponse({'error': 'No photo found in the request'}, status=400)