from flask import Flask, request, jsonify
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'fr_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create_user_folder(name, email, user_id):
    folder_name = f"{name}-{email}-{user_id}"
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

@app.route('/api/v1/create-contract-worker', methods=['POST'])
def create_contract_worker():
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    email = request.form.get('email')
    images = request.files.getlist('images')

    if not all([user_id, name, email, images]):
        return jsonify({'error': 'Missing required parameters'}), 400

    user_folder = create_user_folder(name, email, user_id)

    for image in images:
        if image.filename != '':
            image_path = os.path.join(user_folder, image.filename)
            image.save(image_path)

    return jsonify({'message': 'Images uploaded successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
