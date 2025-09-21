from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
import firebase_admin
from firebase_admin import credentials, auth as admin_auth
# Initialize Flask app
app = Flask(__name__, template_folder='../FRONTEND', static_folder='../FRONTEND')
DATA_FILE = '../LDB/movies.json'

# Initialize Firebase Admin SDK
cred = credentials.Certificate('serviceAccountKey.json')  # Ensure this file is in your API folder
firebase_admin.initialize_app(cred)

# Helper function to read movies
def read_movies():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Home page showing all movies
@app.route('/')
def index():
    movies = read_movies()
    categories = sorted(set(movie['PROP'].get('CATEGORY', 'Unknown') for movie in movies))
    return render_template('index.html', movies=movies, categories=categories)

# Movie detail page
@app.route('/movie/<name>')
def movie_detail(name):
    movies = read_movies()
    movie = next((m for m in movies if m['Movie'] == name), None)
    if movie:
        return render_template('detail.html', movie=movie)
    return "Movie not found", 404

# API: Get all movies
@app.route('/movies', methods=['GET'])
def get_movies():
    return jsonify(read_movies())

# API: Add a new movie
@app.route('/movies', methods=['POST'])
def add_movie():
    movies = read_movies()
    new_movie = request.json
    movies.append(new_movie)
    with open(DATA_FILE, 'w') as f:
        json.dump(movies, f, indent=2)
    return jsonify(new_movie), 201

# Serve poster images
@app.route('/POSTERS/<filename>')
def get_poster(filename):
    return send_from_directory('../LDB/POSTERS', filename)

# Google Sign-In verification
@app.route('/google-login', methods=['POST'])
def google_login():
    id_token = request.json.get('idToken')
    try:
        decoded_token = admin_auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token.get('email')
        name = decoded_token.get('name')
        return jsonify({
            "msg": "Google sign-in successful",
            "uid": uid,
            "email": email,
            "name": name
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
