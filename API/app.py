from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
import firebase_admin
from firebase_admin import credentials, auth as admin_auth

# -------------------------------
# Paths and directories
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder where app.py is
FRONTEND_DIR = os.path.join(BASE_DIR, '../FRONTEND')
STATIC_DIR = FRONTEND_DIR
DATA_FILE = os.path.join(BASE_DIR, '../LDB/movies.json')
POSTERS_DIR = os.path.join(BASE_DIR, '../LDB/POSTERS')
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, 'serviceAccountKey.json')

# -------------------------------
# Initialize Flask app
# -------------------------------
app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=STATIC_DIR)

# -------------------------------
# Initialize Firebase Admin SDK
# -------------------------------
cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)

# -------------------------------
# Helper functions
# -------------------------------
def read_movies():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# -------------------------------
# Routes
# -------------------------------

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
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=2)
    return jsonify(new_movie), 201

# Serve poster images
@app.route('/POSTERS/<filename>')
def get_poster(filename):
    return send_from_directory(POSTERS_DIR, filename)

# Serve icons / tab icons
@app.route('/icon/<filename>')
def get_icon(filename):
    return send_from_directory(POSTERS_DIR, filename)

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

# -------------------------------
# Run the app (prod-ready)
# -------------------------------
if __name__ == '__main__':
    # For Render, host=0.0.0.0 and port=os.environ.get('PORT')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
