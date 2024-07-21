from flask import Flask, request, jsonify
import os
import shutil
import numpy as np
import pickle
import tensorflow
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import GlobalMaxPooling2D
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from sklearn.neighbors import NearestNeighbors
from numpy.linalg import norm
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
WISHLIST_FOLDER = 'wishlist'
IMAGES_FOLDER = 'images'  # Folder where images used for training are stored

# Ensure the uploads and wishlist directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(WISHLIST_FOLDER, exist_ok=True)

# Load feature list and filenames
with open('embeddings.pkl', 'rb') as f:
    feature_list = np.array(pickle.load(f))
with open('filenames.pkl', 'rb') as f:
    filenames = pickle.load(f)

# Load the ResNet50 model
model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
model.trainable = False

# Add a GlobalMaxPooling2D layer
model = tensorflow.keras.Sequential([
    model,
    GlobalMaxPooling2D()
])

# Define hard-coded recommendations based on categories
hard_coded_recommendations = {
    't-shirt': ['sport_shoe1.jpeg', 'sports_watch2.jpeg'],
    'jeans': ['sport_shoe2.jpeg', 'sports_watch2.jpeg'],
    'shirt': ['formal_shoe1.jpg', 'analog_watch1.jpeg'],
    'trouser': ['formal_shoe2.jpeg', 'analog_watch2.jpeg'],
    'shoes': ['sport_shoe2.jpeg', 'formal_shoe1.jpeg'],
    'watch': ['analog_watch1.jpeg', 'sport_watch1.jpeg'],
    # Add more categories and their recommendations here
}

# Function to save uploaded files
def save_uploaded_file(uploaded_file):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(file_path)  # Using save() method for simplicity
        return file_path
    except Exception as e:
        print(f"Error saving file: {e}")  # Logging error
        return None

# Function to extract features from an image
def feature_extraction(img_path, model):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    result = model.predict(preprocessed_img).flatten()
    normalized_result = result / norm(result)
    return normalized_result

# Function to recommend similar items
def recommend(features, feature_list):
    neighbors = NearestNeighbors(n_neighbors=6, algorithm='brute', metric='euclidean')
    neighbors.fit(feature_list)
    distances, indices = neighbors.kneighbors([features])
    return indices

# Function to get category from filename
def get_category(file_name):
    if 'tshirt' in file_name.lower():
        return 't-shirt'
    elif 'jeans' in file_name.lower():
        return 'jeans'
    elif 'shirt' in file_name.lower():
        return 'shirt'
    elif 'formalpant' in file_name.lower() or 'trouser' in file_name.lower():
        return 'trouser'
    elif 'shoes' in file_name.lower():
        return 'shoes'
    elif 'watch' in file_name.lower():
        return 'watch'
    # Add more conditions for other categories
    return None

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file:
        file_path = save_uploaded_file(file)
        if file_path:
            features = feature_extraction(file_path, model)
            indices = recommend(features, feature_list)
            category = get_category(file.filename)
            print(f"Detected category: {category}")
            print(f"Indices: {indices}")
            recommendations = [filenames[i] for i in indices[0][1:]]
            print(f"Recommendations: {recommendations}")
            
            # Prepare response data
            response_data = {
                "recommendations": recommendations,
                "category": category
            }
            
            # Add hard-coded suggestions if category exists in recommendations
            if category in hard_coded_recommendations:
                suggested_images = hard_coded_recommendations[category]
                response_data["suggested_images"] = suggested_images
            
            return jsonify(response_data)
        else:
            return jsonify({"error": "File upload failed"}), 500
    return jsonify({"error": "No file part"}), 400

@app.route('/wishlist', methods=['POST'])
def add_to_wishlist():
    data = request.get_json()
    image_url = data.get('image')
    if image_url:
        # Assuming image_url is a path from IMAGES_FOLDER
        filename = os.path.basename(image_url)
        src_path = os.path.join(IMAGES_FOLDER, filename)
        dest_path = os.path.join(WISHLIST_FOLDER, filename)
        if os.path.exists(src_path):
            try:
                shutil.copy(src_path, dest_path)
                return jsonify({"success": True}), 200
            except Exception as e:
                print(f"Error copying file to wishlist: {e}")  # Logging error
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"error": "File not found in images folder"}), 404
    return jsonify({"error": "Invalid data"}), 400

if __name__ == '__main__':
    app.run(debug=True)
